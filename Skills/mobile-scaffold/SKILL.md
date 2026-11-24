---
name: mobile-scaffold
description: Bootstrap a new Expo Router (React Native) project in Denzel's mobile stack — folder structure, EAS config with per-profile channels, app.json, the auth-gate + tab/stack navigation skeleton, TanStack Query provider with AppState foreground-refetch wiring, expo-secure-store token storage, push-notification registration scaffold, light-theme NativeWind styling, and env-per-EAS-profile base-URL handling. Ships as runnable scripts + asset templates. Must produce a project that boots in Expo Go or a dev build on first run. Use at the very start of any new mobile project, or when adding the standard skeleton (data layer, auth, providers, protected routes) to a bare Expo app.
---

# mobile-scaffold

Stand up a new Expo Router app that **boots and renders a working shell on first run**, wired to
the same backend contract as the web suite. Conventions come from
[`../_shared-mobile/`](../_shared-mobile/README.md) — cite them, don't restate them. The TanStack Query and
query-key conventions are the same ones documented in
[`../_shared-web/data-layer.md`](../_shared-web/data-layer.md); this skill
doesn't reinvent that layer, it adapts it (see `../_shared-mobile/data-layer.md` for exactly what differs).

## When to reach for this

- New Expo Router project in this stack → run the whole thing.
- A bare `create-expo-app` that needs the standard skeleton → run steps 3–6 only.
- Adding one missing piece (e.g. the OTA-update hook) → copy that asset from `assets/`.

Not for planning screen/navigation architecture (`mobile-architect`) or generating feature
screens/hooks (`mobile-components`, `mobile-data`).

## What it produces

```
app.json  eas.json  babel.config.js  metro.config.js  tailwind.config.js  global.css  .env.example
app/{_layout,index}.tsx
app/(auth)/_layout.tsx   app/(tabs)/{_layout.tsx,home/{_layout,index}.tsx}
components/ui/{button,text-field,button-sheet,skeleton,states,toster}.tsx
components/pages/screen.tsx
hooks/{apiFetch,registerForPushNotificationsAsync,useOTAUpdates}.ts
providers/{auth-provider,notification-provider}.tsx
services/actions/auth_actions.ts
libs/{api-urls,query_keys,routes,storage,utils}.ts
```

## Procedure

### 1. Create the Expo app + install deps

```bash
bash scripts/scaffold.sh <project-name>        # macOS/Linux/Git-Bash
pwsh scripts/scaffold.ps1 <project-name>       # Windows PowerShell
```

Runs `npx create-expo-app@latest` (TypeScript template, Expo Router), then installs the
**canonical dependency set**:

```
@tanstack/react-query@^5 nativewind@^4 tailwindcss@^3 tailwind-merge react-hook-form zod
@hookform/resolvers @react-native-async-storage/async-storage expo-secure-store expo-notifications
expo-device expo-constants expo-updates expo-splash-screen expo-status-bar expo-haptics
expo-web-browser react-native-heroicons react-native-safe-area-context react-native-screens
react-native-gesture-handler react-native-reanimated react-native-svg
```

### 2. Config files (assets/)

- `app.json` — static config (canonical default; see `../_shared-mobile/stack-and-structure.md`), scheme,
  `newArchEnabled`, `edgeToEdgeEnabled`, `expo-router`/`expo-splash-screen`/`expo-notifications`
  plugin entries, `runtimeVersion: {policy:"appVersion"}`.
- `eas.json` — **channels per profile are mandatory** (`development`/`preview`/`production`, each
  `channel` matching the profile name) **and** an `env` block per profile feeding
  `EXPO_PUBLIC_API_BASE_URL` — this is the fix for the confirmed hardcoded-URL gap in both
  reference apps. See `../_shared-mobile/native.md#env-across-build-profiles--the-confirmed-gap`.
- `babel.config.js` / `metro.config.js` — NativeWind wiring (`jsxImportSource: "nativewind"`,
  `withNativeWind(config, {input: "./global.css"})`).
