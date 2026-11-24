# Pre-commit review checklist (mobile)

Walk the diff against this. Severity guidance: **blocking** = bug/crash/security issue/broken
pattern; **should-fix** = missing coverage/perf/EAS hygiene; **nitpick** = consistency polish.

## Correctness & data layer

- [ ] Every mutation's `onSuccess` invalidates the correct `queryKeys` target(s) (+ `detail(id)` on
      edits, dependent domains on cascades).
- [ ] Destructive action's `onError` does not sign out / navigate / show false success.
- [ ] Actions throw-or-return directly — no `ActionResult`/`{status,message,data}` wrapper.
- [ ] Tokens go through `TokenStorage` (`expo-secure-store`) — never `AsyncStorage` directly for
      `access_token`/`refresh_token`.
- [ ] `clearAuthData()`/logout removes only auth-specific keys, not a blanket storage wipe.
- [ ] `refreshAccessToken()` returns early if no refresh token is present (doesn't call the
      endpoint with `undefined`).
- [ ] `QueryClient` is a module-level singleton.
- [ ] Root layout's `AppState`→`focusManager` wiring present and unconditional.

## Components & forms

- [ ] 3-tier placement (`ui`/`pages`/`custom`); no reintroduced `features/` delegation layer.
- [ ] Forms: `<Controller>`-wrapped fields + `zodResolver`; snake_case field names matching the API.
- [ ] `ButtonSheet` for confirm/modal UX — not `Alert.alert`.
- [ ] Keyboard handling present (`KeyboardAvoidingView` + `keyboardShouldPersistTaps="handled"`)
      on any screen with text input.

## Native capabilities

- [ ] New/changed notification type has both an invalidation case AND a routing case.
- [ ] Permission denial has a real UX path (message + settings deep-link) — no bare `alert()`.
- [ ] A required-permission flow uses the Gate overlay pattern, not a skippable route.
- [ ] Biometric auth (if present) gates re-entry only — never replaces the actual login flow.

## Performance

- [ ] `FlatList` `renderItem`/`keyExtractor` stable, not recreated inline.
- [ ] Context `value` memoized with `useMemo`.
- [ ] No Reanimated `entering`/`exiting` per-row on a long virtualized list.
- [ ] Images sized/`contentFit` set — not full-res assets at thumbnail display size.
- [ ] Heavy libraries scoped to the screen that needs them, not the root layout.

## EAS / build

- [ ] Every `eas.json` profile has an explicit `channel`.
- [ ] API base URL from `process.env.EXPO_PUBLIC_API_BASE_URL`, not a literal.
- [ ] `runtimeVersion.policy` set; `autoIncrement` on the production profile.

## Backend contract

- [ ] snake_case fields matching the endpoint; response type in `services/models` matches reality.
- [ ] `apiFetch`'s error normalizer handles the real `{detail}` shape (string or 422 array) — no
      single-envelope assumption baked into a screen instead of the shared client.

## Styling

- [ ] `className` (NativeWind) preferred; `StyleSheet.create` reserved for Reanimated-driven
      `style` props NativeWind can't express.
- [ ] No `useColorScheme`/dark-mode branching unless the project has explicitly opted in.

## Out of scope (do not flag)

- Missing tests. Formatting/lint already enforced by ESLint.
