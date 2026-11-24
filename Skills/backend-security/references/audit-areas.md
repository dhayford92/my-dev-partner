# Audit areas (deep)

What to actually read for each area. The scanner flags mechanical smells; these need eyes.
Canonical auth code: [../../_shared-backend/auth.md](../../_shared-backend/auth.md).

## 1. Auth flows
- **aud/iss consistency:** tokens minted and verified with the same `JWT_AUDIENCE`/`JWT_ISSUER`.
  A mismatch means either everything 401s or (worse) verification is loosened to compensate.
- **Refresh + denylist:** refresh verifies `token_type="refresh"`, checks the denylist, rejects
  inactive users. Logout and password-reset deny tokens.
- **Purpose-typed tokens:** verification/reset/OTP tokens carry a distinct `type` and are
  verified with it — otherwise a reset token could be replayed as an access token.
- **No enumeration:** forgot-password / request-verification return the same response whether or
  not the account exists.
- **Password:** bcrypt via `PasswordService` (cost 12), never a custom/`hashlib` scheme; strength
  checked on set/reset.

## 2. Permission boundaries  ← the highest-value read
- **Guard present + correct persona** on every private route (scan catches *missing*).
- **Ownership/tenant scoping in the QUERY** — this is what the scanner cannot see. A route may be
  correctly `CurrentAdminUser`-guarded yet let any admin read any organization's rows because the
  query is `Model.get(id=...)` without `organization_id=perm["organization_id"]` /
  `team_id=auth.team_id` / `user_id=auth.user_id`. Trace every read/mutation for the scope filter.
- **IDOR:** `GET /resource/{id}` must verify the caller owns/*may see* `{id}`, not just that
  they're authenticated.
- **RBAC checks** (if used) actually gate the action (`has_permission(module, action)`), and the
  returned `organization_id` scopes the query.

## 3. Input validation
- Every request body is a pydantic schema with constrained `Field`s (lengths, `ge/le`, `EmailStr`,
  `pattern`). No `dict`/`Any` bodies passed to the DB unfiltered.
- `sort`/`order_by` and dynamic `filter` keys come from an **allow-list**, never a raw client
  string.
- File uploads validated by extension/content-type (storage service already does this).

## 4. Injection
- No `f"... {value} ..."`, `%`, `.format`, or `+` building SQL passed to `execute_query`/raw.
- RLS `set_rls_context` interpolates `user_id`/`team_id` into `SET LOCAL` — those MUST be
  validated UUIDs before the call (cast/validate upstream).
- Tortoise `.filter(**kwargs)` is parameterised — safe; raw SQL is the risk.

## 5. Secrets handling
- Nothing hardcoded (keys, passwords, tokens). `.env` gitignored; `.env.example` has empty values.
- Secrets read only via `settings`. Never logged, never in a response, never in an error `detail`.
- Webhook secrets verified on inbound webhooks (signature check before processing).

## 6. Rate limiting
- `login`, `register`, `otp`, `forgot-password`, `reset-password`, `refresh` all `@limiter.limit`.
- Consider limits on expensive/enumerable endpoints (search, export, invite).

## 7. PII exposure
- Logs and `ActivityLog.metadata` run through `redact()` (phones/emails/tokens/passwords).
- Responses never include `password_hashed`, secrets, or another user's PII. An auth response may
  return the caller's own tokens — that's intended; a *list* endpoint leaking others' emails is
  not.

## 8. Dependency vulnerabilities
- `pip-audit -r requirements.txt`. Triage: fix HIGH/critical, pin, avoid abandoned packages.
- Versions pinned (`==`) so a transitive bump can't silently introduce a CVE.

## 9. Privilege escalation
- `role`, `is_superuser`, `user_type`, `organization_id` are **never** taken from a self-service
  request body. Admin/role assignment is a super-admin-only path.
- Super-admin actions re-check the admin model's role (not just the JWT claim).
- Portal (`portal:true`) and platform tokens don't cross surfaces.
- Mass-assignment: `Model.create(**body.model_dump())` must not let a client set protected fields
  (role/status/balance) — use an explicit field list or a create-schema without them.
