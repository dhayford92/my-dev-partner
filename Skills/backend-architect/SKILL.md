---
name: backend-architect
description: >-
  Plan and design a complete backend system BEFORE any code is written — component structure,
  data flow, API surface, database schema, auth model, caching strategy, background jobs,
  third-party integrations, error/logging strategy, scaling and security considerations, and
  deployment topology — by interviewing the owner about the product and producing a full
  architecture document from the canonical ARCHITECTURE_TEMPLATE (pre-filled with the stack's
  defaults). This skill writes NO implementation code — it produces the design that scaffold /
  api-design / database / auth then build. USE THIS whenever starting a new system or major
  feature and someone says "design", "architect", "plan the system", "how should we build",
  "spec this out", "data model for", or wants an architecture/design doc before implementation.
  Do NOT use it to write code — hand the finished design to backend-scaffold and the build
  skills. For per-project context upkeep use project-context.
---

# backend-architect

Design the system on paper first. Interview the owner, then produce a complete architecture
document from [assets/ARCHITECTURE_TEMPLATE.md](assets/ARCHITECTURE_TEMPLATE.md), pre-filled with the
canonical defaults. **This skill writes no implementation code.**

## When to use
- Starting a new system or a major feature that needs design before building.
- Someone asks to "architect", "plan", "design", "spec out", or wants a data model / API surface
  before code.

Building it? That's `backend-scaffold` + `backend-api-design` + `backend-database` +
`backend-auth`. Maintaining the doc afterward? That's `project-context`.

## Process
1. **Start the doc**:
   ```powershell
   python .\scripts\new_architecture.py --name "My API" --out "D:\...\my-api\docs\ARCHITECTURE.md"
   ```
   This lays down the template (16 sections, defaults pre-filled).
2. **Interview** the owner — grouped, not one question at a time. See
   [references/interview-guide.md](references/interview-guide.md). Do not guess product facts;
   ask. Do state the stack defaults and only ask where the product diverges.
3. **Fill each section** using [references/filling-the-template.md](references/filling-the-template.md).
   Keep the defaults unless the product needs otherwise (and record any deviation as an open
   question / future ADR).
4. **Review** with the owner: walk the API surface, schema, and auth model; surface trade-offs
   and open questions explicitly.
5. **Hand off**: the finished doc drives `backend-scaffold` (topology, auth model, integrations),
   `backend-database` (schema), `backend-api-design` (API surface). Seed the project's
   `DECISIONS.md` (via `project-context`) with the key choices.

## What the doc must cover
Problem statement · users & roles · core flows · components · data flow · API surface · database
schema · auth model · caching · background jobs · third-party integrations · error/logging
strategy · scaling · security · deployment topology · open questions. All 16 are in the template.

## Design to the canonical stack
Every design decision defaults to the shared conventions — don't invent alternatives without a
reason:
- Structure, sub-apps, routing → [../_shared-backend/structure.md](../_shared-backend/structure.md),
  [../_shared-backend/routing.md](../_shared-backend/routing.md)
- Auth model choice (persona / RBAC / team+RLS) → [../_shared-backend/auth.md](../_shared-backend/auth.md)
- DB conventions → [../_shared-backend/database.md](../_shared-backend/database.md)
- Response contract, jobs, logging → the matching `../_shared-backend/` files.

If the product needs something the conventions don't cover, call it out in **Open Questions** and
get a decision — then it becomes a DECISION/ADR and, if fleet-wide, a `../_shared-backend/` update.

## Rules
- **Interview before designing.** Don't invent the product. Ask grouped questions; wait for
  answers.
- **No implementation code.** Schemas in the doc are described (columns/relations), not written
  as Python. Endpoints are listed, not stubbed.
- **State trade-offs, not just a pick.** For caching, auth model, tenancy, jobs — give the option
  chosen and what it costs.
- **Every open question is a risk.** List them; unresolved ones block the build.
