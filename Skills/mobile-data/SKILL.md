---
name: mobile-data
description: Generate the mobile data layer — service actions, TanStack Query hooks, response types/zod schemas, and destructive-action flows — matching Denzel's conventions exactly and staying drop-in compatible with the backend response contract. Covers the throw-or-return action pattern (no ActionResult wrapper on mobile), query-key factory usage, expo-secure-store token handling, foreground-refetch wiring, loading/error/empty handling, and the full delete/deactivate pattern (ButtonSheet confirm, haptics, pessimistic update, stay-signed-in-on-failure, cache invalidation). Use whenever adding an endpoint integration, a data hook, or a delete/remove flow on mobile. Do not use for the screen/component UI (mobile-components) or bootstrapping (mobile-scaffold).
---

# mobile-data

Generate the mobile data layer so every hook and delete flow is indistinguishable from the
reference codebases and correct against the backend contract. The pipeline and rationale are in
[`../_shared-mobile/data-layer.md`](../_shared-mobile/data-layer.md) — this skill is the generation procedure on
top of it. Mobile **reuses** the web suite's TanStack Query philosophy directly; see
[`../_shared-web/data-layer.md`](../_shared-web/data-layer.md) for the
parts that transfer unchanged (query-key factory shape, raw `useQuery`/`useMutation`, no custom
wrapper hook).

## The pipeline (never deviate)

```
apiFetch (Bearer via expo-secure-store, normalized errors)  →  services/actions/{domain}.ts (throws or returns T)  →  raw useQuery/useMutation + queryKeys
```

- **No `ActionResult<T>` wrapper.** That envelope exists on web for Next.js server-action
  serialization; mobile has no such boundary. Every action throws a normalized `ApiError` on
  failure and returns the typed response on success — for **both** query and mutation actions,
  uniformly (unlike web, there's no query-vs-mutation return-shape distinction to remember).
- **No custom data-fetching wrapper hook.** Raw `useQuery`/`useMutation` directly, exactly as both
  reference apps already do.

## Adding an endpoint integration

1. **Endpoint constant** in `libs/api-urls.ts` (right mount: users/core/utils), grouped by domain.
2. **Response type** in `services/models/{domain}.ts` — mirrors the backend response schema,
   snake_case.
3. **Zod schema** (request input / form validation) in `services/schemas/{domain}.ts`.
4. **Service action** in `services/actions/{domain}.ts` — plain async function, calls
   `apiFetch({autoAuth:true})`, throws or returns directly (no wrapper).
5. **Consume** with `useQuery`/`useMutation` + `queryKeys` in the screen.

Full templates: [references/data-hooks.md](references/data-hooks.md).

## Query keys & invalidation

Everything through the `queryKeys` factory (`libs/query_keys.ts`, lowercase export), never inline
arrays. On a successful mutation, `invalidateQueries` the affected `list()` (and `detail(id)` when
editing one). Cascading changes invalidate every dependent domain's `list()`. On sign-out,
`queryClient.clear()` **before** clearing local auth state (confirmed missing in one reference app
— stale cached data from the previous session must not survive into the next login).

## Loading / error / empty

Gate rendering off the query using `components/ui/{skeleton,states}.tsx` (never reinvent per
screen — see `../_shared-mobile/states-and-motion.md`):

```tsx
if (query.isLoading) return <Skeleton className="h-20 w-full" />;
if (query.isError)   return <ErrorState message={getErrorMessage(query.error)} retry={() => query.refetch()} />;
if (data.length === 0) return <EmptyState title="Nothing here yet" />;
```

## Foreground refetch — already wired in the scaffold, don't re-invent per screen

`app/_layout.tsx`'s `AppState`→`focusManager` wiring (see `../_shared-mobile/data-layer.md`) makes
foreground-return refetch work app-wide. Don't add a per-screen `AppState` listener to work around
a query that "doesn't refresh" — check the root layout wiring is present first.

## Destructive actions (delete / deactivate / remove)

**Canonical = `ButtonSheet` confirm + pessimistic + stay-signed-in/on-screen on failure.**
Confirmed in the reference apps' account-deletion flows, and the owner explicitly ruled out the
alternative (signing the user out even when the API call failed is a bug, not a pattern):

1. `ButtonSheet` confirmation (see `mobile-components`) — reason-select or a plain warning message,
   confirm/cancel disabled while pending.
2. `useMutation(deleteAction)` → `onSuccess`: `queryClient.clear()` (or targeted
   `invalidateQueries` for a non-session-ending delete) → toast via `useToster()` → navigate/close.
   `onError`: toast the error, **stay on the current screen / stay signed in** — never treat a
   failed delete as if it succeeded.
3. `isPending` drives the sheet's disabled/label state (`"Deleting..."`).
4. Optional haptic feedback (`selectionFeedback()`) on confirm-tap — sparing, not on every action.

Full template + cascade handling: [references/destructive-actions.md](references/destructive-actions.md).

## Surfacing backend errors correctly

`apiFetch` normalizes the backend's `{detail}` contract (string, or a 422 array of `{loc,msg}`)
into a typed `ApiError` — `status`, and `fieldErrors` for 422s. Consume it:
`show({type:"error", message: getErrorMessage(error)})`; `error.isAuth()` for 401/403 handling;
`error.fieldErrors` mapped onto `form.setError(field, {message})` for validation failures. Never
read `error.detail` directly in screen code — that's `apiFetch`'s job.

## Verify

If a dev build/Expo Go + backend are available: confirm a list loads (skeleton → data), an error
path shows `ErrorState` with a working retry, a create/delete invalidates and the UI updates, and
backgrounding + foregrounding the app refetches a stale query. Report what you actually observed.

## Anti-patterns (do not generate)

- `ActionResult<T>` / `{status,message,data}` envelopes on mobile.
- Signing the user out or treating a delete as successful when the mutation's `onError` fired.
- `Alert.alert` for confirmation instead of `ButtonSheet`.
- A per-screen `AppState` listener duplicating the root layout's foreground-refetch wiring.
- Reading tokens from `AsyncStorage` directly in an action — always through `TokenStorage`
  (`expo-secure-store`).
