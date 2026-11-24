# API Response Contract

All JSON keys are **snake_case** (the frontend consumes snake_case — do not camelCase).
All timestamps are **ISO-8601 UTC**.

## Success envelope

```python
# src/schemas/shared/responses.py
from typing import Any
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    message: str
    data: Any | None = None
```

Return it for actions without a resource body (logout, delete, trigger):
`return SuccessResponse(message="Logged out successfully")`. For resource reads, return the
resource's own response schema directly (with `response_model=` on the route).

## Pagination envelope — CANONICAL

**Exactly this shape** for every list endpoint:

```json
{ "data": [ ... ], "current_page": 1, "page_limit": 50, "total_count": 137 }
```

```python
from typing import Generic, TypeVar
from pydantic import BaseModel, Field
T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    current_page: int = Field(ge=1, default=1)
    page_limit: int = Field(ge=1, le=100, default=50)
    total_count: int = Field(ge=0, default=0)

    @property
    def total_pages(self) -> int:
        return 0 if self.total_count == 0 else (self.total_count + self.page_limit - 1) // self.page_limit
    @property
    def has_next(self) -> bool:
        return self.current_page < self.total_pages

class PaginationParams(BaseModel):
    page: int = Field(ge=1, default=1)
    limit: int = Field(ge=1, le=100, default=50)
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

def create_paginated_response(data, page, limit, total_count):
    return PaginatedResponse(data=data, current_page=page, page_limit=limit, total_count=total_count)
```

Controller usage:

```python
total = await OrderModel.filter(**filters).count()
rows = await OrderModel.filter(**filters).order_by("-created_at").offset(params.offset).limit(params.limit)
return create_paginated_response([OrderOut.model_validate(r) for r in rows],
                                 params.page, params.limit, total)
```

❌ **Not** `{items, total, page, page_size, has_next}` and **not** `{data, total, limit, page}`.

## Errors — raise `HTTPException` (CANONICAL)

Errors are raised as a FastAPI **`HTTPException`** with `status_code`, a human-readable
**`detail`**, and **optional `headers`**. The response body is FastAPI's default — **no
custom envelope, no global handlers**:

```json
{ "detail": "Order not found" }
```

```python
from fastapi import HTTPException, status
from src.schemas.shared.base import ErrorCodes

# simple
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

# with a machine-readable code the frontend can branch on → X-Error-Code header
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="OTP has expired",
    headers={"X-Error-Code": ErrorCodes.OTP_EXPIRED},
)

# auth challenges carry WWW-Authenticate
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### Rules

1. `detail` is a **string** — concise, client-safe (no stack traces, no secrets, no internal
   IDs).
2. When the client must branch on the error programmatically, attach a **stable machine code
   via the `X-Error-Code` header**, drawn from `ErrorCodes`. Keep `detail` human-readable.
3. Use `headers={"WWW-Authenticate": "Bearer"}` on `401`s.
4. **Do NOT** register global exception handlers, **do NOT** wrap errors in a custom
   `{error:{...}}` envelope, and **do NOT** put machine codes inside `detail`. FastAPI's
   default handling of `HTTPException` is the contract.
5. Unhandled (non-`HTTPException`) errors are caught by the controller try/except ladder and
   re-raised as `HTTPException(500, detail="<safe message>")` after `logger.error(...)` — see
   [controllers-services.md](controllers-services.md). Sentry's ASGI integration captures any
   that escape.

❌ **Not** the `{error:{code,message,details}}` global-handler envelope (a common alternative —
rejected). ❌ **Not** a structured dict in `detail`.

### `ErrorCodes` catalog — `src/schemas/shared/base.py`

A flat catalog of stable string codes, used as **`X-Error-Code` header values** (not a
response envelope). Extend per project.

```python
class ErrorCodes:
    # Auth
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    ACCOUNT_BLOCKED = "ACCOUNT_BLOCKED"
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_INVALID = "OTP_INVALID"
    # Resource
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    # Server
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    # extend per project (billing, team, share, ...)
```

## Status codes

| Code | Use |
|------|-----|
| 200 | OK (reads, updates, actions) |
| 201 | Created |
| 400 | Bad request / domain `ValueError` |
| 401 | Missing/invalid/expired/revoked token |
| 403 | Authenticated but wrong persona / lacks permission |
| 404 | Resource not found |
| 409 | Conflict / already exists |
| 422 | Request validation failure (FastAPI/pydantic) |
| 429 | Rate limited (SlowAPI) |
| 500 | Unhandled — logged, generic message to client |
| 503 | Dependency down (health check degraded) |

## Validation

- Request/response validation is pydantic v2 at the route boundary. Validation failures
  return **FastAPI's default 422** shape (`{"detail": [{"loc", "msg", "type"}, ...]}`) — no
  custom formatter, consistent with the plain-`HTTPException` error convention above.
- Schema location and naming taxonomy: see [code-style.md](code-style.md).
- Base schema config for ORM interop:

```python
from pydantic import BaseModel, ConfigDict
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)
```

## Health check (in `main.py`)

Returns `{status, version, checks:{database, redis}}`; 200 when all `ok`, else 503. Used as
the first-run smoke test by `backend-scaffold`.
