---
name: backend-reverse-engineer
description: >-
  Map an existing backend codebase as it was ACTUALLY built (not as documented) — real
  architecture and component structure, true data flow through the live code paths, critical
  problem areas ranked by risk, architectural drift from conventions, and dead/unreachable code —
  then produce a staged, incremental refactoring strategy with concrete production-grade
  replacement code. Always separates WHAT IS from WHAT SHOULD BE. Includes a script that
  inventories models/tables/routers/routes/services and auto-detects convention drift. USE THIS
  whenever inheriting, auditing, or trying to understand an unfamiliar or messy existing project,
  when asked to "map", "audit the architecture", "reverse engineer", "understand this codebase",
  "find the tech debt", "what's wrong with this project", or plan a refactor of existing code. For
  a single bug use backend-debug; for a pre-commit review of a diff use backend-review.
---

# backend-reverse-engineer

Understand a codebase as built, find what's risky, and plan a safe refactor. **Always separate
WHAT IS (reality) from WHAT SHOULD BE (target).** Never conflate the two, and never refactor
before mapping.

## When to use
- Inheriting or auditing an unfamiliar/legacy/messy project.
- "Map this", "reverse engineer", "find the tech debt", "what's wrong here", "plan a refactor".

Single bug → `backend-debug`. Reviewing a diff → `backend-review`. Designing something new →
`backend-architect`.

## Process
1. **Inventory (facts first).** Run the mapper:
   ```powershell
   python .\scripts\map_codebase.py --project "D:\...\some-api"          # human report
   python .\scripts\map_codebase.py --project "D:\...\some-api" --json   # machine-readable
   ```
   It lists sub-apps, models+tables, routers+routes, controllers, services, and auto-detects
   drift (config style, `print()` vs logger, pagination shape, error style, missing `/api/v1`,
   Float-for-money, missing soft delete, duplicate `related_name`, unregistered models). This is
   a **fact-finder** — it reports WHAT IS; judgement is yours.
2. **Read the real code paths.** For the 2–3 most important flows, trace entry → guard →
   controller → services/models → DB + async side-effects. Document what the code *actually*
   does, not what names/docs imply.
3. **Rank problem areas by risk.** Most-severe first: what breaks, for whom, how likely, with
   `file:line` evidence.
4. **Spot drift & dead code.** Start from the mapper's drift list; add unreachable code,
   commented endpoints, unregistered models, functions with no callers.
5. **Plan a staged refactor.** Incremental, each stage independently shippable and low-risk. For
   high-value stages, write **concrete replacement code** matching `../_shared-backend/`.
6. **Report** using [assets/report_template.md](assets/report_template.md).

## The WHAT-IS / WHAT-SHOULD-BE discipline
Every finding and recommendation names both:
> **What is:** `configs/settings.py` reads config via `os.environ` in a plain class; missing
> vars surface as `None` at runtime (`settings.py:13`).
> **What should be:** pydantic-settings `BaseSettings` with typed UPPER_CASE `Field`s
> (`../_shared-backend/config.md`), so a missing var fails fast at boot.

Never present the target as if it's the current state, and never "fix" reality in the report
without labelling it a change.

## Drift is measured against `../_shared-backend/`
The canonical target is the shared conventions:
[config](../_shared-backend/config.md) · [routing](../_shared-backend/routing.md) ·
[response-contract](../_shared-backend/response-contract.md) · [database](../_shared-backend/database.md) ·
[auth](../_shared-backend/auth.md) · [logging](../_shared-backend/logging.md). The mapper encodes several of
these as automatic checks; read the code for the rest.

## Refactor safety
- **Incremental only.** No big-bang rewrites. Each stage compiles, passes `/health`, and is
  revertible.
- **Preserve working conventions.** Prefer the owner's existing conventions over "best practice";
  flag ones you think are wrong as discussion items (report §8), don't unilaterally change them.
- **Live data:** any schema change follows [../_shared-backend/database.md] + backend-database's
  safe-migrations rules.
- **Verify each stage** (see `backend-debug` / the `verify` skill) before the next.

## Rules
- Map before you judge; judge before you change.
- Cite `file:line` for every problem.
- Rank by risk (impact × likelihood), not by how easy it is to fix.
- Dead-code claims state confidence (certain / likely) — "no callers found" ≠ "definitely unused"
  (dynamic imports, string refs).
- Unknown intent → Open Questions, not a guess.
