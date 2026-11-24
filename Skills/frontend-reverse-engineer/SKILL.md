---
name: frontend-reverse-engineer
description: Map an existing frontend's real architecture as it was actually built, trace prop and data flow through the component tree, identify problem areas (prop drilling, inconsistent loading/error states, duplicated fetch logic, component bloat, cache misuse) ranked by risk, and produce a staged refactor plan with production-grade replacement code. Use when inheriting or auditing an unfamiliar frontend, before a big refactor, or when a codebase has drifted from convention. Always separates what IS from what SHOULD BE — it never pretends the current state is the intended one.
---

# frontend-reverse-engineer

Reconstruct what a frontend actually does — not what its README claims — then chart the path to
what it should be. Convention baseline for "should be" is
[`../_shared-web/`](../_shared-web/README.md); deviations from it are findings, not new normal.

## Golden rule

**Separate "what IS" from "what SHOULD BE" in every artifact.** Never launder the current state
into the recommendation. If a page fetches three ways, say so plainly before proposing one.

## Phase 1 — Map what IS (read before concluding)

Read broadly; don't sample. Produce:

1. **Stack & structure actual** — framework, deps (compare `package.json` to the canonical set),
   folder layout, where the data layer really lives, route groups.
2. **Route map** — every route, its group, layout, protection (read `middleware.ts` — what does it
   *actually* gate?).
3. **Data flow trace** — for the main flows, follow one request end to end: component →
   hook/action → fetch client → backend, and back. Note the envelope handling actually used.
4. **Component tree + prop/data flow** — for the heaviest pages, draw the tree and annotate what
   props/callbacks pass through each level and where state lives. Mark pass-through props that
   nothing at the intermediate level uses (prop drilling).
5. **Convention adherence table** — for each `../_shared-web/` convention: Followed / Partial /
   Violated, with file evidence.

Use `Grep`/`Glob` to quantify: how many `useQuery` vs custom-hook call sites, how many distinct
loading patterns, how many places re-implement a fetch. Cite `file:line`.

## Phase 2 — Identify problem areas (ranked by risk)

Rank by **risk = impact × likelihood-of-causing-a-bug**, not by how ugly it is. For each: the
problem, where it occurs (all sites, not one), why it's risky, and the blast radius. The recurring
categories in this stack:

| Category | What to look for |
|----------|------------------|
| Duplicated fetch logic | same endpoint fetched via different mechanisms; hand-rolled fetch beside server actions |
| Inconsistent data layer | mix of raw `useQuery`, deprecated `useApi`/`useAsyncData`, and ad-hoc `useEffect` fetches |
| Inconsistent loading/error | some pages skeleton, some spinner, some nothing; missing `isError` handling |
| Error contract gaps | bare `Error` throws instead of a typed `ApiError`; HTTP status not preserved; 422 field errors dropped (canonical is `{detail}` — branch on status) |
| Prop drilling | data threaded >2 levels; candidates for context/composition |
| Component bloat | 300+ line page components doing fetch + transform + render + dialog orchestration |
| Cache misuse | inline query keys, missing invalidation, stale-after-mutation, key collisions |
| Missing boundaries | no `error.tsx`/`not-found.tsx`; unhandled throw surfaces |

Full checklist: [references/audit-checklist.md](references/audit-checklist.md).

## Phase 3 — Staged refactor plan (with real code)

Not a wish list — an ordered plan a developer executes safely.

- **Stages ordered by leverage & safety**: foundational/low-risk first (e.g. centralize the fetch
  client + error normalizer), then per-feature migrations, then cleanup/deletion of dead paths.
- Each stage: what changes, why, the files touched, the **production-grade replacement code**
  (matching `../_shared-web/` conventions), and how to verify the stage didn't regress.
- Keep stages independently shippable. Note which are mechanical vs need judgment.
- Call out risky migrations (auth/refresh, cache-key changes) and how to de-risk them.

Template: [references/refactor-plan.md](references/refactor-plan.md).

## Working rules

- **Evidence or it didn't happen** — every claim about the current state cites `file:line`.
- **Don't invent intent.** If you can't tell why something was built a way, say "unclear intent"
  and ask, rather than assuming incompetence or genius.
- **Match the target to the owner's conventions**, not generic best practice. The refactor moves
  the code toward `../_shared-web/`, not toward your preferences.
- Distinguish **must-fix** (bug risk) from **should-fix** (consistency) from **nice-to-have**.
- This skill **plans and writes replacement code**; it doesn't silently apply a sweeping refactor.
  Land it stage by stage with the owner.
