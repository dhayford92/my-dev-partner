# Frontend failure classes — diagnose & fix

For each: how to confirm it, the root cause, the robust fix. Cite `../../_shared-web/` for the canonical shape.

## Stale cache after mutation

- **Confirm:** mutation succeeds (200 in network), UI keeps old data until reload.
- **Cause:** `onSuccess` doesn't `invalidateQueries`, or invalidates a different key than the query
  uses (inline array vs factory; missing `params`).
- **Fix:** invalidate the exact `queryKeys.<domain>.list()` (and `detail(id)`). Route every key
  through the factory so query and invalidation can't drift. For edited detail, invalidate both.

## State desync (two sources of truth)

- **Confirm:** a value shown from `useState` disagrees with the query/context after an update.
- **Cause:** server data copied into `useState` (`const [x, setX] = useState(query.data)`), never
  re-synced.
- **Fix:** don't duplicate server state — read from the query. If you must (draft editing), sync in
  a controlled way and treat the query as source of truth on save/invalidate. For context hydrated
  from server props, `useEffect(() => setX(prop), [prop])` (the `UserTeamProvider` pattern).

## Race condition / out-of-order responses

- **Confirm:** intermittent; fast interactions show wrong/flickering data; slow network hides it.
- **Cause:** async in `useEffect` with no cancellation; typed search firing overlapping requests.
- **Fix:** let TanStack Query own it (keyed by input, it dedupes/cancels); debounce the input and
  include it in the key. For hand-rolled effects, an `AbortController` + ignore-stale flag. For
  optimistic mutations, `cancelQueries` in `onMutate`.

## Effect / render loop

- **Confirm:** infinite re-renders or a request firing repeatedly; CPU spike.
- **Cause:** unstable dependency — a new object/array/function identity each render feeding
  `useEffect`/`useMemo`/a query key, or `setState` unconditionally in render/effect.
- **Fix:** stabilize deps (`useMemo`/`useCallback`, or move constants out of the component); make
  query keys from primitives, not fresh objects; guard `setState` with a change check. Don't
  silence exhaustive-deps — fix the identity.

## Hydration mismatch

- **Confirm:** "Hydration failed / content did not match" warning; flash on load.
- **Cause:** render depends on `Date.now()`, `Math.random()`, `window`, `localStorage`, or a
  client-only branch during SSR.
- **Fix:** move nondeterminism into `useEffect` (post-mount), gate on a mounted flag, or mark the
  subtree client-only. For theme, `suppressHydrationWarning` on `<html>` (already set) + next-themes.

## Wrong value / stale closure

- **Confirm:** handler uses an old value; derived UI doesn't update.
- **Cause:** closure captured stale state; derived value computed once; missing/duplicate list
  `key`.
- **Fix:** use functional `setState(prev => …)`; derive during render (or `useMemo` on real deps);
  give lists stable unique keys (never index when the list reorders).

## Auth: random 401s / redirect loop

- **Confirm:** protected pages bounce to login intermittently, or loop.
- **Cause:** access token expired and refresh not triggered; middleware trusts a token it can't
  decode; cookie flags (`sameSite`/`secure`) blocking the cookie.
- **Fix:** proactive refresh in `getAccessToken` (decode `exp`, refresh if past) + middleware
  refresh on `/portal/*`; verify cookie flags; ensure `apiFetch` attaches the *refreshed* token.
  See `../../_shared-web/api-contract.md#auth--tokens`.

## Unnecessary re-renders (perf)

- **Confirm:** React Profiler shows a subtree re-rendering on unrelated state changes.
- **Cause:** context value is a fresh object each render; inline object/array/callback props to
  memoized children; whole list re-rendered on one row change.
- **Fix:** memoize context value (`useMemo`); stabilize callbacks (`useCallback`); `React.memo`
  rows with stable props; split context so unrelated consumers don't re-render.

## Diagnosis tools quick-ref

- `read_network_requests` → is the payload wrong (data bug) or the render (UI bug)?
- `read_console_messages` → React warnings pinpoint keys, hydration, act, deps.
- Add a temporary `console.count("render <Cmp>")` to confirm a render/loop hypothesis, then remove.
