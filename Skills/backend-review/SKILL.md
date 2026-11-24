---
name: backend-review
description: >-
  Pre-commit review of backend changes against Denzel's conventions — correctness, convention
  conformance, security, performance (N+1, indexing), error handling, logging coverage, test
  coverage, and migration safety — producing findings grouped as BLOCKING / SHOULD-FIX / NITPICK.
  Includes a script that mechanically pre-scans changed files (syntax, missing response_model,
  swallowed exceptions, missing rate limits on auth routes, hardcoded secrets, error-style drift,
  Float-for-money, missing soft delete) so the human review focuses on logic. USE THIS before
  committing/pushing, when asked to "review", "check my changes", "is this ready", "look over
  this PR/diff", or as a final pass on generated/edited backend code. For a single bug use
  backend-debug; for a security-only deep audit use backend-security; for whole-codebase mapping
  use backend-reverse-engineer.
---

# backend-review

A disciplined pre-commit pass over a change. Two layers: a **mechanical pre-scan** (script) then
a **human/AI read** for correctness and logic the script can't judge. Output grouped
**BLOCKING / SHOULD-FIX / NITPICK**.

## When to use
Before committing/pushing; "review this", "is this ready", "check my changes", final pass on
generated code.

Single bug → `backend-debug`. Security deep-dive → `backend-security`. Whole codebase →
`backend-reverse-engineer`.

## Process
1. **Mechanical pre-scan:**
   ```powershell
   python .\scripts\review_changes.py --project "D:\...\some-api"            # changed vs HEAD (git)
   python .\scripts\review_changes.py --project "D:\...\some-api" --base main # vs a branch
   python .\scripts\review_changes.py --project "D:\...\some-api" --all       # whole src (no git)
   ```
   Catches the deterministic issues (syntax, missing `response_model`, swallowed `except`,
   missing rate limit on auth routes, hardcoded secrets, error-style drift, Float-for-money,
   missing soft delete) and groups them. Exit code is non-zero on any BLOCKING finding (usable in
   a hook). It's a **pre-filter, not the review**.
2. **Read for what the script can't judge** — the [full checklist](references/review-checklist.md):
   correctness/logic, security, performance, error handling, logging coverage, tests, migration
   safety. This is where the real review happens.
3. **Group & report** using [references/grouping.md](references/grouping.md) and
   [assets/findings-template.md](assets/findings-template.md).

## The nine review categories
1. **Correctness** — does it do what it should? Edge cases, off-by-one, wrong status, wrong
   scope, race conditions. (Read; the script can't.)
2. **Conventions** — matches `../_shared-backend/` (structure, routing, envelopes, naming, config).
3. **Security** — auth guard present + correct persona, input validated, no injection, no secret
   leak, PII handled. (Deep dive → `backend-security`.)
4. **Performance** — N+1 (`prefetch_related`), missing index on filtered columns, unbounded
   queries, sync calls in async paths.
5. **Error handling** — the try/except ladder, `HTTPException(detail, X-Error-Code)`, no swallowed
   exceptions.
6. **Logging coverage** — `logger` not `print`; mutations audited via `ActivityService`; PII
   redacted; errors logged before 500.
7. **Test coverage** — is the changed logic exercised? (The repos have little/no tests; flag
   critical untested paths, don't demand a suite that doesn't exist.)
8. **Migration safety** — new/changed models have a migration; the SQL is safe for live data
   (`../_shared-backend/database.md` + backend-database safe-migrations).
9. **Context sync** — did `SCHEMA.md`/`API.md` get updated in the same change (`project-context`)?

Per-category detail: [references/review-checklist.md](references/review-checklist.md).

## Grouping (the output contract)
- **BLOCKING** — must fix before commit: broken/incorrect, security hole, data-loss migration,
  won't compile, secret committed.
- **SHOULD-FIX** — real issues that aren't release-blockers: convention drift, missing rate
  limit, N+1, swallowed error, missing activity log on an audited mutation.
- **NITPICK** — style/polish: naming, a missing `response_model` on a trivial route, comments.

Definitions + how to phrase findings: [references/grouping.md](references/grouping.md).

## Rules
- **Read the logic** — the script finds mechanical issues; correctness/security/perf need eyes.
- **Cite `file:line`** and say concretely what breaks, not "this looks off."
- **Respect the owner's conventions** — review against `../_shared-backend/`, not personal preference; a
  convention you'd change goes to the Phase-4 optimisation report, not a blocking finding.
- **Don't invent test demands** — flag genuinely risky untested paths; don't require coverage the
  project never had.
- **False positives cost trust** — verify a flagged issue is real before listing it BLOCKING.
