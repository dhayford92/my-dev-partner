import { ROUTES } from "@/libs/routes";
import { useAuth } from "@/providers/auth-provider";
import { Redirect } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { View } from "react-native";
import Animated, { FadeIn } from "react-native-reanimated";

/**
 * The ONE auth gate in the app. Nested layouts ((auth), (tabs)) carry no guard logic — see
 * ../../../_shared-mobile/stack-and-structure.md#the-auth-gate--the-only-guard-in-the-app for the documented
 * deep-link gap this implies.
 */
export default function Index() {
  const { isAuthenticated, isHydrated } = useAuth();

  if (!isHydrated) {
    return (
      <View className="flex-1 items-center justify-center bg-brandBlue-500">
        <StatusBar style="light" />
        <Animated.View entering={FadeIn.duration(800)}>
          {/* Replace with your logo */}
        </Animated.View>
      </View>
    );
  }

  return <Redirect href={isAuthenticated ? ROUTES.HOME.ROOT : ROUTES.AUTH.WELCOME} />;
}
