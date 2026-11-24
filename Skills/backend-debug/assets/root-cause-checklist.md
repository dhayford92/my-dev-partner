# Root-cause checklist

Work top to bottom. Don't propose a fix until 1–4 are answered.

## 1. What it actually does
- [ ] Reproduced the failure (or pinned the exact failing line from the trace).
- [ ] Stated behaviour as `inputs → actual output/error`, precisely.
- [ ] Read the real failing path (ignored names/comments/intent).
- [ ] Separated symptom (where it threw) from behaviour (what went wrong).

## 2. True origin
- [ ] Traced backwards to the first point reality diverges from what's required.
- [ ] Confirmed the origin is the cause, not just an earlier symptom.
- [ ] Cited `file:line` for the origin.

## 3. Why (causal)
- [ ] Explained *why* the state is wrong here (ordering / assumption / missing invariant).
- [ ] The explanation predicts the observed failure (not just restates it).

## 4. Blast radius
- [ ] Listed the edge cases that hit the same flaw (null/empty/expired/concurrent/first-run/tz…).
- [ ] Searched for adjacent code paths with the same pattern (copy-paste, missing guard).
- [ ] Decided the fix scope = the class of bug, not just this instance.

## 5. Fix + trade-off
- [ ] Chose the fix that prevents the class (fail-fast / unrepresentable bad state) where possible.
- [ ] Stated the trade-off explicitly (perf / complexity / behaviour change / migration).
- [ ] If it's a narrow/temporary patch, labelled it as such + named the real cause left open.
- [ ] Fix matches `../../_shared-backend/` conventions.

## 6. Verify
- [ ] Ran the actual failing path with the reproducing input; observed corrected behaviour.
- [ ] Checked the step-4 edge cases.
- [ ] Checked one previously-working input for regression.
- [ ] If unverifiable here: said so + named exactly what must be run (input → expected).

## Report
- [ ] Wrote it up as: what it does → origin (file:line) → why → other affected paths → fix +
      trade-off → verification.
