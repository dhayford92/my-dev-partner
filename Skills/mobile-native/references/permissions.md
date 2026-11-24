# Permission templates (generate verbatim, adapt the capability)

Confirmed pattern across both reference apps: request at the point of need. **New going forward:**
always handle denial with an in-app message + settings deep-link, never a bare `alert()`.

## Push notification permission

```ts
const { status: existing } = await Notifications.getPermissionsAsync();
let finalStatus = existing;
if (existing !== "granted") {
  finalStatus = (await Notifications.requestPermissionsAsync()).status;
}
if (finalStatus !== "granted") {
  show({ type: "info", message: "Enable notifications in Settings to get delivery updates." });
  return undefined;
}
```

## Location permission (confirmed pattern: request at 3 points in the more mature reference app —
proactively at splash, at the point of use, and via a mandatory "Gate" for a required flow)

```ts
const { status } = await Location.requestForegroundPermissionsAsync();
if (status !== "granted") {
  show({
    type: "info",
    message: "Location access is needed to set your delivery address.",
  });
  return null;
}
const position = await Location.getCurrentPositionAsync({});
```

### The "Gate" pattern — for a permission that blocks a core flow

```tsx
// features/location/PrimaryLocationOnboardingGate.tsx (or equivalent)
export function PrimaryLocationOnboardingGate() {
  const { primaryLocation, isLocationHydrated } = useLocation();
  if (!isLocationHydrated || primaryLocation) return null; // satisfied — render nothing
  return (
    <View className="absolute inset-0 z-50 bg-white">
      {/* full-screen "set your location to continue" flow */}
    </View>
  );
}

// mounted alongside the root Stack, not as a route:
<Stack screenOptions={{ headerShown: false }}>...</Stack>
<PrimaryLocationOnboardingGate />
```

A Gate blocks by rendering an overlay, not by redirecting — this keeps the underlying route stack
intact so dismissing the gate (once satisfied) doesn't require re-navigation.

## Camera / media library permission (image picker)

`expo-image-picker`'s `launchImageLibraryAsync`/`launchCameraAsync` request permission internally
on call — you don't need a separate explicit `requestMediaLibraryPermissionsAsync()` call before
invoking them. Set the rationale text once, statically, in `app.json`'s plugin config:

```json
["expo-image-picker", { "photosPermission": "This app accesses your photos to set your profile picture.", "cameraPermission": "Allow the app to access your camera to take a profile picture." }]
```

Handle the result explicitly — neither reference app checks for a canceled/denied result:

```ts
const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["images"], quality: 0.8 });
if (result.canceled) return; // user backed out or permission was denied — don't treat as an error
onChange(result.assets[0].uri);
```

## Settings deep-link (the missing piece in both reference apps)

```ts
import { Linking } from "react-native";

function openAppSettings() {
  Linking.openSettings();
}
```

Show this as a button inside the denial message, not automatically — don't redirect the user out
of the app without them choosing to.
