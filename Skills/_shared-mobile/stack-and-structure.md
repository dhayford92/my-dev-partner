# Mobile Stack & Structure — Canonical (Single Source of Truth)

This folder is the **one place** the conventions for Denzel's React Native / Expo Router stack
are written down. Every skill under `frontend-mobile/` points here instead of restating. Change a
convention **here** and every skill inherits it.

> Extracted from production mobile apps and reconciled with the owner. Where they disagreed, the owner picked one
> canonical variant; the losing variant is marked "❌ not this."
>
> This suite complements `../_shared-web/` (Next.js) and `../_shared-backend/` (FastAPI). Where mobile
> reuses a web-suite convention verbatim (TanStack Query patterns, query-key factory shape), this
> folder **cites** `../_shared-web/` rather than restating it — see
> [data-layer.md](data-layer.md).

## Stack (always)

- **Framework:** Expo SDK ~54, **Expo Router ~6** (file-based), React Native 0.81, **React 19**,
  TypeScript strict.
- **Package manager:** **pnpm**.
- **Styling:** **NativeWind v4** + Tailwind v3, `className`-only — **no `StyleSheet.create`**
  except where NativeWind genuinely can't express a value (e.g. Reanimated `style` props driven by
  shared values). See [states-and-motion.md](states-and-motion.md).
- **State:** React Context (no Zustand/Redux) for auth/notifications/domain state; **TanStack
  Query** for all server data. See [data-layer.md](data-layer.md).
- **Icons:** `react-native-heroicons` only — no other icon libraries, no emoji glyphs for UI.
- **Animation/gesture:** `react-native-reanimated` + `react-native-gesture-handler`, used
  **sparingly** — see [states-and-motion.md](states-and-motion.md).
- **Toasts:** a custom `TosterProvider`/`useToster()` (not a third-party toast lib).

## Canonical decisions at a glance

| Area | Canonical | ❌ Not this |
|------|-----------|-------------|
| Screen architecture | logic lives directly in the `app/` route file | thin route + separate `features/{domain}/` folder |
| Component folders | 3-tier: `components/ui/`, `components/pages/`, `components/custom/` | flat `components/` with no tiering |
| Forms | `react-hook-form` + `zodResolver` + a **`<Controller>`-wrapped** field component | imperative `watch`/`setValue` wiring to a plain controlled input; no validation library at all |
| Token storage | **`expo-secure-store`** | `AsyncStorage` (both reference repos do this — a real gap, not a pattern to keep) |
| Dark mode | **not scaffolded** — light theme only | `useColorScheme` + light/dark token scale |
| Data-layer envelope | actions **throw** a normalized error / **return** data directly (no wrapper) | web's `ActionResult<T> = {data,error}` (that exists for Next.js server-action serialization; mobile has no such boundary) |
| Query-keys export | `export const queryKeys = {...}` (lowercase) | `QueryKeys` (capitalized) |
| Destructive-action errors | pessimistic; **stay signed in / on screen** on API failure | sign the user out locally even when the delete call failed (confirmed bug, not a pattern) |
| EAS Update | explicit `channel` per build profile **and** a manual guarded OTA-check hook | channels with no hook, or a hook with no channels (both reference repos ship only half) |
| List virtualization | plain RN `FlatList` | `@shopify/flash-list` (neither repo uses it) |

## Folder tree

```
app/
├─ (auth)/               # unauthenticated: welcome, phone/email + OTP, complete-account
│  └─ _layout.tsx        # bare <Stack screenOptions={{headerShown:false}}> — no guard logic here
├─ (tabs)/               # authenticated tab group
│  ├─ _layout.tsx        # <Tabs>, safe-area-aware tab bar (useSafeAreaInsets)
│  └─ <tab>/_layout.tsx + index.tsx
├─ (modals-or-secondary-group)/   # e.g. (sub) or (others) — pushed stack screens outside the tabs
├─ _layout.tsx            # root: providers, QueryClientProvider, focusManager wiring, root <Stack>
└─ index.tsx              # THE auth gate — see below
components/
├─ ui/                   # generic primitives: Button, TextField, ButtonSheet, Skeleton, Toster
├─ pages/                # screen-shell wrappers: Screen (SafeAreaView), TopBar/SubHeader
└─ custom/{domain}/       # domain-specific components (optional per-domain subfolders)
services/
├─ actions/{domain}.ts   # plain async functions; call apiFetch; throw or return (see data-layer.md)
├─ models/{domain}.ts    # response TypeScript types (mirror backend response schema)
└─ schemas/{domain}.ts   # zod schemas for request input / form validation
providers/               # AuthProvider, NotificationProvider, domain providers (Currency, Location, ...)
libs/  (or constants/)    # api-urls.ts, query_keys.ts, routes.ts, storage.ts, utils.ts
hooks/                   # apiFetch.ts, registerForPushNotificationsAsync.ts, useOTAUpdates.ts
```

**Path alias:** `@/*` → `./*` (root-relative, no `src/`). Always `@/` imports, never `../../`
climbing. Route screens are `export default function ScreenName() { ... }` with all logic, hooks,
and JSX directly in the file — there is no separate `features/` delegation layer.

## The auth gate — the only guard in the app

`app/index.tsx` is the **sole** place auth state gates navigation:

```tsx
export default function Index() {
  const { isAuthenticated, isHydrated } = useAuth();
  if (!isHydrated) return <SplashLikeScreen />;   // reading AsyncStorage/SecureStore on mount
  return <Redirect href={isAuthenticated ? ROUTES.HOME.ROOT : ROUTES.AUTH.WELCOME} />;
}
```

**Known, confirmed gap (carry forward, don't silently invent a fix):** neither `(auth)/_layout.tsx`
nor `(tabs)/_layout.tsx` has any guard logic — they're bare `<Stack>`/`<Tabs>`. A deep link straight
into a nested authenticated route while logged out is **not** blocked by any layout, only by
whatever that screen does with missing auth-derived data. `mobile-architect` and `mobile-review`
should flag this when relevant; it is documented as the current reality, not fixed by default.

## Config files

- **`app.json`** (static) is canonical over `app.config.ts` (dynamic) **unless** the project
  genuinely needs computed/conditional config — most don't.
- **`eas.json`**: `development`/`preview`/`production` build profiles, each with an explicit
  `channel` matching the profile name. See [native.md](native.md#eas-buildupdate).
- **`babel.config.js`**: `babel-preset-expo` with `jsxImportSource: "nativewind"` + `nativewind/babel`.
- **`metro.config.js`**: `withNativeWind(config, { input: "./global.css" })`.
- **`tsconfig.json`**: extends `expo/tsconfig.base`, `strict: true`, `paths: { "@/*": ["./*"] }`.

## Marketing/thin-feature apps

The reference apps were full product apps (unlike the web suite's marketing-site case). If a future mobile project is genuinely thinner
(e.g. a single-purpose utility app), treat absent product patterns (auth, push, offline) as N/A,
not inconsistency, same principle as the web suite.
