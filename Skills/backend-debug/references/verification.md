# Verification — never claim a fix works without it

A fix is a hypothesis until the failing path runs and produces the correct behaviour. Reading
the diff is not verification.

## The rule
Exercise the **actual failing path** and observe the **corrected behaviour**. Then confirm the
edge cases you enumerated (method step 4) are handled.

## How to verify, by change type
- **Endpoint behaviour** → boot the app and hit the route (the `verify` skill / browser preview /
  `curl`/`httpx`), with the input that reproduced the bug. Observe status + body.
- **A wrong value / logic** → reproduce with the triggering input; confirm the output is now
  correct, and try one boundary input.
- **DB / query / N+1** → run the query path; check the result and (for N+1) that the query count
  dropped. `SELECT`-count via logs.
- **Migration** → apply on a scratch DB, confirm schema + a read/write; for live data follow
  safe-migrations and verify on a copy first.
- **Auth** → run the full token cycle (issue → use → refresh → logout→denied), not just the one
  call that failed.
- **Background task / email** → confirm the side effect (row written, log line, message) — the
  HTTP 200 says nothing about the task.

## Minimum evidence to claim "fixed"
State, concretely:
1. The input that reproduced the bug.
2. The behaviour before (error/wrong output).
3. The behaviour after (observed, from actually running it).
4. Which edge cases you checked.

Without those, say "proposed fix, **not yet verified**" and name exactly what needs to be run.

## Regression awareness
- Did the fix change behaviour for the *working* inputs? Check one.
- Did it touch a shared helper used elsewhere? Note the blast radius.
- If you fixed a duplicated bug in one place, verify the twin instances too.

## When you can't verify here
If the environment can't run the path (no DB/Redis, external dependency, prod-only data), do not
imply success. Say: "fix applied; requires verification by running X with input Y, expecting Z."
Honesty about an unverified fix beats a confident wrong claim.
