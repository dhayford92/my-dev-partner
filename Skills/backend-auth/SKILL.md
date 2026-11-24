---
name: backend-auth
description: >-
  Build authentication and authorization in Denzel's canonical FastAPI stack, reproduced
  exactly — JWT (python-jose HS256, 60-min access, 30-day stateless refresh + Redis denylist),
  bcrypt cost 12, registration, login, refresh, logout, email verification, password reset,
  the admin-vs-client split, HTTPBearer→AuthContext→persona guards, and the three
  authorization models (persona guards by default; org-scoped JSON RBAC and team+Postgres-RLS
  as opt-in modules) with permission checks at both route and service level, admin portal
  access control (portal JWT with portal:true + role), and the seeder for default
  roles/permissions. USE THIS whenever adding or changing auth — login/register/logout/refresh,
  password reset or email verification, JWT/token handling, permission or role checks, RBAC,
  multi-tenant/team access, admin portal access control, or "who can do what" logic. Use
  backend-scaffold for the base auth in a new project; this skill deepens and extends it.
---

# backend-auth

Reproduce auth + authz exactly. **The JWT/bcrypt/denylist/guard code and the three authz
models are defined in [../_shared-backend/auth.md](../_shared-backend/auth.md)** — read it; this skill provides
the drop-in flow modules and opt-in authz modules, and explains how to wire each.

## When to use
- Adding/altering login, register, refresh, logout.
- Adding password reset or email verification.
- Any authorization decision: persona guards, RBAC, team/RLS, portal access, permission checks.

`backend-scaffold` already ships the base (register/login/refresh/logout + guards +
JWTService/PasswordService/token_denylist + a seeded relational RoleModel). This skill adds the
verification/reset flows and the richer authz models.

## The base (already canonical)
JWT HS256 via python-jose; claims `sub, jti, iat, exp, iss, aud, type, user_type`; bcrypt cost
12; 60-min access, 30-day stateless refresh; Redis denylist for revocation; `HTTPBearer` →
`AuthContext` → `Current<Persona>User` guards; a mismatched `user_type` → 403. Purpose-typed
tokens (`type="otp_request"`, `"email_verification"`, `"password_reset"`) prevent replay. Full
code: [../_shared-backend/auth.md](../_shared-backend/auth.md).

## Add: email verification + password reset
Drop-in files in `assets/flows/`:
- `verification_reset_schemas.py` → `src/schemas/users/`
- `verification_reset_controller.py` → `src/apps/users/controllers/` (`AccountFlowController`)
- `reset_password.html` → `src/templates/` (`email_verification.html` ships with scaffold)

Then add routes to your client auth router (each takes `background_tasks: BackgroundTasks`):
`POST /verify-email/request`, `POST /verify-email`, `POST /forgot-password`,
`POST /reset-password`. Reset denies all the user's tokens (log out everywhere). See
[references/auth-flows.md](references/auth-flows.md).

## Choose the authorization model
Authz is **project-dependent** (per the owner). Pick one — details + wiring in
[references/authz-models.md](references/authz-models.md):

| Model | When | Assets |
|-------|------|--------|
| **Persona guards** (default) | B2C / simple admin | ships with scaffold (`libs/auth.py`) |
| **Org-scoped JSON RBAC** | B2B, configurable per-org roles | `assets/rbac/` |
| **Team + Postgres RLS** | multi-tenant SaaS | `assets/rls/` + `assets/portal/` |

- **RBAC** (`assets/rbac/`): `role_model.py` (JSON `{module:{read,write,delete}}`, org-scoped,
  M2M, `DEFAULT_ROLE_LIST`), `permission_checks.py`
  (`UserPermissionChecks.has_client_user_permission(email, module, action)` → `{user_id,
  organization_id}`), `seed_rbac.py`. Checks run **in the controller**, then scope queries by
  the returned `organization_id`.
- **Team + RLS** (`assets/rls/rls.py`): JWT carries `team_id`; queries filter by it; Postgres
  RLS policies enforce isolation via `set_rls_context`. See
  [references/authz-models.md](references/authz-models.md).

## Admin portal access control
`assets/portal/portal_auth.py` — a separate auth surface. Portal JWTs carry `portal: true` +
`role` (admin|finance|user); portal routes have **no** team scope; guards
`PortalUser/PortalAdmin/PortalFinanceOrAdmin`. See
[references/portal-access.md](references/portal-access.md).

## Permission checks: route vs service level
- **Route level** — persona/portal via the dependency (`CurrentAdminUser`, `PortalAdmin`).
- **Service/controller level** — data-driven RBAC via
  `UserPermissionChecks.has_client_user_permission(...)` before mutating, then org-scope every
  query. Both layers coexist: the guard proves *who*, the check proves *what they may do*.

## Seeder
Default roles/permissions: `scaffold`'s `scripts/seed.py` (relational RoleModel + super admin)
or `assets/rbac/seed_rbac.py` (org-scoped `DEFAULT_ROLE_LIST`). Both idempotent. See
[../_shared-backend/database.md](../_shared-backend/database.md) seeders and
[references/authz-models.md](references/authz-models.md).

## Don't
- Don't call `jose`/`bcrypt` directly — use `JWTService`/`PasswordService`.
- Don't leak account existence in verification/reset responses (always the same message).
- Don't skip denylisting on logout / password reset.
- Don't mix authz models silently — pick one per project and say which (per `dev-partner`).
