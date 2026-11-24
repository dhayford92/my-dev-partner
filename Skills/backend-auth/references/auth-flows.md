# Auth flows

Base JWT/bcrypt/denylist/guard code: [../../_shared-backend/auth.md](../../_shared-backend/auth.md). This covers the
end-to-end flows and how to wire the drop-in verification/reset module.

## Register (email + password)
1. Validate password strength (`PasswordService.is_password_strong`).
2. Reject duplicate email (409, `X-Error-Code: EMAIL_IN_USE`).
3. Create user with `password_hashed = PasswordService.hash_password(...)`.
4. Issue access + refresh tokens. Optionally send a verification email (below).

## Login
1. Fetch by email; `PasswordService.verify_password` (constant-time; returns False on any
   error — no leak of which factor failed).
2. Reject inactive/deleted (403, `ACCOUNT_BLOCKED`).
3. Update `last_login_at`; issue tokens.

## Refresh (stateless)
1. `verify_token(refresh_token, token_type="refresh")`.
2. Reject if the `jti` is denied.
3. Reject inactive/deleted user.
4. Issue a **new access token** (refresh stays the same unless rotating).

## Logout
`token_denylist.add_to_denylist(jti)` for the current token. For "log out everywhere",
`token_denylist.deny_all_for_user(user_id)`.

## Email verification (drop-in `AccountFlowController`)
- `POST /verify-email/request` → mints a `type="email_verification"` token, emails a
  `FRONTEND_BASE_URL/verify-email?token=...` link via BackgroundTasks. **Same response
  whether or not the email exists** (no enumeration).
- `POST /verify-email` → verifies the typed token, sets `is_verified = True`.

## Password reset (drop-in `AccountFlowController`)
- `POST /forgot-password` → mints a `type="password_reset"` token, emails a reset link. Same
  no-enumeration response.
- `POST /reset-password` → validates strength, verifies the typed token, sets new hash, and
  **denies all the user's tokens** (forces re-login everywhere).

### Wiring the routes
Add to `client_auth_router.py` (rate-limit the request-side endpoints):
```python
from fastapi import BackgroundTasks
from src.apps.users.controllers.verification_reset_controller import AccountFlowController
from src.schemas.users.verification_reset_schemas import (
    RequestVerificationSchema, VerifyEmailSchema, ForgotPasswordSchema, ResetPasswordSchema)

@router.post("/forgot-password")
@limiter.limit(RateLimitConfig.FORGOT_PASSWORD)
async def forgot_password(request: Request, body: ForgotPasswordSchema, background_tasks: BackgroundTasks):
    return await AccountFlowController.forgot_password(body, background_tasks)

@router.post("/reset-password")
async def reset_password(request: Request, body: ResetPasswordSchema):
    return await AccountFlowController.reset_password(body)
```

## OTP (phone) variant
For phone/OTP auth (phone-first apps): a `type="otp_request"` token carries the phone; an
`OTPService` stores/verifies the code in Redis; `verify_otp` denies the otp_request token
after use and issues real tokens. Add `services/auth/otp_service.py` + an SMS provider. The
flow mirrors register/login but keyed on phone + code instead of email + password.

## Token TTLs & rotation
Access 60 min, refresh 30 days (settings). Refresh rotation (issuing a new refresh + denying
the old) is optional — add it if you need one-time-use refresh tokens; otherwise refresh
stays valid until expiry or explicit logout.
