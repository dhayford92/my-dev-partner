---
name: frontend-data
description: Generate the data layer — server actions, query/mutation hooks, response types/zod schemas, and destructive-action flows — matching Denzel's conventions exactly and staying drop-in compatible with the backend response envelope. Covers query-key factory usage, the apiFetch→server-action→raw-TanStack pipeline, the error normalizer + pagination adapter, loading/error/empty handling, and the full delete/deactivate pattern (confirmation UX, pessimistic update, rollback, cache invalidation, cascading UI). Use whenever adding an endpoint integration, a data hook, or a delete/remove flow. Do not use for the component/form UI (frontend-components) or bootstrapping (frontend-scaffold).
---

# frontend-data

Generate the data layer so every hook and delete flow is indistinguishable from the codebase and
correct against the backend contract. The pipeline, envelope, and rationale are in
[`../_shared-web/data-layer.md`](../_shared-web/data-layer.md) and
[`../_shared-web/api-contract.md`](../_shared-web/api-contract.md) — this skill is the generation
procedure on top of them.

## The pipeline (never deviate)

```
apiFetch (Bearer, normalized errors)  →  lib/actions/{domain}.ts ("use server", ActionResult<T>)  →  raw useQuery/useMutation + queryKeys
```

- **No `useApi.ts` / `useApiQuery` / `useAsyncData`.** They are deprecated. Generate raw TanStack.
- Server actions return **`ActionResult<T> = {data,error}`** (canonical). List actions run the
  response through `toPaginated` before returning.

## Adding an endpoint integration

1. **Endpoint constant** in `lib/constants/api-urls.ts` (right mount: users/core/utils), grouped
   by domain, parameterized routes as functions.
2. **Response type** in `lib/models/{domain}.ts` — mirrors the backend response schema, snake_case.
3. **Zod schema** (if it's request input or needs client validation) in `lib/schemas/{domain}.ts`.
4. **Server action** in `lib/actions/{domain}.ts` — `"use server"`, calls `apiFetch({autoAuth:true})`,
   returns `ActionResult` (or unwrap-or-throw for read actions used directly in `useQuery`).
5. **Consume** with `useQuery`/`useMutation` + `queryKeys` in the component.

Full templates: [references/data-hooks.md](references/data-hooks.md).

### Query vs mutation return convention (be consistent)

- Action used in **`useQuery`** → return the **unwrapped data or throw** (so `isLoading`/`isError`
  work, and the query-cache retry policy applies). Errors are `ApiError` from `apiFetch`.
- Action used in **`useMutation`** → return **`ActionResult`**; `onSuccess` checks `result.error`,
  toasts, and invalidates. For 422s, map `ApiError.fieldErrors` back onto the form.

Document which convention each action uses (a one-line comment) so callers don't guess.

## Query keys & invalidation

Everything goes through the `queryKeys` factory (`lib/constants/query-keys.ts`), never inline
arrays. On a successful mutation, `invalidateQueries` the affected `list()` (and `detail(id)` when
you edited one). Cascading deletes invalidate every dependent domain's `list()`.

## Loading / error / empty (from the states kit)

Gate rendering off the query. Use `components/ui/states.tsx` (never reinvent):

```tsx
if (query.isLoading) return <LoadingState variant="skeleton" />;   // or a bespoke *-loading-screen
if (query.isError)   return <ErrorState error={getErrorMessage(query.error)} retry={{ onClick: () => query.refetch() }} />;
if (data.length === 0) return <EmptyState title="Nothing here yet" action={...} />;
```

Which skeleton where: [`../_shared-web/states-and-motion.md`](../_shared-web/states-and-motion.md).

## Destructive actions (delete / deactivate / remove)

**Canonical = pessimistic + confirm + invalidate.** No optimistic updates, no undo (unless the
owner explicitly asks). Pattern:

1. `ConfirmDialog` (destructive variant) — description spells out cascades ("this will also
   delete…"). Confirm + cancel disabled while pending.
2. `useMutation(deleteAction)` → `onSuccess`: check `result.error` → `toast` →
   `invalidateQueries` the list (+ any dependent domains) → close dialog + clear selection.
   `onError` → `toast.error(getErrorMessage(err))`.
3. `isLoading`/`isPending` drives the dialog's disabled/label state.

Full template, cascade handling, and the (opt-in) optimistic + rollback variant:
[references/destructive-actions.md](references/destructive-actions.md).

## Surfacing backend errors correctly

`apiFetch` already normalizes all three real backend error shapes into a typed `ApiError`
(`code`, `status`, `details`, `fieldErrors`) — see `../_shared-web/api-contract.md`. Consume it:
`toast.error(getErrorMessage(err))`, `err.isAuth()` for redirect/refresh, `err.fieldErrors` for
form field errors. Never read `result.detail` directly in feature code.

## Verify

If the dev server + backend are up, exercise the hook: confirm the list loads (skeleton→data),
an error path shows `ErrorState` with retry, a create/delete invalidates and the UI updates, and
a 422 maps to field errors. Use the preview tools; report what you observed.

## Anti-patterns (do not generate)

- `useApi`/`useApiQuery`/`useAsyncData`; `ResponseModel {status,message,data}` envelopes.
- Inline query-key arrays; forgetting to invalidate after a mutation.
- Optimistic delete by default; `createOptimisticUpdate`-style helpers that call `useQueryClient`
  inside callbacks (broken).
- Reading `result.detail || result.message` in feature code — that's `apiFetch`'s job now.
