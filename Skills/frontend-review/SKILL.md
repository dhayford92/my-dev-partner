---
name: frontend-review
description: Pre-commit review of frontend changes for correctness, convention adherence, accessibility, performance (unnecessary re-renders, bundle size, waterfall fetches), loading/error/empty-state coverage, and consistency with the backend API contract. Use before committing or opening a PR on any frontend change, or when asked to review a diff/branch. Groups findings blocking / should-fix / nitpick, each with file:line and a concrete fix. Treats tests as out of scope. Not for writing the code (frontend-components/frontend-data) or deep architecture audits (frontend-reverse-engineer).
---

# frontend-review

Catch what matters before it ships. Baseline conventions: [`../_shared-web/`](../_shared-web/README.md).
Review **the diff** (and its immediate blast radius), not the whole repo — that's
`frontend-reverse-engineer`.

## Scope

- **In:** correctness, conventions, a11y, performance, loading/error/empty coverage, backend-
  contract consistency, security hygiene (token/PII handling in client code).
- **Out:** tests (owner's call — do not flag missing tests), and pure style ESLint/Prettier
  already enforces.

## What to check (grouped by the output buckets)

### Correctness (usually blocking)

- Mutations: does every success `invalidateQueries` the right key? Is `result.error` checked
  before the success path? 422 mapped to field errors?
- Query keys from the factory (not inline); keys include all params they depend on.
- Server actions: `"use server"` present; `ActionResult` returned (or unwrap-or-throw for query
  actions) — no stray `ResponseModel`.
- No stale closures, missing list `key`s, unstable effect deps, or unguarded races (see
  `frontend-debug`).
- Auth: token attached via `apiFetch({autoAuth})`; no token in URL/query; refresh path intact.

### Conventions (blocking if it breaks the pattern, else should-fix)

- 3-tier component placement; `InputField` family used (no raw `<input>` + manual errors).
- Native `form=""` dialog submit (no `getElementById().click()`).
- No deprecated `useApi`/`useApiQuery`/`useAsyncData`.
- `@/` imports only; `cn()` for class merging; tokens over raw hex in product code.
- Errors consumed via normalized `ApiError`/`getErrorMessage`, not `result.detail`.

### Loading / error / empty coverage (should-fix, blocking if a path crashes)

- Every query renders `isLoading` (skeleton/spinner per context) AND `isError` (`ErrorState` +
  retry) AND empty (`EmptyState`). A query with no error branch is a finding.
- Skeleton matches the loaded layout (no shift). Mutations show pending/disabled state.

### Accessibility (should-fix)

- Inputs have labels (via `InputField`); `aria-invalid` on error; buttons have text or
  `sr-only`; icon-only buttons labeled.
- Dialogs use the shadcn primitives (focus trap/escape handled); destructive actions confirmed.
- Interactive elements are real `<button>`/`<a>` (not clickable `<div>`); keyboard reachable;
  visible focus. Images have `alt`.

### Performance (should-fix; blocking if it causes a visible waterfall/jank)

- Unnecessary re-renders: unmemoized context values, inline object/array/callback props to
  memoized children, whole-list re-render on one row change.
- Waterfalls: independent server actions `await`ed sequentially in a layout/page → `Promise.all`.
- Bundle: heavy libs (editor, charts) imported into shared layouts instead of `dynamic()`;
  `"use client"` on components that could stay server components.
- Missing `placeholderData: keepPreviousData` on paginated lists that flicker.

### Backend-contract consistency (should-fix, blocking on breakage)

- Request/response field names snake_case, matching the endpoint. Response types in `lib/models`
  match what the API returns. Pagination read via the adapter (handles the divergent shapes).
- Error handling doesn't assume one envelope — uses the normalizer.

Full checklist: [references/review-checklist.md](references/review-checklist.md).

## Output format

Group findings and order by severity within each group. Every finding: `file:line`, what's wrong,
why it matters, and a concrete fix (code where useful).

```
## Blocking
- app/portal/projects/page.tsx:58 — delete mutation never invalidates projects.list(); UI shows
  the deleted row until reload. Add `await qc.invalidateQueries({ queryKey: queryKeys.projects.list() })` in onSuccess.

## Should-fix
- components/custom/reports/report-card.tsx:22 — query has no isError branch; an API failure
  renders a blank card. Add <ErrorState … retry>.

## Nitpick
- lib/actions/team.ts:14 — inline query key `['team', id]`; use queryKeys.teams.detail(id).
```

If nothing is blocking, say so plainly. Don't manufacture findings; don't pad nitpicks.

## Verify claims

For any "this breaks" finding, confirm with a read of the surrounding code (and the preview/network
tools if a runtime claim). Don't assert a runtime bug you haven't traced — mark uncertain ones as
"likely" and say what would confirm.
