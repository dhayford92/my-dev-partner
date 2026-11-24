import Constants from "expo-constants";
import * as Device from "expo-device";
import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

/**
 * Registers for push notifications and returns the Expo push token, or undefined if permission
 * was denied or this isn't a physical device. See ../../../_shared-mobile/native.md#push-notifications.
 */
export default async function registerForPushNotificationsAsync(): Promise<string | undefined> {
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#FF231F7C",
    });
  }

  if (!Device.isDevice) {
    if (__DEV__) console.log("Push notifications require a physical device.");
    return undefined;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== "granted") {
    finalStatus = (await Notifications.requestPermissionsAsync()).status;
  }
  if (finalStatus !== "granted") {
    // Canonical: surface an in-app message with a Linking.openSettings() action here —
    // do NOT use a bare alert() (confirmed anti-pattern in both reference apps).
    return undefined;
  }

  const projectId =
    Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
  if (!projectId) throw new Error("EAS project ID not found in app config.");

  const { data: token } = await Notifications.getExpoPushTokenAsync({ projectId });
  return token;
}
