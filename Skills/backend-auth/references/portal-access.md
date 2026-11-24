# Admin portal access control

The admin portal is a **separate auth surface** from the platform (client/vendor) app. Assets
in `assets/portal/portal_auth.py`. This is the portal-token model.

## Token separation
Portal JWTs carry a `portal: true` claim plus a `role` (admin | finance | user). Platform
guards reject portal tokens and vice versa, so a portal token can't be used on client routes.

Issue a portal token:
```python
access, jti, exp = JWTService.create_access_token(
    user_id=portal_user.id, type="access",
    additional_claims={"portal": True, "email": portal_user.email, "role": portal_user.role})
```

## Guards
```python
from src.libs.portal_auth import PortalUser, PortalAdmin, PortalFinanceOrAdmin

@portal_router.get("/plans", ...)
async def list_plans(auth: PortalUser): ...          # any portal user

@portal_router.post("/plans", ...)
async def create_plan(auth: PortalFinanceOrAdmin): ...   # finance or admin

@portal_router.delete("/users/{id}", ...)
async def remove_user(auth: PortalAdmin): ...        # admin only
```

`get_portal_user` verifies the token, asserts `portal: true` (403 otherwise), and checks the
denylist. `get_portal_admin` / `get_portal_finance_or_admin` narrow by `role`.

## Portal role matrix (example — adapt per product)
| Role | Can do |
|------|--------|
| `admin` | Everything; see all portal activity logs |
| `finance` | CRUD plans/billing; see own activity only |
| `user` | Read plans; see own activity only |

## Routing
Portal routes live under a `/portal` prefix on the users sub-app:
`/users/api/v1/portal/{feature}`. Router files: `portal_auth_router.py`,
`portal_users_router.py`, `portal_plans_router.py`, etc. **No team/tenant scope** on portal
routes.

## Portal models
- `PortalUserModel` (`portal_users`) — portal accounts with `role`.
- Optionally `PortalSession` (`portal_sessions`) — server-side refresh storage if you want
  session listing/revocation beyond the stateless denylist.
- `PortalActivityLog` (`portal_activity_log`) — portal audit trail (no team_id), written
  directly by portal controllers (separate from the platform `ActivityLog`).

## Invitation flow (typical)
1. `POST /portal/users/invite` (admin) → create inactive `PortalUserModel` + a
   `type="portal_invite"` token.
2. Email the invite URL with `?token=...`.
3. `POST /portal/accept-invite` with token + password → activate, set hash, return a portal
   JWT.

## Portal activity logging
Portal mutations write to `PortalActivityLog` directly (no team_id), NOT the platform
`ActivityService`. Keep the two trails separate so admin actions and tenant actions don't mix.
