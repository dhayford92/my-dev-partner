# Maintenance workflow

The context is maintained **inline with code changes**, not in a periodic sweep. This file is
the operating procedure.

## On project start
1. `init_context.py --project <ROOT>` — creates the six core files (`--with-frontend` also
   creates `COMPONENTS.md`; `--with-mobile` also creates `SCREENS.md`).
2. Fill `OVERVIEW.md` by hand (product purpose/personas/flows can't be derived from code).
3. Populate `SCHEMA.md` from the current models, `API.md` from the current routers,
   `ARCHITECTURE.md` from the components/services/jobs/integrations (per surface present).
4. Seed `DECISIONS.md` with the foundational choices (authz model, deployment, any deviation
   from `../../_shared-backend/`, `../../_shared-web/`, or `../../_shared-mobile/` —
   including a deliberate mobile-vs-web divergence, e.g. no dark mode on mobile).
5. `verify_context.py` — confirm SCHEMA/API cover every table/route.

## On every change (the loop)
After making a code change in a task, before considering the task done:
1. Ask: **which context file does this touch?** (use the table in SKILL.md).
2. Update that file with the new fact — same task, same diff.
3. Add a `CHANGELOG.md` entry (newest first, absolute date).
4. If the change embodies a non-obvious decision, add an ADR to `DECISIONS.md`.

Examples:
- Added `OrderModel` → add its table block to `SCHEMA.md`; changelog "Added orders table".
- Added `POST /core/api/v1/admin/examples` → add the row to `API.md`; changelog entry.
- Swapped Resend for another provider → update `ARCHITECTURE.md` integrations; ADR for the why.

## On handoff / periodically
- Run `verify_context.py` and resolve every reported drift.
- Skim `OVERVIEW.md` and `ARCHITECTURE.md` for anything now false.

## What NOT to put in context
- Conventions (those live in `../../_shared-backend/` / `../../_shared-web/` /
  `../../_shared-mobile/` and apply fleet-wide).
- Secrets or credentials.
- Long code dumps — reference the file path instead.
- Speculative/planned work (use OVERVIEW "out of scope" or an ADR marked `proposed`).

## Keep it diff-friendly
Small, factual lines and tables. A context update should be a 2–5 line diff most of the time.
If updating one fact rewrites a whole section, the section was too prose-y — restructure into
rows.
