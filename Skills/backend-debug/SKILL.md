---
name: backend-debug
description: >-
  Root-cause debugging for the FastAPI + Tortoise backend, with strict discipline: first
  establish what the code ACTUALLY does (not what it appears to intend), then trace the failure
  to its true origin, explain WHY it failed in causal terms, enumerate hidden edge cases and
  adjacent code paths carrying the same latent bug, then propose the most robust fix and state
  explicitly what that fix trades off. It never patches a symptom without saying so, and never
  claims a fix works without a verification step. USE THIS whenever something is broken,
  failing, erroring, flaky, throwing, returning wrong data, hanging, leaking, or "works
  sometimes" — any bug, exception, stack trace, 500, failing request, race, or incorrect result
  in the backend. For understanding a whole unfamiliar codebase use backend-reverse-engineer;
  for a pre-commit quality pass use backend-review.
---

# backend-debug

Find the true cause, fix it robustly, prove it. Discipline over guesswork: the fastest wrong
fix is the one that patches a symptom.

## When to use
Anything broken/failing/flaky/wrong: an exception, a 500, a wrong result, a hang, a leak, a
race, "works sometimes." One bug at a time.

Whole-codebase understanding → `backend-reverse-engineer`. Pre-commit quality → `backend-review`.

## The required method (in order — don't skip)
1. **Establish what the code ACTUALLY does.** Read the real path, not the names or the intent.
   Reproduce the failure or pin the exact failing line from the trace. State the observed
   behaviour precisely (inputs → actual output/error).
2. **Trace to the true origin.** Follow the call chain back from the symptom to the first point
   where reality diverges from what's required. The origin is usually upstream of where the
   exception surfaces. Cite `file:line`.
3. **Explain WHY, causally.** Not "it's null" — *why* is it null here? What state/assumption/
   ordering made it so? A cause you can't explain, you can't fix.
4. **Enumerate hidden edge cases + adjacent bugs.** What other inputs hit the same flaw? Which
   *other* code paths share the same latent bug (same pattern copy-pasted, same missing check)?
   Fixing one instance and leaving three is not a fix.
5. **Propose the most robust fix — and state its trade-off.** The fix that prevents the class of
   bug, not just this instance. Say explicitly what it costs (performance, complexity, behaviour
   change, migration).
6. **Verify.** Never claim it works without exercising the actual failing path and observing the
   corrected behaviour. See [references/verification.md](references/verification.md).

Full method with examples: [references/debugging-method.md](references/debugging-method.md).
Checklist: [assets/root-cause-checklist.md](assets/root-cause-checklist.md).

## Two hard rules
- **Never patch a symptom silently.** If you must apply a narrow/temporary fix (a guard, a
  try/except, a default), say so explicitly and name the underlying cause it doesn't address.
- **Never claim a fix works without verifying.** "This should fix it" is not done. Drive the
  path; observe the result. If you can't verify, say that plainly.

## Stack-specific failure modes
Most backend bugs here cluster into known patterns — async/await misuse, Tortoise N+1 /
transaction / relation errors, JWT/aud/denylist issues, migration drift, background-task and
lifespan ordering, Redis outages breaking auth. See
[references/common-failure-modes.md](references/common-failure-modes.md) to jump to the likely
cause faster (but still verify the specific case — a matching pattern is a hypothesis, not a
diagnosis).

## Anti-patterns
- "Add a try/except and move on" without naming the cause.
- Fixing the line that threw instead of the line that made the state wrong.
- Changing code until the error disappears (you've hidden it, not fixed it).
- Declaring success from reading the diff instead of running the path.
- Fixing one occurrence of a copy-pasted bug and ignoring its twins.
