# First-run verification & troubleshooting

Never claim the scaffold works without walking this. Report what you actually observed.

## Checklist

| # | Step | Expected | Needs backend? |
|---|------|----------|----------------|
| 1 | `npx expo start` | Compiles, no red-screen error; QR scans into Expo Go or a dev build | no |
| 2 | Open the app cold | Branded loading view, then redirect to `(auth)/welcome` | no |
| 3 | Submit the welcome form empty | zod validation error shown under the field | no |
| 4 | Enter a value, submit | `requestOTP` fires; toast shows (success or the real backend error) | yes, for a real result |
| 5 | Log in fully (valid OTP) against a running backend | Lands on `(tabs)/home`; "Backend connection" card shows the `/me` payload | **yes** |
| 6 | Background the app, then foreground it | A stale query on screen refetches (confirms `focusManager` wiring) | yes |
| 7 | Kill and relaunch after logging in | Redirect goes straight to `(tabs)/home` (session restored from SecureStore) | no |

If the backend isn't running, verify 1–3 and 7, and state that 4–6 are pending a live API.

## Verifying in the browser/device (agent)

The preview browser tools don't drive a native app — use `preview_start`/`preview_logs` only to
confirm the Metro bundler itself starts cleanly (no build errors), and ask the user to scan the
QR code on a physical device or simulator for the rest. Do not claim steps 2–7 are verified from
Metro logs alone.

## Common issues

- **`Unable to resolve module nativewind/babel`** — run `npx expo install nativewind tailwindcss`
  again; confirm `babel.config.js` and `metro.config.js` match the scaffold templates exactly.
- **Styles not applying** — `global.css` must be imported in the root layout (`import
  "@/global.css"`) and referenced in `metro.config.js`'s `withNativeWind(config, {input:
  "./global.css"})`.
- **`SecureStore` throws on web** (`expo start --web`) — `expo-secure-store` has no web
  implementation; this stack targets iOS/Android. If web support is genuinely needed, branch
  `TokenStorage` on `Platform.OS === "web"` to fall back to `AsyncStorage` there — don't silently
  swallow the error.
- **Push token fetch fails with "Project ID not found"** — `app.json`'s `extra.eas.projectId` must
  be set (from `eas init` or the Expo dashboard) before `registerForPushNotificationsAsync` works.
- **`focusManager` refetch never fires** — confirm the `AppState` listener is registered in the
  **root** layout (not a nested one) and isn't gated behind any conditional render.
- **Redirect loop on `/`** — `isHydrated` never flips true; check `getAccessToken()` isn't
  throwing before reaching the `finally` block in `AuthProvider`'s hydration effect.

## After first run

- Replace the placeholder logo/colors; the light-only `brandBlue`/`ink` tokens in
  `tailwind.config.js` are neutral placeholders.
- Add real domains: endpoints in `libs/api-urls.ts`, query keys in `libs/query_keys.ts`, actions
  in `services/actions/`, screens via `mobile-components`/`mobile-data`.
- Set real EAS project ID + update URL in `app.json`, and real per-profile URLs in `eas.json`.
