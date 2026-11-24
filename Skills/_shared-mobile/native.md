# Native Capabilities — Canonical (push, permissions, EAS, biometrics, deep links)

Everything here has no web-suite equivalent. Confirmed patterns are cited from both reference
apps; two items (notification-tap routing, biometric auth) are **new ground** — neither reference
app has them, built fresh per owner decision, not extracted.

## Push notifications

### Registration — confirmed near-identical in both apps

```ts
export default async function registerForPushNotificationsAsync() {
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#FF231F7C",
    });
  }
  if (!Device.isDevice) return; // simulators can't get a push token

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;
  if (existing !== "granted") {
    finalStatus = (await Notifications.requestPermissionsAsync()).status;
  }
  if (finalStatus !== "granted") {
    // ❌ confirmed anti-pattern in both apps: bare alert(), no rationale, no settings deep-link.
    // Canonical: show a themed in-app message (toast or inline banner) explaining what's lost
    // (e.g. "You won't get delivery updates") with a button to Linking.openSettings().
    return;
  }

  const projectId = Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
  if (!projectId) throw new Error("Project ID not found");
  return (await Notifications.getExpoPushTokenAsync({ projectId })).data;
}
```

### Provider — context + two listeners, confirmed identical shape

```tsx
Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldPlaySound: true, shouldSetBadge: false, shouldShowBanner: true, shouldShowList: true }),
});

export default function NotificationProvider({ children }: { children: ReactNode }) {
  const [expoPushToken, setExpoPushToken] = useState<string | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    registerForPushNotificationsAsync().then(setExpoPushToken, setError);

    const received = Notifications.addNotificationReceivedListener((n) => {
      handleNotificationPayload(n.request.content.data, queryClient); // invalidate relevant queries
    });
    const responded = Notifications.addNotificationResponseReceivedListener((r) => {
      handleNotificationPayload(r.notification.request.content.data, queryClient);
      routeFromNotification(r.notification.request.content.data); // NEW — see below
    });

    return () => { received.remove(); responded.remove(); };
  }, []);

  return <NotificationContext.Provider value={{ expoPushToken, ... }}>{children}</NotificationContext.Provider>;
}
```

`handleNotificationPayload` — confirmed pattern in both apps: branch on `data.type` (and
`data.user_type` where the backend sends it) to `queryClient.invalidateQueries()` the relevant
domain(s). Centralize this branching in one function per app rather than duplicating the
if/else chain across the received- and response-listeners (both reference apps duplicate it
verbatim between the two listeners — worth collapsing to one function called from both).

### Token registration with the backend — confirmed pattern

On auth hydration, compare the freshly-fetched Expo token against the last one cached in
`AsyncStorage` (`notification_token`); only call the backend action when it changed or wasn't
registered yet:

```ts
const cached = await DataStorage.get("notification_token");
if (expoPushToken && expoPushToken !== cached) {
  await DataStorage.set("notification_token", expoPushToken);
  await sendNotificationTokenAction(expoPushToken);
}
```

### NEW — notification-tap → navigation routing

Neither reference app does this today (`addNotificationResponseReceivedListener` only invalidates
queries). Canonical, newly designed:

```ts
function routeFromNotification(data: Record<string, unknown> | undefined) {
  if (!data?.type) return;
  switch (data.type) {
    case "request_status_update": return router.push(`/(sub)/requests/${data.request_id}`);
    case "transaction": return router.push(`/(others)/transaction-detail?id=${data.transaction_id}`);
    case "auth": return router.push(ROUTES.PROFILE?.ROOT ?? "/(tabs)/profile");
    default: return; // unknown/unhandled type — do nothing rather than guess a route
  }
}
```

Rules: route from `data.type` (+ an id field the backend already sends for that type), never
guess a route for an unrecognized type, and call this **after** the cache-invalidation branch so
the screen you land on already has fresh data queued. Handle the **cold-start** case too —
`Notifications.getLastNotificationResponseAsync()` on app launch, since a tap that launched the
app doesn't fire the listener.

