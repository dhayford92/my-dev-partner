---
name: frontend-architect
description: Plan a frontend's page and component architecture BEFORE writing code — page inventory, component tree, per-page data requirements, server-cache vs client-state boundaries, route map, and how each page consumes the backend API surface. Use when starting a new feature area or app, when a page is getting complex enough to need a plan, or right after backend-architect has defined the API. Interviews the owner about the product if no project context exists. Writes planning docs only — never implementation code.
---

# frontend-architect

Turn a product requirement into a concrete build plan a developer (or `frontend-components` /
`frontend-data`) can execute without guessing. **No implementation code** — the output is a plan.

Conventions come from [`../_shared-web/`](../_shared-web/README.md). The plan must be expressible in the
canonical structure (route groups, 3-tier components, server-cache-vs-context boundaries) — if it
isn't, that's a signal to rethink the plan, not to invent new structure.

## When to use

- New app or new feature area (e.g. "add a billing section").
- A page has grown past ~2 data sources or ~3 dialogs and needs deliberate decomposition.
- Immediately after `backend-architect` defines endpoints — map the frontend onto them.

Do **not** use to write components/hooks (that's `frontend-components` / `frontend-data`) or to
bootstrap the project (`frontend-scaffold`).

## Inputs — get context first

1. If `.claude/context/ARCHITECTURE.md` / `API.md` exist for this project, read them — they hold
   the product model and the real API surface. (These are maintained by `project-context` once it
   exists; until then, gather the same facts by interview.)
2. If no context, **interview the owner** — grouped, not one at a time:
   - What are the top-level user personas, and which map to `/portal` vs public routes?
   - What are the primary resources (nouns) and their list/detail/create/edit/delete needs?
   - Which data is real-time / streamed vs request-response?
   - What must work offline-optimistically vs must be confirmed server-side?
   - Which backend endpoints exist (paths, auth, pagination) — or is backend not built yet?
3. Never invent endpoints or product rules. If unknown, mark **[ASSUMPTION]** and confirm.

## The plan — produce these six artifacts

Write them to `.claude/context/` if the project uses it, otherwise present in chat. Full
templates in [references/planning-artifacts.md](references/planning-artifacts.md).

1. **Route map** — every route, its group (`(auth)` / `portal` / public / `shared`), protection,
   and layout. Mirrors the backend persona/mount split.
2. **Page inventory** — per page: purpose, route, data sources (which server actions/endpoints),
   mutations, dialogs, empty/error/loading needs.
3. **Component tree** — per page: the 3-tier breakdown (`ui/` primitives reused, `page/`
   composites, `custom/{domain}/` feature components), with parent→child data/callback flow.
   Flag any prop-drilling deeper than ~2 levels as a candidate for context or composition.
4. **Data requirements** — per page: query keys (from the factory), cache/stale expectations,
   invalidation targets on each mutation, and whether a query "unwraps-or-throws" or "returns
   ActionResult". Cite `../_shared-web/data-layer.md`.
5. **State boundaries** — for each piece of state, classify: **server cache** (TanStack Query),
   **global client** (React Context — justify each one; default is *don't*), or **local**
   (`useState`). Cite `../_shared-web/data-layer.md#state-boundaries`.
6. **API consumption map** — table of endpoint → consuming page(s) → request shape → response
   type (the `lib/models` type) → error/pagination handling. This is the contract with the
   backend suite; reference `../_shared-backend/response-contract.md` for envelopes, and note
   where the real backend diverges per `../_shared-web/api-contract.md`.

## Working rules

- **Challenge before planning.** If the requirement implies an over-complex page (5 tabs, 8
  queries), say so and propose a split. Scope creep is flagged here, cheaply, not in code review.
- **Prefer the owner's conventions over generic best practice.** A plan that fights the stack is
  wrong even if textbook-correct.
- **Decisions the owner must make** (route protection model, whether a resource needs optimistic
  UX, whether new global context is justified) are surfaced as questions, not assumed.
- Hand off cleanly: each page in the inventory should be buildable by `frontend-components` +
  `frontend-data` from the plan alone.

## Output contract

The plan feeds `frontend-components` (component tree + forms) and `frontend-data` (data
requirements + API map). Keep names consistent with what those skills will generate: query-key
factory paths, `lib/actions/{domain}` function names, `lib/models/{domain}` type names.
