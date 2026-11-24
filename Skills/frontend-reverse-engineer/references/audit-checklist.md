# Audit checklist & probes

Concrete greps/reads to quantify the current state. Cite `file:line` for every finding.

## Data layer

- Count client fetch mechanisms: `useQuery(` / `useMutation(` vs deprecated `useApiQuery` /
  `useApi` / `useAsyncData` vs raw `useEffect` + `fetch`. A healthy repo has one (raw TanStack).
- Server actions: do they all return `ActionResult`, or a mix with `ResponseModel {status,...}` /
  raw-throw? Inconsistent envelopes = finding.
- Fetch client: is there one (`apiFetch`/`useFetch`) or several? Do any components call `fetch()`
  directly?
- Error handling: grep `result.detail`, `.message ||`, `catch` blocks that swallow. Does a failed
  request yield a typed `ApiError` with the HTTP status preserved (canonical is `{detail}` — branch
  on status), and are 422 field errors surfaced onto forms rather than flattened to a string?
- Query keys: inline arrays (`useQuery({ queryKey: ['x', id] })`) vs the `queryKeys` factory.
  Collisions or missing params in keys.
- Invalidation: for each mutation, is there a matching `invalidateQueries`? Grep mutations, check
  each `onSuccess`.
- Pagination: how many shapes are consumed? Is there an adapter or is each list bespoke?

## Components & forms

- Page component sizes: flag `page.tsx` > ~250 lines (fetch + transform + orchestration + render
  all in one).
- Forms: RHF + `InputField` family, or raw `<input>` + manual error wiring? Mixed?
- Dialog submit: any `document.getElementById(id).click()` (replace with native `form=""`).
- Duplicated components: same card/table/dialog re-implemented per feature instead of a `ui/`
  extension.
- Prop drilling: trace props through intermediate components that don't use them.

## States & boundaries

- Loading: count distinct patterns (skeleton / spinner / none / bespoke). Pages with no `isError`
  branch. Pages with no empty state.
- `error.tsx` / `not-found.tsx` / error boundary present? (Their absence is common — flag it.)
- Suspense/`loading.tsx` used inconsistently with in-component loading.

## Styling & motion

- Token usage vs raw hex in product code. Dark-mode coverage gaps.
- Motion on the wrong surface (framer in admin tables; nothing where a skeleton is needed).

## Auth

- Token storage (cookies vs localStorage), refresh strategy (proactive vs 401-driven), what
  `middleware.ts` actually gates, role checks and where they live.

## Perf smells

- Re-renders: large context values without memo; inline object/array props to memoized children.
- Waterfalls: sequential `await` of independent server actions in a layout/page (should be
  `Promise.all`).
- Bundle: heavy libs imported into shared layouts; missing dynamic import for editor/chart-heavy
  routes.

## Output of the audit

A convention-adherence table (Followed / Partial / Violated + evidence) and a ranked problem list
feed directly into `references/refactor-plan.md`.
