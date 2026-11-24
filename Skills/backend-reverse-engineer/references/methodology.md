# Reverse-engineering methodology

The order matters: **facts → flows → risk → drift/dead code → staged plan.** Skipping to
"here's how I'd rewrite it" before establishing what's actually there produces confident,
wrong recommendations.

## 1. Facts before opinions
Run `map_codebase.py` and read the inventory. Do not form a refactor opinion until you can
state, from evidence: how many sub-apps/models/routes exist, what the auth model is, what the
tenancy model is, and where config/logging/errors are handled. The mapper gives you the
skeleton; confirm by reading.

## 2. Trace real flows, not names
A function called `verify_otp` might not verify anything; a "service" might hold route logic.
Trace the 2–3 most important flows through the actual calls: entry → guard → controller →
services/models → DB, plus async side-effects (background email, activity log, scheduled
follow-up). Write down what each step *does*, with `file:line`. Surprises here are usually the
real bugs.

## 3. Rank by risk = impact × likelihood
- **Impact:** data loss > auth/permission bypass > wrong results > performance > style.
- **Likelihood:** on every request > common path > rare edge > only under specific config.
A subtle auth bypass on the login path outranks a messy-but-correct utility. Put the ranking in
the report table, most-severe first, each with evidence.

## 4. Drift vs. dead code
- **Drift** = deviation from `../../_shared-backend/` or the codebase's own conventions (the mapper flags
  many automatically). Impact of drift is usually maintainability + latent bugs, not immediate
  failure — rank accordingly.
- **Dead code** = unreachable/unused: commented-out endpoints, models not in `ORM_MODELS`,
  functions with no callers, superseded implementations. State confidence — dynamic imports,
  string model refs, and scheduler registration mean "no direct caller" ≠ "unused."

## 5. Staged, reversible refactor
- Order stages by value/risk: highest-value-lowest-risk first (often: logging discipline, config
  hardening, adding missing indexes, fixing an N+1).
- Each stage: independently shippable, compiles, passes `/health`, revertible.
- Write concrete replacement code for the top stages (matching `../../_shared-backend/`), not just "improve
  X."
- Defer risky, high-blast-radius changes (auth model swap, tenancy change, table restructure)
  behind their own stages with explicit migration + rollback plans.

## 6. Respect the owner's conventions
Prefer existing conventions over "best practice." If a convention looks wrong (e.g. FloatField
for money, `{detail}` errors), note it as a **discussion item** in report §8 / §9 with the
trade-off — don't unilaterally rewrite it. The Phase-4-style optimisation call is the owner's.

## Anti-patterns to avoid
- Presenting the target state as if it's current (breaks the WHAT-IS/WHAT-SHOULD-BE split).
- "Rewrite it all" — never actionable, never safe.
- Ranking by ease of fix instead of risk.
- Guessing intent instead of listing an open question.
