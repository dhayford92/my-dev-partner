# Mobile failure classes — diagnose & fix

For each: how to confirm it, the root cause, the robust fix. Cite `../../_shared-mobile/` for the canonical
shape.

## Stale cache after mutation

- **Confirm:** mutation succeeds (check the network response), UI keeps old data.
- **Cause:** `onSuccess` doesn't `invalidateQueries`, or invalidates a different key than the one
  the query uses (inline array vs. the `queryKeys` factory — a typo'd param drifts the key).
- **Fix:** invalidate the exact `queryKeys.<domain>.list()`/`detail(id)` the screen's `useQuery`
  actually uses. Route every key through the factory so query and invalidation can't drift apart.

## Foreground-refetch silently not working

- **Confirm:** background the app, wait, foreground it — a query that should refetch doesn't.
- **Cause:** the `AppState`→`focusManager.setFocused()` wiring is missing from the root layout (or
  was accidentally removed during a refactor, or duplicated per-screen in a way that conflicts).
- **Fix:** confirm exactly one `AppState` listener exists, in `app/_layout.tsx`, calling
  `focusManager.setFocused(status === "active")` guarded by `Platform.OS !== "web"`. See
  `../../_shared-mobile/data-layer.md`.

## Token/session desync — random logouts or 401s

- **Confirm:** user gets logged out or hits 401 during what should be a valid session.
- **Cause:** `expires_in` stored as a **relative** value instead of an absolute Unix timestamp (or
  computed with the wrong clock/timezone assumption); `refreshAccessToken()` called without first
  checking a refresh token exists, sending `refresh_token: undefined` to the backend.
- **Fix:** store `now_seconds + ttl_seconds` at write time; compare directly against
  `Math.floor(Date.now()/1000)` on read. Return early (`null`) from refresh if no refresh token is
  present. See `../../_shared-mobile/data-layer.md#token-storage`.

## Native crash vs. JS error

- **Confirm:** a JS error shows a red-screen with a component stack in Metro/the app; a **native**
  crash kills the app instantly with nothing in the JS console — check `adb logcat` (Android) or
  the Xcode device console (iOS) for the actual native exception.
- **Cause:** usually a native module misconfigured — a missing `Info.plist`/`AndroidManifest.xml`
  entry a config plugin should have added, a permission not declared, or a native dependency
  version mismatch after an Expo SDK upgrade.
- **Fix:** `npx expo-doctor` to catch version mismatches; confirm the relevant Expo config plugin
  is actually listed in `app.json`'s `plugins` array; a **full native rebuild**
  (`eas build` or `npx expo run:ios`/`run:android`) is required after fixing a native config issue
  — a JS-only reload will not pick it up.

## Expo Go vs. dev-build vs. production-build divergence

- **Confirm:** the bug report says "works for me" (likely Expo Go) but not for a tester (likely a
  TestFlight/internal-track build), or vice versa.
- **Cause:** a capability Expo Go can't run at all (most custom native modules, some push-token
  behavior — `Device.isDevice` and the Expo Go sandboxing both affect this), or an env var that
  correctly differs by EAS build profile but wasn't accounted for when comparing behavior.
- **Fix:** reproduce on the *same* runtime as the report before diagnosing further. Check
  `eas.json`'s `env` per profile if the divergence looks config-shaped rather than code-shaped.

## Hot-reload stale state masking a real fix

- **Confirm:** you fixed the code, but the bug "still happens" in the running app.
- **Cause:** Fast Refresh preserved component state (e.g. a `useState`/context value) across the
  edit — you're looking at old state under new code, not the actual behavior of the fix.
- **Fix:** force a full reload (shake menu → Reload, or `r` in the Metro terminal, or fully kill
  and relaunch) before concluding a fix didn't work. This is the single most common false-negative
  in mobile debugging — check it before going further down a wrong path.

## Platform-specific bug (iOS-only / Android-only)

- **Confirm:** reproduce on both platforms; note exactly where behavior diverges.
- **Cause:** a `Platform.OS` branch that's missing rather than wrong (e.g. `KeyboardAvoidingView`
  `behavior` needs `"padding"` on iOS / `"height"` on Android — using one value for both is a
  common source of a keyboard-covers-the-field bug on one platform only); Android's hardware back
  button not intercepted where a custom sheet/modal needs to handle it; safe-area insets differ
  meaningfully by device (notch vs. no notch, gesture nav vs. button nav on Android).
- **Fix:** branch explicitly on `Platform.OS`, test both, don't assume parity.

## Re-render / perf issues

- **Confirm:** React DevTools Profiler shows a subtree re-rendering on unrelated state changes, or
  scroll jank on a long list.
- **Cause:** a context value that's a fresh object literal every render (no `useMemo`); a
  `FlatList` `renderItem` defined inline (recreated every render, breaks memoization of rows);
  Reanimated `entering`/`exiting` animations applied per-row on a long `FlatList` (fights
  virtualization — the animation itself becomes the perf cost).
- **Fix:** `useMemo` the context value; hoist `renderItem` to a stable reference (or wrap the row
  component in `React.memo`); reserve entrance animations for short, glanceable lists, not
  virtualized long ones.

## Memory / OOM (app killed after extended use)

- **Confirm:** the app is silently killed by the OS after heavy image/list use, more likely on
  older/lower-memory devices.
- **Cause:** full-resolution images rendered at thumbnail size with no resize hint; an unbounded
  in-memory list (e.g. accumulating all pages of an infinite-scroll query without
  windowing/eviction); a subscription (notification listener, `AppState` listener) created without
  a cleanup function in `useEffect`'s return, leaking on every mount/unmount cycle.
- **Fix:** use `expo-image` with an explicit size/`contentFit`; verify every `useEffect` that adds
  a listener also returns a matching removal; consider `FlatList`'s `windowSize`/
  `removeClippedSubviews` for very long lists.

## Diagnosis tools quick-ref

- `adb logcat` (Android) / Xcode device console (iOS) — the only way to see a native crash's real
  stack trace; the JS console shows nothing when the crash is native.
- React DevTools Profiler — confirm a render/re-render hypothesis before "fixing" it.
- `npx expo-doctor` — catches native dependency/config drift after an SDK upgrade.
- Temporarily add `console.count("render <Screen>")` to confirm a render-loop hypothesis, then
  remove it.
