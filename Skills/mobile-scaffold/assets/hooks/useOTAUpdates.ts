import { useCallback, useEffect, useRef } from "react";
import { AppState, type AppStateStatus } from "react-native";
import * as Updates from "expo-updates";

/**
 * Checks for an EAS Update (OTA) on launch and whenever the app returns to the foreground.
 * No-ops in development / Expo Go (Updates.isEnabled is false there). See ../../../_shared-mobile/native.md.
 */
export function useOTAUpdates(): void {
  const isRunning = useRef(false);

  const checkAndApply = useCallback(async () => {
    if (!Updates.isEnabled || __DEV__) return;
    if (isRunning.current) return;
    isRunning.current = true;
    try {
      const result = await Updates.checkForUpdateAsync();
      if (result.isAvailable) {
        await Updates.fetchUpdateAsync();
        await Updates.reloadAsync();
      }
    } catch (err) {
      if (__DEV__) console.log("[OTA] Update check failed:", err);
    } finally {
      isRunning.current = false;
    }
  }, []);

  useEffect(() => {
    checkAndApply();
    let previousState: AppStateStatus = AppState.currentState;
    const subscription = AppState.addEventListener("change", (nextState) => {
      if (previousState.match(/inactive|background/) && nextState === "active") {
        checkAndApply();
      }
      previousState = nextState;
    });
    return () => subscription.remove();
  }, [checkAndApply]);
}
