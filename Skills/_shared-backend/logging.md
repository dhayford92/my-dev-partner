# Logging (two systems) + PII redaction + Request IDs

There are **two separate logging systems**. Keep them separate.

## (a) Developer / error logging

**stdlib `logging`.** Configured once in `main.py`:

```python
import logging
from configs.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
```

Every module that logs does:

```python
import logging
logger = logging.getLogger(__name__)
```

### Rules

1. **`print()` is banned** for diagnostics. Always `logger.debug/info/warning/error`.
   (a bare `print("[ERROR] ...")` habit is explicitly rejected.)
2. In `except Exception` blocks: `logger.error(f"<context>: {e}")` (use `logger.exception(...)`
   when you need the full stack trace in the dev log / Sentry).
3. Levels: `debug` for traces, `info` for lifecycle/successful side effects, `warning` for
   recoverable/expected-bad input, `error` for unexpected failures.
4. **Sentry** is initialized **only when `SENTRY_DSN` is set** — guard it:

   ```python
   if settings.SENTRY_DSN:
       import sentry_sdk
       sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1,
                       environment="production" if not settings.DEBUG else "development")
   ```

## (b) Admin activity logging (audit trail)

A **database audit trail** of user-facing mutations, via `ActivityService` →
`ActivityLog`. This is a product feature (admins read it), not diagnostics.

### Model — `src/apps/utils/models/activity_model.py`

```python
from tortoise.models import Model
from tortoise import fields
from src.apps.users.models.user_enum import ActivityAction   # StrEnum: create/update/delete/share/revoke

class ActivityLog(Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(index=True)
    user_type = fields.CharField(max_length=20, default="admin")   # client|vendor|admin
    action = fields.CharEnumField(ActivityAction, max_length=50)
    resource_type = fields.CharField(max_length=100)
    resource_id = fields.UUIDField(null=True)
    resource_name = fields.CharField(max_length=255, null=True)
    metadata = fields.JSONField(default=dict)
    ip_address = fields.CharField(max_length=50, null=True)
    user_agent = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = "activity_logs"
        ordering = ["-created_at"]
```

### Service — `src/services/activity/activity_service.py`

`ActivityService.log(...)` plus convenience `log_create / log_update / log_delete /
log_share / log_revoke`. It extracts IP (`x-forwarded-for` first) and user-agent from the
request. Call the specific helper from the controller as part of the mutation:

```python
await ActivityService.log_create(
    user_id=auth.user_id, resource_type="order", resource_id=order.id,
    resource_name=order.reference, metadata=redact(payload), request=request,
)
```

- **Log every create/update/delete/share/revoke**, in the same controller method that made
  the change — never as a separate pass.
- Multi-tenant projects add a scope column (`team_id` / `organization_id`) and a matching
  **portal** variant (`PortalActivityLog`, no tenant scope) for admin-console actions.

## PII redaction (REQUIRED — new addition, not in the repos yet)

Neither logging system redacts today. **Add a redaction helper** and run all logged/audited
free-form data through it. Redact: passwords, tokens/JWTs, API keys, full card numbers,
and mask emails/phones.

`src/libs/redaction.py`:

```python
import re

_SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "secret",
                   "api_key", "authorization", "card_number", "cvv", "pin", "otp"}

def _mask_email(v: str) -> str:
    name, _, domain = v.partition("@")
    return f"{name[:2]}***@{domain}" if domain else v

def _mask_phone(v: str) -> str:
    return v[:3] + "****" + v[-2:] if len(v) >= 6 else "****"

def redact(data):
    """Recursively redact PII from a dict/list before logging or storing in metadata."""
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            if k.lower() in _SENSITIVE_KEYS:
                out[k] = "***REDACTED***"
            elif isinstance(v, str) and "@" in v and re.match(r"[^@]+@[^@]+\.[^@]+", v):
                out[k] = _mask_email(v)
            elif k.lower() in {"phone", "phone_number", "msisdn"} and isinstance(v, str):
                out[k] = _mask_phone(v)
            else:
                out[k] = redact(v)
        return out
    if isinstance(data, list):
        return [redact(x) for x in data]
    return data
```

Use it: `logger.info(f"payment payload: {redact(payload)}")` and
`metadata=redact(changes)` when writing `ActivityLog`.

## Request correlation ID (REQUIRED — new addition)

`X-Request-ID` is CORS-exposed everywhere but never generated. **Add middleware** that
generates one per request, stores it on `request.state`, echoes it in the response header,
and includes it in log records.

`src/libs/request_id.py`:

```python
import uuid, contextvars
from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid
        token = request_id_ctx.set(rid)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = rid
        return response
```

Add a logging filter that injects `request_id_ctx.get()` into every record and extend the
format string with `%(request_id)s`. Register `app.add_middleware(RequestIDMiddleware)` in
the factory (before CORS in add order so it runs outermost).
