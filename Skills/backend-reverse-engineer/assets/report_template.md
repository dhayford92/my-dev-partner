# Reverse-Engineering Report — {{PROJECT}}

_Date: {{DATE}} · Commit/branch: {{REF}}_

> This report separates **WHAT IS** (the system as actually built) from **WHAT SHOULD BE** (the
> target). Every recommendation names both. Nothing here is applied — it's an analysis.

## 1. Executive summary
<!-- 3–6 sentences: what the system is, its overall health, the top 3 risks, and the headline
recommendation. -->

## 2. Architecture as built (WHAT IS)
<!-- The real structure from map_codebase.py + reading the code. Sub-apps, domains, the
controller/service/model split as actually practised (not as documented). Note where reality
diverges from any existing docs. -->

- Sub-apps / domains:
- Auth model in practice:
- Data layer / tenancy:
- Cross-cutting (logging, errors, config) in practice:

## 3. Data flow (as built)
<!-- Trace the 2–3 most important flows end to end through the real code paths: entry → guard →
controller → services/models → DB + async side-effects. Call out where the flow does something
surprising. -->

## 4. Critical problem areas (ranked by risk)
<!-- Ordered most-severe first. For each: WHAT IS (the current behaviour + evidence
file:line), the RISK (what breaks, for whom, how likely), and WHAT SHOULD BE (target). -->

| # | Area | Risk | Evidence | What is → What should be |
|---|------|------|----------|--------------------------|
| 1 | | high/med/low | file:line | |

## 5. Architectural drift
<!-- Where the code has drifted from its own conventions or the canonical ../../_shared-backend/ set.
Use map_codebase.py drift output as the starting list; explain the impact of each. -->

## 6. Dead / unreachable code
<!-- Unused modules, commented-out endpoints, models not registered in ORM_MODELS, functions
with no callers, superseded implementations left in place. Mark confidence (certain / likely). -->

## 7. Staged refactoring strategy
<!-- Ordered, incremental. Each stage independently shippable and low-risk. For the highest-value
stages, include CONCRETE production-grade replacement code (matching ../../_shared-backend/ conventions),
not just prose. -->

### Stage 1 — <name> (low risk, high value)
- **What is:**
- **What should be:**
- **Change:** <!-- concrete steps + replacement code -->
- **Risk / rollback:**

### Stage 2 — …

## 8. What NOT to change
<!-- Working conventions to preserve. Prefer the owner's existing conventions over "best
practice"; if a convention seems wrong, note it here as a discussion item, don't unilaterally
refactor it. -->

## 9. Open questions
<!-- Anything whose intent couldn't be inferred from the code. These block the risky refactors. -->
