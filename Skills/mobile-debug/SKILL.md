---
name: mobile-debug
description: Debug a mobile (Expo/React Native) bug to its true causal origin — establish what the screen/hook actually does, distinguish a JS-layer bug from a native crash, account for Expo Go vs dev-build vs production-build behavioral differences, trace platform-specific (iOS-only/Android-only) bugs, catch stale state from hot reload masking the real bug, trace on-device performance/memory issues, explain why causally, enumerate every other place the same bug pattern likely hides, propose the most robust fix with trade-offs stated, and never claim a fix works without an on-device verification step. Use for any misbehaving screen, native crash, or platform-specific bug. Not for adding features (mobile-components/mobile-data) or broad audits (mobile-reverse-engineer).
---

# mobile-debug

Same discipline as `frontend-debug`/`backend-debug`, applied to Expo/React Native. **Find the true
cause, don't pattern-match a symptom.** Convention baseline: [`../_shared-mobile/`](../_shared-mobile/README.md).

## The method (do not skip steps)

### 1. Establish what the code ACTUALLY does

Read the screen/hook/native module involved before theorizing. State the real behavior in one
paragraph: props/state in, effects, what renders/fires when. Don't trust file names or comments.

### 2. Reproduce & observe — with the right runtime

**First question: which runtime is this bug in?**

| Runtime | What it tells you |
|---------|---------------------|
| Expo Go | JS-only bugs; **cannot** reproduce anything needing a native module not in the Expo Go client (most custom native code, some `expo-notifications` behavior) |
| Development build | Full native module support; closest to production for JS+native behavior, but `__DEV__` is true (different bundling, no code-signing/OTA behavior) |
| Production build (TestFlight/internal track/store) | Real bundling, real OTA-update behavior, real push-token environment (dev vs. prod APNs/FCM certs differ) |

A bug that "only happens in production" is common and real — don't dismiss a report because you
can't repro it in Expo Go; check whether the feature even exists there first (push tokens, some
native config, EAS Update behavior are all production-runtime-dependent).

Observe with real tools: Metro/console logs, `adb logcat` (Android native crashes), Xcode device
console (iOS native crashes), React DevTools for render/prop inspection. A JS error shows a
red-screen with a stack trace; a **native crash** kills the app with no JS stack — that alone
tells you which layer the bug is in.

### 3. Trace to true origin

Follow the causal chain backward. Common mobile-specific root causes (with their tells):

| Class | Tells | Usual root cause |
|-------|-------|-------------------|
| Stale cache after mutation | UI shows old data after a create/delete | missing `invalidateQueries`; wrong/inline query key |
| Foreground-refetch not firing | data stays stale after backgrounding/returning | the `AppState`→`focusManager` wiring is missing or was removed from the root layout |
| Token/session desync | random logouts, 401s right after a working session | `getAccessToken()`'s proactive-expiry math wrong (off-by-timezone, `expires_in` stored as delta instead of absolute); refresh called with an undefined token |
| Native crash (no JS stack) | app closes instantly, `adb logcat`/Xcode console shows a native exception | a native module misconfigured (missing Info.plist key, missing Android permission, a config plugin not applied — often needs a full rebuild, not just a JS reload) |
| Expo Go vs. dev/prod-build divergence | "works on my machine" (Expo Go) but not for the tester (TestFlight) | a native capability Expo Go doesn't support, or an env var that differs by build profile |
| Hot-reload stale state | a fixed bug "still happens" after editing the file | Fast Refresh preserved component state across the edit; force a full reload (shake menu → Reload, or `r` in the Metro terminal) before concluding the fix didn't work |
| Platform-specific bug | works on iOS, breaks on Android (or vice versa) | a `Platform.OS` branch missing; `KeyboardAvoidingView behavior` needs to differ; Android's back button not handled; safe-area insets differ |
| Re-render / perf | screen janks on scroll, or a context update re-renders everything | unmemoized context value; `FlatList` `renderItem` recreated inline every render; Reanimated `entering` on every row of a long list |
| Memory / OOM | app gets killed after extended use, especially with images/lists | large images not resized (`expo-image` without a `contentFit`/size hint), an unbounded `FlatList` without `windowSize` tuning, a listener/subscription never cleaned up in a `useEffect` return |

Name the class, then point to the exact line that's the origin — not where it surfaces.

### 4. Explain WHY (causally)

State the mechanism precisely: "the `AppState` listener was removed from `app/_layout.tsx` when X
was refactored → `focusManager.setFocused` never fires → TanStack Query never treats a foreground
return as a refetch trigger → the screen shows data from before backgrounding." If you can't state
the mechanism, you haven't found the cause yet.

### 5. Enumerate other occurrences

Grep for the same pattern elsewhere (other missing `invalidateQueries`, other unmemoized context
providers, other screens with the same `Platform.OS` gap). Fixing one occurrence and leaving five
is a failure.

### 6. Propose the most robust fix + trade-offs

Prefer removing the class of bug over patching the one instance. State trade-offs honestly (e.g.
"moving tokens to SecureStore fixes the desync risk but needs a migration path for existing
sessions — see mobile-reverse-engineer's stage template"). Present a quick patch vs. the correct
fix when they differ, and recommend one.

### 7. Verify — on-device, never claim it from a type-check alone

Reproduce the original repro **on the runtime it actually happens in** (Expo Go/dev-build/
production, whichever is relevant) and confirm the symptom is gone with no new console/native-log
errors. If you can't access the right runtime (e.g. no physical device for a push-token bug), say
so explicitly and state what verification is pending.

## Anti-patterns

- Declaring a fix works after only a Metro/JS reload when the bug was native-layer (needs a full
  rebuild).
- "Try this and see" without a stated root-cause mechanism.
- Fixing the one reported screen and skipping step 5.
- Assuming a bug is JS-layer because it's easier to check, without first looking at whether a
  native crash log exists.

## Reference

Symptom→cause playbook with diagnosis snippets: [references/failure-classes.md](references/failure-classes.md).