- `tailwind.config.js` — light-theme-only tokens (no `darkMode` key — see
  `../_shared-mobile/states-and-motion.md#dark-mode--not-scaffolded-by-default`).
- `.env.example` → copy to `.env` for local dev (`EXPO_PUBLIC_API_BASE_URL=http://localhost:8000`).

### 3. Data layer + storage (assets/)

- `hooks/apiFetch.ts` — the fetch client + error normalizer (mirrors
  `frontend-scaffold/assets/hooks/apiFetch.ts`'s normalizer logic, no cookies).
- `libs/storage.ts` — `TokenStorage` (expo-secure-store, tokens only) + `DataStorage`
  (AsyncStorage, everything else) — see `../_shared-mobile/data-layer.md#token-storage`.
- `libs/api-urls.ts` — reads `process.env.EXPO_PUBLIC_API_BASE_URL`, mirrors the backend's
  `/users`, `/core`, `/utils` mount + `/api/v1/{persona}/` shape.
- `libs/query_keys.ts` — the `queryKeys` factory (lowercase, `all`/`list()`/`detail(id)` shape).
- `libs/utils.ts` — `ApiError`, `getErrorMessage`.
- `services/actions/auth_actions.ts` — throw-or-return actions (no `ActionResult`), proactive
  token-expiry check + refresh, `clearAuthData()` removing only auth keys.

### 4. Providers, shell, root layout

- `providers/auth-provider.tsx` — hydration flag, `useMemo`-ed context value, `queryClient.clear()`
  on sign-out.
- `providers/notification-provider.tsx` — registration + the two listeners, centralized payload
  handler (invalidate + route — see `../_shared-mobile/native.md`).
- `app/_layout.tsx` — module-level `QueryClient`, `AppState`→`focusManager` wiring,
  `WebBrowser.maybeCompleteAuthSession()`, `SplashScreen` handling, `useOTAUpdates()`, root
  `<Stack screenOptions={{headerShown:false}}>`, `<TosterProvider>`.
- `app/index.tsx` — the auth gate (branded loading state while `!isHydrated`, then `<Redirect>`).
- `components/pages/screen.tsx` — `SafeAreaView`-based `Screen`.
- `components/ui/{button,text-field,button-sheet,skeleton,states,toster}.tsx` — the primitives
  from `../_shared-mobile/components-and-forms.md` and `../_shared-mobile/states-and-motion.md`.

### 5. Navigation skeleton

`app/(auth)/_layout.tsx` and `app/(tabs)/_layout.tsx` — bare `<Stack>`/`<Tabs>` (no guard logic —
this matches the confirmed reality; see `../_shared-mobile/stack-and-structure.md#the-auth-gate--the-only-guard-in-the-app`
for the documented gap). One example tab (`home`) with a minimal screen that renders and calls one
real authed query as the smoke test.

### 6. Push notification registration scaffold

`hooks/registerForPushNotificationsAsync.ts` — permission check/request, Android channel setup,
Expo push token fetch. Wired into `NotificationProvider`, which is mounted in the root layout.

## First-run verification (required — never claim success without it)

Full checklist in [references/first-run.md](references/first-run.md). Minimum:

1. `npx expo start` compiles with no red-screen errors; scan into Expo Go or a dev build.
2. `/` (index) renders the branded loading state, then redirects to `(auth)` when logged out.
3. The `(auth)` welcome/login screen renders; a form field shows a validation error on empty submit.
4. Force a valid login (against a running backend) → lands on `(tabs)/home`; the smoke-test query
   renders real data or a clear error state.
5. Background the app and foreground it again → confirm (via a log or React Query devtools) that
   a stale query refetches (proves the `focusManager` wiring works).

Report what you actually observed; if no backend is available, verify 1–3 and 5, and say 4 is
pending a running API.

## Cross-skill contract

Everything generated here is drop-in compatible with the backend's response contract and JWT
model, and reuses the exact `queryKeys`/TanStack conventions from the web suite. Feature screens
from `mobile-components`/`mobile-data` build on exactly these files — don't diverge from the asset
templates; change `../_shared-mobile/` first if a convention needs to change.
