# Decisions (ADR log) — {{PROJECT_NAME}}

> Architecture Decision Records. Append a new entry whenever a non-obvious choice is made
> (or reversed). Newest first. Never rewrite history — supersede with a new entry.

<!-- Template for each entry:

## ADR-NNN: <short title>
- **Date:** YYYY-MM-DD
- **Status:** accepted | superseded by ADR-XXX | deprecated
- **Context:** what forced a decision.
- **Decision:** what we chose.
- **Alternatives:** what we rejected and why.
- **Consequences:** trade-offs / follow-ups.
-->

## ADR-001: Adopt canonical backend conventions
- **Date:** {{DATE}}
- **Status:** accepted
- **Context:** New project on the standard FastAPI + Tortoise stack.
- **Decision:** Follow the shared conventions (config, routing, auth, response contract,
  logging) as-is.
- **Alternatives:** Per-project variations — rejected to keep the fleet consistent.
- **Consequences:** Changes to conventions happen in the shared reference, not per project.
