# Biometric auth (new capability — neither reference app has this)

Gates access to an **already-authenticated** session (the user still logs in via OTP/OAuth first);
it is a re-entry convenience, not a login method.

## Setup

```bash
npx expo install expo-local-authentication
```

`app.json` — iOS needs a usage description if Face ID is used:

```json
{ "ios": { "infoPlist": { "NSFaceIDUsageDescription": "Unlock the app with Face ID." } } }
```

## The unlock check

```ts
// libs/biometrics.ts
import * as LocalAuthentication from "expo-local-authentication";
import DataStorage from "@/libs/storage";

const BIOMETRIC_ENABLED_KEY = "biometric_unlock_enabled";

export async function isBiometricAvailable(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  return hasHardware && isEnrolled;
}

export async function isBiometricEnabled(): Promise<boolean> {
  return (await DataStorage.get<boolean>(BIOMETRIC_ENABLED_KEY)) ?? false;
}

export async function setBiometricEnabled(enabled: boolean): Promise<void> {
  await DataStorage.set(BIOMETRIC_ENABLED_KEY, enabled);
}

export async function tryBiometricUnlock(): Promise<boolean> {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock with biometrics",
    fallbackLabel: "Use passcode",
    cancelLabel: "Cancel",
  });
  return result.success;
}
```

## Wiring into the auth gate

Default **off**. Only check biometrics when the preference is on **and** a session already
exists — never as a replacement for the actual login flow:

```tsx
// app/index.tsx
export default function Index() {
  const { isAuthenticated, isHydrated } = useAuth();
  const [biometricPassed, setBiometricPassed] = useState(false);
  const [biometricChecked, setBiometricChecked] = useState(false);

  useEffect(() => {
    (async () => {
      if (!isHydrated || !isAuthenticated) { setBiometricChecked(true); return; }
      const enabled = await isBiometricEnabled();
      if (!enabled) { setBiometricPassed(true); setBiometricChecked(true); return; }
      const ok = await tryBiometricUnlock();
      setBiometricPassed(ok);
      setBiometricChecked(true);
    })();
  }, [isHydrated, isAuthenticated]);

  if (!isHydrated || !biometricChecked) return <SplashLikeScreen />;
  if (isAuthenticated && !biometricPassed) return <BiometricLockScreen onRetry={/* re-run tryBiometricUnlock */} />;
  return <Redirect href={isAuthenticated ? ROUTES.HOME.ROOT : ROUTES.AUTH.WELCOME} />;
}
```

`BiometricLockScreen` is a simple full-screen prompt with a "Try again" button (biometric failure
shouldn't sign the user out — it's a re-entry gate, not an auth failure).

## Settings toggle

```tsx
const [available, setAvailable] = useState(false);
const [enabled, setEnabled] = useState(false);

useEffect(() => {
  isBiometricAvailable().then(setAvailable);
  isBiometricEnabled().then(setEnabled);
}, []);

if (!available) return null; // don't show the toggle on hardware that can't support it

<Switch
  value={enabled}
  onValueChange={async (next) => {
    if (next) {
      const ok = await tryBiometricUnlock(); // confirm capability actually works before enabling
      if (!ok) { show({ type: "error", message: "Couldn't verify biometrics." }); return; }
    }
    await setBiometricEnabled(next);
    setEnabled(next);
  }}
/>
```
