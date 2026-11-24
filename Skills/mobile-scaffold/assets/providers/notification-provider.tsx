import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { useQueryClient, type QueryClient } from "@tanstack/react-query";
import type { EventSubscription } from "expo-modules-core";
import * as Notifications from "expo-notifications";
import { router } from "expo-router";
import registerForPushNotificationsAsync from "@/hooks/registerForPushNotificationsAsync";
import { queryKeys } from "@/libs/query_keys";

interface NotificationContextValue {
  expoPushToken: string | null;
  error: Error | null;
}

const NotificationContext = createContext<NotificationContextValue | null>(null);

export function useNotification(): NotificationContextValue {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error("useNotification must be used within NotificationProvider");
  return ctx;
}

/** Centralized so both listeners share one branch — extend per project's notification types. */
function handleNotificationPayload(
  data: Record<string, unknown> | undefined,
  queryClient: QueryClient,
) {
  if (!data?.type) return;
  switch (data.type) {
    case "auth":
      queryClient.invalidateQueries({ queryKey: queryKeys.profile.me() });
      break;
    default:
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.list() });
  }
}

/** New convention (neither reference app has this) — route based on the notification payload. */
function routeFromNotification(data: Record<string, unknown> | undefined) {
  if (!data?.type) return;
  switch (data.type) {
    case "auth":
      router.push("/(tabs)/home");
      break;
    default:
      // Unknown type — do nothing rather than guess a route.
      break;
  }
}

export default function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [expoPushToken, setExpoPushToken] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const queryClient = useQueryClient();
  const receivedListener = useRef<EventSubscription | null>(null);
  const responseListener = useRef<EventSubscription | null>(null);

  useEffect(() => {
    registerForPushNotificationsAsync().then(
      (token) => setExpoPushToken(token ?? null),
      (err) => setError(err),
    );

    // Cold-start tap: the response listener below doesn't fire for the tap that launched the app.
    Notifications.getLastNotificationResponseAsync().then((response) => {
      if (response) routeFromNotification(response.notification.request.content.data);
    });

    receivedListener.current = Notifications.addNotificationReceivedListener((n) => {
      handleNotificationPayload(n.request.content.data, queryClient);
    });

    responseListener.current = Notifications.addNotificationResponseReceivedListener((r) => {
      handleNotificationPayload(r.notification.request.content.data, queryClient);
      routeFromNotification(r.notification.request.content.data);
    });

    return () => {
      receivedListener.current?.remove();
      responseListener.current?.remove();
    };
  }, [queryClient]);

  return (
    <NotificationContext.Provider value={{ expoPushToken, error }}>
      {children}
    </NotificationContext.Provider>
  );
}
