# Authentication & Authorization

## Auth stack (identical across all four repos — highly stable)

- **JWT**, HS256, via **`python-jose`** (`from jose import jwt, JWTError`). Never PyJWT.
- **Passwords:** `bcrypt`, cost factor **12**.
- **Access token:** 60 min. **Refresh token:** 30 days, **stateless + Redis denylist**.
- **Transport:** `HTTPBearer` → `AuthContext` → persona dependency guards.

## JWT service — `services/auth/jwt_service.py`

Claims: `sub, jti, iat, exp, iss, aud, type, user_type` (+ `additional_claims`).

```python
import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from configs.settings import settings


class JWTService:
    ALGORITHM = "HS256"

    @staticmethod
    def create_access_token(user_id: uuid.UUID, user_type: str | None = None,
                            type: str = "access",
                            additional_claims: dict | None = None) -> tuple[str, str, datetime]:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jti = str(uuid.uuid4())
        payload = {
            "sub": str(user_id), "jti": jti, "iat": now, "exp": expires_at,
            "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE, "type": type,
        }
        if user_type:
            payload["user_type"] = user_type
        if additional_claims:
            payload.update(additional_claims)
        token = jwt.encode(payload, settings.API_SECRET_KEY, algorithm=JWTService.ALGORITHM)
        return token, jti, expires_at            # (token, jti, expires_at) — callers unpack all 3

    @staticmethod
    def create_refresh_token(user_id, session_id=None, user_type=None) -> tuple[str, str, datetime]:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = str(uuid.uuid4())
        payload = {"sub": str(user_id), "jti": jti, "iat": now, "exp": expires_at,
                   "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE, "type": "refresh"}
        if user_type: payload["user_type"] = user_type
        return jwt.encode(payload, settings.API_SECRET_KEY, algorithm=JWTService.ALGORITHM), jti, expires_at

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        payload = jwt.decode(token, settings.API_SECRET_KEY, algorithms=[JWTService.ALGORITHM],
                             audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER)
        if payload.get("type") != token_type:
            raise JWTError(f"Invalid token type. Expected {token_type}")
        return payload
```

Typed tokens beyond access/refresh use the `type` claim (e.g. `type="otp_request"`,
`type="password_reset"`) so a token minted for one purpose can't be replayed for another.

## Password service — `services/auth/password_service.py`

```python
import bcrypt

class PasswordService:
    COST_FACTOR = 12

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            return False

    @staticmethod
    def is_password_strong(password: str) -> tuple[bool, str | None]:
        if len(password) < 8:                     return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password): return False, "Needs an uppercase letter"
        if not any(c.islower() for c in password): return False, "Needs a lowercase letter"
        if not any(c.isdigit() for c in password): return False, "Needs a digit"
        return True, None
```

## Token denylist (revocation) — `services/auth/token_denylist.py`

Redis-backed. Key `token:denied:{jti}` with TTL = token's remaining life; per-user revoke
key `token:denied:user:{user_id}` for "log out everywhere".

```python
token_denylist = TokenDenylistService()   # module-level singleton

await token_denylist.add_to_denylist(jti, expires_at=exp)   # logout one token
await token_denylist.is_denied(jti)                         # checked on every request
await token_denylist.deny_all_for_user(user_id)             # force logout all devices
await token_denylist.un_deny_all_for_user(user_id)          # re-enable (e.g. undelete)
```

**Refresh is stateless:** verify the refresh JWT, check it's not denied, issue a new access
token. No DB session table by default. (Projects that genuinely need server-side session
listing — e.g. an admin portal — may add a `SessionModel`; that's an opt-in, not the default.)

## Guards — `libs/auth.py`

`HTTPBearer(auto_error=False)` → `get_current_user` builds an `AuthContext`, checks the
denylist, then persona guards narrow by `user_type`.

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from src.services.auth import JWTService, token_denylist

security = HTTPBearer(auto_error=False)


class AuthContext:
    def __init__(self, user_id, user_type=None, email=None, jti=None, is_superuser=False):
        self.user_id, self.user_type, self.email = user_id, user_type, email
        self.jti, self.is_superuser = jti, is_superuser
    @property
    def id(self): return self.user_id          # so controllers can use auth.id


async def get_current_user(request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> AuthContext:
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing authorization header",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = JWTService.verify_token(credentials.credentials, token_type="access")
        user_id = UUID(payload["sub"]); jti = payload.get("jti")
        if jti and await token_denylist.is_denied(jti):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")
        if await token_denylist.is_user_denied(user_id):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session invalidated")
        return AuthContext(user_id, str(payload.get("user_type")), str(payload.get("email")), jti)
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})


async def get_current_client_user(auth: Annotated[AuthContext, Depends(get_current_user)]):
    if auth.user_type != "client":
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Invalid user type. Expected 'client'.")
    return auth
# ...get_current_admin_user, get_current_vendor_user, get_current_super_admin_user analogously

# Type aliases — this is what routers import:
CurrentUser        = Annotated[AuthContext, Depends(get_current_user)]
CurrentClientUser  = Annotated[AuthContext, Depends(get_current_client_user)]
CurrentAdminUser   = Annotated[AuthContext, Depends(get_current_admin_user)]
CurrentVendorUser  = Annotated[AuthContext, Depends(get_current_vendor_user)]
CurrentSuperAdminUser = Annotated[AuthContext, Depends(get_current_super_admin_user)]
```

Routers then just annotate: `async def me(auth: CurrentClientUser): ...`. A mismatched
`user_type` yields **403**.

## Authorization — pick the model that fits the project

The **default** for a new project is **persona guards** (above): `user_type ∈
{client, vendor, admin, ...}` enforced by the dependency. The two richer models are
**opt-in modules** the `backend-auth` skill can add when the product needs them:

### (a) Persona guards — DEFAULT
`user_type` in the JWT + `Current<Persona>User` deps. Super-admin re-checks the admin
model's `role` enum. No permission table. Use for B2C / simple admin apps.

### (b) JSON RBAC (org-scoped) — opt-in
For B2B where roles are configurable per organization. A `UserRoleModel` stores
`frameworks: JSONField(list)` + `permissions: JSONField` shaped
`{framework: {read: bool, write: bool, delete: bool}}`, M2M to users, `unique_together`
`(organization, name)`. Checks happen **in the controller**:

```python
perm = await UserPermissionChecks.has_client_user_permission(email, "compliance", "write")
if not perm:
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permission")
org_id = perm["organization_id"]          # then scope every query by org_id
rows = await TaskModel.filter(organization_id=org_id, ...)
```

Ship a seeder with default roles (`default_role_list`: Super Admin, Manager, Officer,
Auditor, General User, ...).

### (c) Team + Postgres RLS (multi-tenant) — opt-in
For multi-tenant SaaS. JWT carries `team_id`; every platform query filters by it;
Postgres RLS policies enforce isolation via `set_rls_context(user_id, team_id)` +
`RLSMiddleware`. A separate **portal** JWT (`portal: true` claim + `role`) governs the admin
console with its own `PortalUser/PortalAdmin` guards, and portal routes carry **no** team
scope.

> Choosing between (a)/(b)/(c) is a structural decision — surface it and confirm with the
> owner before scaffolding auth, per `dev-partner`.
