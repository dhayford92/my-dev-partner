---
name: mobile-native
description: Everything with no web equivalent — push notifications end-to-end (permission, registration, foreground/background handling, tap-routing), biometric auth via expo-local-authentication, device permission requests (camera/location/media) with rationale and denial handling, deep linking, and the EAS Build/Update workflow (build profiles, channels, OTA rollout and rollback, versioning, per-profile env). This is the skill to invoke for anything touching a native capability. Use for push setup, permission flows, biometric unlock, or any EAS/build-profile/OTA-update task. Do not use for screens/forms (mobile-components), data hooks (mobile-data), or bootstrapping a whole project (mobile-scaffold, which already wires the baseline push/EAS scaffold — this skill extends or troubleshoots it).
---

# mobile-native

Native-capability code, generated to the confirmed patterns where they exist and to a clearly
new-but-deliberate design where they don't. Conventions and full evidence in
[`../_shared-mobile/native.md`](../_shared-mobile/native.md) — this skill is the generation procedure on top of
it, plus deeper references for each capability.

## Push notifications

`mobile-scaffold` already wires registration + the two-listener provider. This skill extends that
baseline:

- **New notification type** → add one row to the payload-handling switch (invalidate) **and** the
  routing switch (navigate) in `providers/notification-provider.tsx` — always both, together (see
  `../_shared-mobile/native.md#push-notifications`). Don't add a type that only invalidates or only
  routes; decide both at once, ideally from `mobile-architect`'s push-notification-strategy table.
- **Permission denial UX** — replace the scaffold's bare early-return with an in-app message +
  `Linking.openSettings()` action. Never a bare `alert()` (confirmed anti-pattern in both
  reference apps — fix it, don't reproduce it).
- **Cold-start tap** — `Notifications.getLastNotificationResponseAsync()` on launch (already in
  the scaffold's provider) — don't forget this when troubleshooting "tap routing doesn't work"; the
  live listener only fires for taps while the JS runtime is already running.

Full reference: [references/permissions.md](references/permissions.md#push-notification-permission).

## Device permissions (camera, location, media, notifications)

Confirmed pattern: request at the point of need, no custom "why we need this" pre-screen for
permissions with an obvious in-context reason. **New, going forward:** always handle denial —
neither reference app does today.

```ts
const { status } = await Location.requestForegroundPermissionsAsync();
if (status !== "granted") {
  show({ type: "info", message: "Location is needed to set your delivery address." });
  // offer a button that calls Linking.openSettings() if status === "denied" and can't re-prompt
  return;
}
```

For a **required** permission blocking a core flow, use the confirmed "Gate" pattern — a
full-screen component rendered alongside the root `<Stack>` (not a route) that blocks until
satisfied. Full templates per capability: [references/permissions.md](references/permissions.md).

## Biometric auth (new — neither reference app has this)

Gates access to an **already-authenticated** session; it is not a login method.

```ts
import * as LocalAuthentication from "expo-local-authentication";

export async function tryBiometricUnlock(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  if (!hasHardware || !isEnrolled) return false;
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock with biometrics",
    fallbackLabel: "Use passcode",
  });
  return result.success;
}
```

Default the feature **off**; store the user's opt-in as a plain `AsyncStorage` preference (not
sensitive); check it in `app/index.tsx` (the one auth gate) before rendering the redirect when a
session already exists. Full setup + settings-screen toggle template:
[references/biometrics.md](references/biometrics.md).

## Deep linking

`scheme` in `app.json`; Expo Router's file-based linking handles the routing itself
(`experiments.typedRoutes: true`). `WebBrowser.maybeCompleteAuthSession()` at the root layout
(already in the scaffold) is required for any OAuth-callback deep link. Remember: a deep link into
a nested authenticated route is **not** blocked by any layout guard (see
`../_shared-mobile/stack-and-structure.md#the-auth-gate--the-only-guard-in-the-app`) — if a specific deep
link target is sensitive, that screen itself must check `useAuth().isAuthenticated` and redirect,
since the framework won't do it for you.

## EAS Build & Update

Full reference: [references/eas-workflow.md](references/eas-workflow.md). Covers: build profiles +
mandatory channels, the manual guarded OTA-update hook (already scaffolded), per-profile env vars
for the API base URL, versioning (`runtimeVersion: {policy:"appVersion"}`, `autoIncrement` on
production), and the rollback runbook (there is no in-app rollback — it's an EAS-dashboard/CLI
operation, documented as a runbook step, not code).

## Verify

Native capabilities mostly can't be verified in a simulator/Expo Go alone (push tokens need a
physical device; biometrics need real hardware or a simulator with biometrics configured). Be
explicit about what you verified vs. what needs a physical device / EAS build — don't claim a push
flow works from Expo Go logs alone if the token fetch was skipped because `Device.isDevice` was
false.

## Anti-patterns (do not generate)

- Bare `alert()` for any permission-denied case.
- A notification type that invalidates a query but has no routing case (or vice versa).
- Biometric auth as a login *replacement* rather than a session-unlock gate.
- An `eas.json` build profile without an explicit `channel`.
- A hardcoded API base URL literal instead of `process.env.EXPO_PUBLIC_API_BASE_URL`.
