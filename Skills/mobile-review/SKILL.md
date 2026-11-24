---
name: mobile-review
description: Pre-commit review of mobile (Expo/React Native) changes for correctness, convention adherence, performance (list virtualization, image optimization, re-render cost), permission usage and denial handling, offline-state coverage, bundle size, and EAS build/config sanity. Use before committing or opening a PR on any mobile change, or when asked to review a diff/branch. Groups findings blocking / should-fix / nitpick, each with file:line and a concrete fix. Treats tests as out of scope (mirrors the web suite's stance). Not for writing the code (mobile-components/mobile-data) or deep architecture audits (mobile-reverse-engineer).
---

# mobile-review

Catch what matters before it ships. Baseline conventions: [`../_shared-mobile/`](../_shared-mobile/README.md).
Review **the diff** and its immediate blast radius, not the whole repo — that's
`mobile-reverse-engineer`.

## Scope

- **In:** correctness, conventions, performance, permission/offline coverage, backend-contract
  consistency, EAS/build config sanity, token-storage security.
- **Out:** tests (owner's call — do not flag missing tests, mirrors the web suite's stance), pure
  style already enforced by ESLint/Prettier.

## What to check (grouped by output bucket)

### Correctness (usually blocking)

- Every mutation's `onSuccess` invalidates the right query key(s); a destructive action's
  `onError` does **not** sign the user out or navigate away as if it succeeded (the confirmed bug
  class from Phase 0 — treat any recurrence as blocking).
- Service actions throw-or-return directly — no `ActionResult`-style wrapper creeping in from web
  habits.
- Tokens read/written through `TokenStorage` (`expo-secure-store`), never `AsyncStorage` directly.
- `getAccessToken()`'s expiry math uses an absolute stored timestamp, not a relative one re-derived
  incorrectly on each check.
- `QueryClient` is a module-level singleton, never created inline in JSX.
- The root layout's `AppState`→`focusManager` wiring is present and unconditional.

### Conventions (blocking if it breaks the pattern, else should-fix)

- 3-tier component placement (`ui`/`pages`/`custom`); logic stays in the route file (no stray
  `features/` delegation layer reintroduced).
- Forms use `<Controller>`-wrapped fields + `zodResolver` — not manual `useState` validation.
- `ButtonSheet` for confirmation/modal UX — not `Alert.alert`.
- `queryKeys` (lowercase) factory used for every key — no inline arrays, no `QueryKeys` renaming.
- No dark-mode branching (`useColorScheme`) unless the project has explicitly opted in.

### Performance (should-fix; blocking if it causes visible jank)

- `FlatList` `renderItem`/`keyExtractor` are stable references, not recreated inline every render.
- Context values are memoized (`useMemo`) — check any new/changed provider.
- Reanimated `entering`/`exiting` isn't applied per-row on a long, scrollable `FlatList`.
- Images sized appropriately (`expo-image` with a `contentFit`/explicit size) — not full-resolution
  assets rendered at thumbnail size.
- No heavy library (maps, charts, editors) imported into the root layout when only one screen
  needs it.

### Permission & offline coverage (should-fix; blocking if a path crashes/hangs)

- Every permission request has a denial branch — no bare `alert()`; ideally an in-app message +
  `Linking.openSettings()`.
- A required-permission flow uses the "Gate" overlay pattern, not a route the user could
  navigate around.
- Network failures show a clear, actionable error (not a generic crash or an infinite spinner).

### EAS / build config (should-fix)

- Every `eas.json` build profile has an explicit `channel`.
- API base URL comes from `process.env.EXPO_PUBLIC_API_BASE_URL`, not a hardcoded literal.
- `app.json`/`app.config.ts` — static unless the project genuinely needs computed config.

### Backend-contract consistency (should-fix, blocking on breakage)

- Request/response field names snake_case, matching the endpoint.
- `apiFetch`'s error normalizer handles the backend's real `{detail}` shape (string or 422 array)
  — no assumption of a different envelope.

Full checklist: [references/review-checklist.md](references/review-checklist.md).

## Output format

Group findings, ordered by severity within each group. Every finding: `file:line`, what's wrong,
why it matters, and a concrete fix.

```
## Blocking
- app/(others)/more/delete-account.tsx:58 — onError still calls signOut() and navigates to
  welcome, treating a failed delete as successful. Remove the signOut/navigate from onError;
  show the toast and stay on screen (see mobile-data/references/destructive-actions.md).

## Should-fix
- providers/notification-provider.tsx:71 — response listener invalidates queries but never routes
  anywhere for `type: "request_status_update"`. Add the routing case alongside the invalidation.

## Nitpick
- libs/query_keys.ts:14 — inline `["recipients", "list"]` used directly in one screen instead of
  `queryKeys.recipients.list()`.
```

If nothing is blocking, say so. Don't manufacture findings or pad nitpicks.

## Verify claims

For a runtime claim ("this crashes", "this doesn't refetch"), confirm by reading the surrounding
code path fully rather than asserting from a partial read. Mark genuinely uncertain findings as
"likely" and say what would confirm them (usually: run it on-device).
