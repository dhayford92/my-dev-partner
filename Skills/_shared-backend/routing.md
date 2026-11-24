# Routing

## URL shape

```
/{domain}          /api/v1        /{persona}/{feature}
   mount        include-prefix        router-prefix
```

- **domain** — `users` | `core` | `utils` (the mounted sub-app, `main.py`).
- **/api/v1** — version, applied in `views/<domain>.py` at `include_router(..., prefix=API_V1)`.
- **persona/feature** — the router's own `prefix`, persona-first.

**Examples:**

| Endpoint | mount | include | router prefix | route |
|----------|-------|---------|---------------|-------|
| `POST /users/api/v1/client/auth/login` | `/users` | `/api/v1` | `/client/auth` | `/login` |
| `GET /users/api/v1/admin/users` | `/users` | `/api/v1` | `/admin/users` | `""` |
| `GET /core/api/v1/client/orders` | `/core` | `/api/v1` | `/client/orders` | `""` |

> **Versioning is mandatory** on all new projects. Never omit `/api/v1` (some older services historically
> did; that is corrected here).

## Persona in the prefix

Persona (`client` / `vendor` / `admin` / `portal`) is encoded in the **router prefix**, not
in a nested folder tree. One router file per persona+feature: `client_auth_router.py`,
`admin_auth_router.py`, `vendor_auth_router.py`.

## Router = thin. Delegate to a controller.

Real example (`src/apps/users/routers/client_auth_router.py`):

```python
from fastapi import APIRouter, BackgroundTasks, Request

from configs.rate_limiting import limiter, RateLimitConfig
from src.libs.auth import CurrentClientUser
from src.schemas.shared.token import RefreshRequest, TokenResponse
from src.schemas.users.client_schemas import ClientAuthResponse
from src.apps.users.controllers.client_auth_controller import ClientAuthController

router = APIRouter(prefix="/client/auth", tags=["Client Auth"])


@router.post("/login", response_model=ClientAuthResponse)
@limiter.limit(RateLimitConfig.LOGIN)
async def login(request: Request, body: LoginSchema, background_tasks: BackgroundTasks):
    """Authenticate a client and return tokens."""
    return await ClientAuthController.login(body, background_tasks)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(RateLimitConfig.REFRESH_TOKEN)
async def refresh_token(request: Request, body: RefreshRequest):
    """Refresh an access token."""
    return await ClientAuthController.refresh_token(body)


@router.post("/logout")
async def logout(auth: CurrentClientUser):
    """Invalidate the current token."""
    return await ClientAuthController.logout(auth.jti, auth.user_id)
```

Rules the example encodes:

1. `APIRouter(prefix=..., tags=[...])`. Tags are human-readable ("Client Auth").
2. Every handler sets `response_model=`.
3. Handlers are one-liners: `return await <Controller>.<method>(...)`. No logic.
4. **Rate-limited routes must accept `request: Request`** — SlowAPI's decorator requires it.
   Use the constants in `RateLimitConfig`, not raw strings.
5. Auth via the type-alias dependency (`CurrentClientUser`, etc. — see [auth.md](auth.md)).
6. `BackgroundTasks` is passed straight through to the controller.
7. Multiple related routers may live in one file (e.g. `router` + `profile_router`), each
   with its own prefix.

## Rate limiting

`configs/rate_limiting.py` exposes a `limiter` (SlowAPI, Redis-backed) and a
`RateLimitConfig` constants class:

```python
class RateLimitConfig:
    LOGIN = "10/minute"
    REGISTER = "5/minute"
    OTP_VERIFICATION = "5/minute"
    REFRESH_TOKEN = "30/minute"
    LIST_RESOURCES = "100/minute"
    CREATE_RESOURCE = "30/minute"
```

Decorate sensitive endpoints (auth, OTP, register, password reset) with
`@limiter.limit(RateLimitConfig.X)`. The limiter is attached via `app.state.limiter` in the
lifespan; the `RateLimitExceeded` handler is registered in `main.py`.

## Pagination / filtering / sorting

- List endpoints accept `page` (default 1) and `limit` (default 50, max 100) query params
  and return the pagination envelope — see [response-contract.md](response-contract.md).
- Filtering: explicit query params mapped to Tortoise `.filter(...)`.
- Sorting: `sort` / `order` params mapped to Tortoise `.order_by(...)`; default `-created_at`.

## Idempotency

Not implemented in the repos. For new payment/write endpoints where it matters, accept an
`Idempotency-Key` header and dedupe via Redis (`SETNX` + TTL) before executing. Flag this
explicitly when designing such an endpoint rather than assuming it.
