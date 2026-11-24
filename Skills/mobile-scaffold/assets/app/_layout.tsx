import "@/global.css";
import { AuthProvider } from "@/providers/auth-provider";
import NotificationProvider from "@/providers/notification-provider";
import TosterProvider from "@/components/ui/toster";
import { useOTAUpdates } from "@/hooks/useOTAUpdates";
import { focusManager, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import * as Notifications from "expo-notifications";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import * as WebBrowser from "expo-web-browser";
import React, { useEffect } from "react";
import { AppState, type AppStateStatus, Platform } from "react-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import "react-native-reanimated";

// Module-level singleton — never create the QueryClient inline in JSX (recreates on every render).
const queryClient = new QueryClient();

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

SplashScreen.preventAutoHideAsync();
WebBrowser.maybeCompleteAuthSession();
SplashScreen.setOptions({ duration: 300, fade: true });

export default function RootLayout() {
  // React Native has no browser visibilitychange event — this is the required TanStack Query
  // foreground-refetch wiring. See ../../../_shared-mobile/data-layer.md.
  useEffect(() => {
    function onAppStateChange(status: AppStateStatus) {
      if (Platform.OS !== "web") focusManager.setFocused(status === "active");
    }
    const subscription = AppState.addEventListener("change", onAppStateChange);
    return () => subscription.remove();
  }, []);

  useOTAUpdates();

  useEffect(() => {
    SplashScreen.hideAsync();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <NotificationProvider>
        <TosterProvider>
          <AuthProvider>
            <GestureHandlerRootView style={{ flex: 1 }}>
              <Stack screenOptions={{ headerShown: false }}>
                <Stack.Screen name="index" />
                <Stack.Screen name="(auth)" />
                <Stack.Screen name="(tabs)" />
              </Stack>
            </GestureHandlerRootView>
          </AuthProvider>
        </TosterProvider>
      </NotificationProvider>
    </QueryClientProvider>
  );
}
