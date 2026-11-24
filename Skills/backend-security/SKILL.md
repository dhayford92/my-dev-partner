---
name: backend-security
description: >-
  Security audit of the FastAPI + Tortoise backend — authentication flows, permission/ownership
  boundaries, input validation, injection surfaces (SQL/order_by/filter), secrets handling, rate
  limiting, PII exposure in logs and responses, dependency vulnerabilities, and admin-privilege
  escalation paths. Includes a heuristic scanner that flags permissive CORS, committed/hardcoded
  secrets, raw-SQL injection, mutating routes without an auth guard, missing auth rate limits, PII
  in logs, secrets leaked in response schemas, and role-from-request-body escalation. USE THIS
  whenever asked to "security review", "audit auth/permissions", "is this secure", "check for
  vulnerabilities/injection/leaks", before shipping anything auth- or payment-related, or when
  reviewing access-control and data-exposure. For a general pre-commit review use backend-review;
  for a single bug use backend-debug.
---

# backend-security

Audit the backend for security holes: who can do what, what's exposed, what's injectable, what
leaks. Two layers: a **heuristic scan** (script) then a **read audit** of the flows the script
can't reason about (ownership scoping, auth-flow logic, escalation paths).

## When to use
"Security review", "audit auth/permissions", "is this secure", "check for injection/leaks",
before shipping auth/payment/admin features.

General pre-commit pass → `backend-review`. Single bug → `backend-debug`.

## Process
1. **Scan:**
   ```powershell
   python .\scripts\security_scan.py --project "D:\...\some-api"          # human report
   python .\scripts\security_scan.py --project "D:\...\some-api" --json    # machine-readable
   ```
   Flags: permissive CORS (`*` + credentials), `.env` not gitignored, hardcoded secrets/keys,
   string-built SQL, **mutating routes with no auth guard**, auth routes missing rate limits, PII
   in logs, secrets in response schemas, `role` set from request body, debug defaults. Exit code
   non-zero on any HIGH. It's a **pre-scan** — the real audit reads flows.
2. **Read audit** the areas the scan can't judge — the
   [audit areas](references/audit-areas.md) and [checklist](references/checklist.md).
3. **Dependency CVEs:** `pip-audit -r requirements.txt` (or `pip install pip-audit` first). The
   scanner can't do this — run it.
4. **Report** findings by severity with `file:line`, concrete exploit, and fix.

## The nine audit areas
1. **Auth flows** — token minting/verification (aud/iss consistency), refresh + denylist, reset/
   verify purpose-typed tokens, no enumeration, bcrypt not custom hashing.
2. **Permission boundaries** — every private route has the right persona guard; **ownership /
   tenant scoping** (`user_id`/`organization_id`/`team_id`) enforced in the query, not just the
   persona. This is the #1 real-world hole and needs reading — the scan only catches a *missing*
   guard, not a *wrong scope*.
3. **Input validation** — pydantic schemas on every body; constrained types; no unvalidated
   client value reaching `order_by`/`filter`/SQL.
4. **Injection** — no f-string/`%`/`.format`/concatenation into `execute_query`/raw SQL; RLS
   `SET LOCAL` values are validated UUIDs (they're interpolated).
5. **Secrets handling** — nothing hardcoded; `.env` gitignored; secrets only via `settings`;
   never logged or returned.
6. **Rate limiting** — auth/OTP/reset/register endpoints limited; sensitive writes limited.
7. **PII exposure** — logs + activity metadata run through `redact()`; responses never include
   password hashes, tokens (unless intended), or secrets.
8. **Dependency vulnerabilities** — `pip-audit`; pinned versions; no abandoned/critical CVEs.
9. **Privilege escalation** — `role`/`is_superuser`/`user_type` never set from client input on
   self-service endpoints; super-admin actions re-check the admin model; portal vs platform token
   separation intact.

Detail per area: [references/audit-areas.md](references/audit-areas.md).

## Severity
- **HIGH** — exploitable now: missing auth/ownership check, injection, secret committed/leaked,
  privilege escalation, PII in a response.
- **MED** — real weakness needing a trigger: PII in logs, missing rate limit, weak validation,
  known-but-not-critical dep CVE.
- **LOW** — hardening: debug defaults, verbose errors, missing security headers.

## Rules
- **Read ownership scoping** — the scan finds *missing* guards; only reading finds a guard that
  checks persona but not ownership (any admin reading any tenant's data). Trace the query filters.
- **Confirm before HIGH** — a flagged item must be a real, reachable exploit. Explain the exploit
  path; don't cry wolf.
- **Never introduce a "fix" that weakens** (loosening CORS, disabling rate limits, printing
  tokens to debug). If you must debug with sensitive data, redact.
- **Report, don't silently patch** auth changes — auth fixes are high-blast-radius; propose,
  explain the exploit, then apply with verification (`backend-debug` discipline).
