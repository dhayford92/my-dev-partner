# Grouping findings

Every finding lands in exactly one bucket. Severity is about **consequence**, not effort.

## BLOCKING — do not commit until fixed
- Incorrect behaviour on a real input (wrong result, wrong scope, crash).
- Security hole: missing/incorrect auth guard, missing ownership/tenant scope, injection,
  secret committed, PII leaked in a response.
- Data-loss or unsafe-on-live migration (unexpected DROP, un-backfilled NOT NULL).
- Won't compile / import error.

## SHOULD-FIX — real issues, not release-blockers
- Convention drift from `../../_shared-backend/` (config style, error style, envelope, naming).
- Missing rate limit on an auth/OTP/reset endpoint.
- N+1 or a missing index on a hot path.
- Swallowed exception (no log/raise); error logged but leaks internals.
- Audited mutation with no `ActivityService` call.
- Context files not updated for a schema/API change.

## NITPICK — polish
- Naming, a missing `response_model` on a trivial route, comment density, dead import.
- Money-as-Float / missing soft-delete **when confirmed intentional or on a reference table**.

## Phrasing a finding
`[SEVERITY] file:line — <what's wrong> → <concrete consequence> → <fix>.`

> `[BLOCKING] client_orders_controller.py:42 — list() returns every order, not just the caller's
> (no user_id filter) → any client can read others' orders → filter by auth.user_id.`

> `[SHOULD-FIX] admin_router.py:18 — POST /login has no @limiter.limit → brute-force exposure →
> add @limiter.limit(RateLimitConfig.LOGIN) and a request: Request param.`

Good findings are specific, cite a location, name the consequence, and give the fix. "This looks
messy" is not a finding.

## Output shape
```
## Review — <change/PR>

### BLOCKING (n)
- file:line — problem → consequence → fix

### SHOULD-FIX (n)
- ...

### NITPICK (n)
- ...

### Notes
- context sync status, test status, anything deferred to the optimisation report.
```

If a bucket is empty, say "none" — don't omit it. A review with zero BLOCKING and a clear
SHOULD-FIX list is a good review; inventing blockers to look thorough erodes trust.
