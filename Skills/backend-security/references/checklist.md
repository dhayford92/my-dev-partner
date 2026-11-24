# Security audit checklist

⚙ = the scanner covers it mechanically. The rest need reading. Cite `file:line`; state the
exploit; assign severity (HIGH/MED/LOW).

## Auth
- [ ] Token mint/verify use the same aud/iss.
- [ ] Refresh checks `token_type`, denylist, active user.
- [ ] Verify/reset/OTP tokens are purpose-typed and verified as such.
- [ ] No account enumeration on forgot-password / request-verification.
- [ ] bcrypt via PasswordService; strength enforced.
- [ ] Logout + reset deny tokens.

## Access control
- [ ] Every private route has the correct persona guard. ⚙(missing guard)
- [ ] Ownership/tenant scope enforced IN THE QUERY (`user_id`/`organization_id`/`team_id`). ← read
- [ ] `GET /{id}` verifies the caller may see `{id}` (no IDOR).
- [ ] RBAC `has_permission` gates the action; returned org scopes the query.
- [ ] Super-admin actions re-check the admin model role.

## Input & injection
- [ ] Every body is a constrained pydantic schema.
- [ ] `sort`/dynamic filters from an allow-list, not raw client strings.
- [ ] No string-built SQL into `execute_query`/raw. ⚙
- [ ] RLS `SET LOCAL` values are validated UUIDs.
- [ ] Uploads validated (extension/content-type).

## Secrets
- [ ] No hardcoded keys/passwords/tokens. ⚙
- [ ] `.env` gitignored; `.env.example` empty. ⚙
- [ ] Secrets only via `settings`; never logged/returned/in error detail.
- [ ] Inbound webhooks verify their signature.

## Rate limiting
- [ ] login/register/otp/forgot/reset/refresh limited. ⚙
- [ ] Expensive/enumerable endpoints limited.

## PII & data exposure
- [ ] Logs + activity metadata redacted (`redact()`). ⚙(logs)
- [ ] No password hash/secret in any response schema. ⚙
- [ ] List endpoints don't leak other users' PII.

## Privilege escalation
- [ ] `role`/`is_superuser`/`user_type`/`organization_id` never from a self-service body. ⚙(role)
- [ ] `create(**body.model_dump())` can't set protected fields (mass-assignment).
- [ ] Portal vs platform token separation intact.

## Config & hardening
- [ ] CORS not `*` + credentials. ⚙
- [ ] `DEBUG=false` and docs off in prod. ⚙
- [ ] Errors don't leak stack traces / internal ids to clients.

## Dependencies
- [ ] `pip-audit -r requirements.txt` clean of HIGH/critical.
- [ ] Versions pinned.

## Report format
```
## Security audit — <scope>

### HIGH (n)
- [category] file:line — <exploit path> → <fix>

### MED (n)
### LOW (n)

### Dependencies
- pip-audit result summary
```
