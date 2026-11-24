# Pre-commit review checklist

Walk the diff against this. Severity guidance: **blocking** = bug / crash / broken pattern;
**should-fix** = missing coverage / a11y / perf; **nitpick** = consistency polish.

## Data & correctness

- [ ] Every mutation `onSuccess` checks `result.error`, toasts, and `invalidateQueries` the
      correct factory key (+ `detail(id)` on edits, dependent lists on cascades).
- [ ] Query keys come from `queryKeys` and include every dependency (search/page/filters).
- [ ] Query actions unwrap-or-throw; mutation actions return `ActionResult`. No `ResponseModel`.
- [ ] `apiFetch({ autoAuth: true })` for authed calls; no direct `fetch()` in components.
- [ ] Errors read via `getErrorMessage`/`ApiError` (code, fieldErrors) — not `result.detail`.
- [ ] 422 → `form.setError` per `ApiError.fieldErrors`.
- [ ] No stale closures / missing list keys / unstable effect deps / unguarded async races.

## Components & forms

- [ ] Right tier: primitive vs `ui/` extension vs `custom/{domain}`. No forked shadcn files.
- [ ] Forms: RHF + `zodResolver` + `InputField` family; schema in `lib/schemas/{domain}`; snake_case.
- [ ] Dialog submit uses native `form="<id>"`.
- [ ] Loading: submit label swap + `disabled` on button and fields.
- [ ] No deprecated `useApi`/`useApiQuery`/`useAsyncData`.

## States

- [ ] Each query handles `isLoading` (context-appropriate), `isError` (retry), and empty.
- [ ] Skeletons mirror final layout (no shift). 404 detail → `NotFoundState`.
- [ ] Route has/inherits `error.tsx` + `not-found.tsx`; risky client subtrees wrapped in a boundary.

## Accessibility

- [ ] Labels on inputs; `aria-invalid` on error; icon-only buttons have `sr-only` text.
- [ ] Real `<button>`/`<a>` for interactions; keyboard reachable; visible focus.
- [ ] Images `alt`; color not the only status signal; dialogs use shadcn (focus trap).

## Performance

- [ ] Context values memoized; no inline object/array/callback props to memoized children.
- [ ] Independent server actions parallelized (`Promise.all`), not awaited in series.
- [ ] Heavy libs `dynamic()`-imported off shared layouts; server components stay server where possible.
- [ ] Paginated lists use `keepPreviousData`.

## Backend contract

- [ ] Field names snake_case, match the endpoint; `lib/models` type matches the real response.
- [ ] Pagination via `toPaginated`; error handling via the normalizer (no single-envelope assumption).
- [ ] Base URL from env; cookie names namespaced; no token/PII in URLs or logs.

## Styling

- [ ] Tokens over raw hex in product code; dark mode covered; `cn()` for conditional classes.
- [ ] Motion on the right surface (no framer in admin tables; skeletons where data loads).

## Out of scope (do not flag)

- Missing tests. Formatting/lint already enforced by ESLint/Prettier.