## Permissions — request timing & denial handling

Confirmed pattern in both apps: call the native permission prompt directly at the point of need
(no custom "why we need this" pre-screen). This is fine for permissions with an obvious,
in-context reason (camera icon tapped → camera permission prompt). Denial handling is **not**
implemented in either app today — canonical going forward:

```ts
const { status } = await Location.requestForegroundPermissionsAsync();
if (status !== "granted") {
  // show an inline message + a button that calls Linking.openSettings() — don't just alert() and stop
}
```

For a **required** permission that blocks a core flow (e.g. location for a delivery app), a
full-screen "Gate" component (see stack-and-structure.md) is the confirmed pattern — render it
alongside the root `<Stack>`, not as a route.

## Biometric auth — NEW (neither app has this)

`expo-local-authentication`, gating access to the already-authenticated session (not a login
method — the user still authenticates via OTP/OAuth first; biometrics unlock a session that's
already stored):

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

Gate this behind a user-facing setting (default **off**) rather than forcing it on every app open
— store the preference in `AsyncStorage` (not sensitive), check it in the auth gate
(`app/index.tsx`) before rendering the redirect when the preference is on and the session exists.

## Deep linking

`scheme` set in `app.json`; `WebBrowser.maybeCompleteAuthSession()` called once at the top of the
root layout (needed for OAuth-callback flows — harmless boilerplate even for apps without OAuth,
confirmed present in both). No custom deep-link route handling beyond Expo Router's own
file-based linking config (`experiments.typedRoutes: true` in both apps' configs) — a deep link
into a nested route is subject to the same "no guard at nested layouts" gap noted in
stack-and-structure.md.

## EAS Build & Update

### `eas.json` — channels are mandatory per profile

```json
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal", "channel": "development" },
    "preview": { "distribution": "internal", "channel": "preview" },
    "production": { "autoIncrement": true, "channel": "production" }
  }
}
```

Without an explicit `channel`, EAS Update can't target a build profile distinctly — confirmed gap
in one reference app (it ships OTA updates with no channel mapping at all).

### OTA updates — the manual guarded hook (canonical, confirmed in the more mature app)

```ts
export function useOTAUpdates() {
  const isRunning = useRef(false);
  const checkAndApply = useCallback(async () => {
    if (!Updates.isEnabled || __DEV__) return;   // no-ops in dev / Expo Go
    if (isRunning.current) return;
    isRunning.current = true;
    try {
      const result = await Updates.checkForUpdateAsync();
      if (result.isAvailable) {
        await Updates.fetchUpdateAsync();
        await Updates.reloadAsync();
      }
    } catch {
      /* network hiccup — fail silently, try again next foreground */
    } finally {
      isRunning.current = false;
    }
  }, []);

  useEffect(() => {
    checkAndApply(); // on launch
    let prev: AppStateStatus = AppState.currentState;
    const sub = AppState.addEventListener("change", (next) => {
      if (prev.match(/inactive|background/) && next === "active") checkAndApply();
      prev = next;
    });
    return () => sub.remove();
  }, [checkAndApply]);
}
```

Call `useOTAUpdates()` once, at the top of the root layout. Rollback: revert the channel/branch on
EAS's dashboard (or `eas update:republish` a known-good update) — there is no in-app rollback
mechanism in either reference app; document this as an operational runbook step, not code.

### Env across build profiles — the confirmed gap

**Neither app** varies the API base URL (or any config) by EAS build profile — both hardcode a
single literal in `libs/api-urls.ts` regardless of whether the build is development/preview/
production. Canonical going forward: read from `expo-constants`' `extra` block, populated per
profile via `eas.json`'s `env` key or `app.config.ts` conditional logic:

```ts
const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl ?? "https://api.example.com";
```

### Versioning

`runtimeVersion: { policy: "appVersion" }` in both — canonical. `autoIncrement: true` on the
production build profile (native build number auto-bumps; `version` in `app.json` is the
human-facing app version, bumped manually).
