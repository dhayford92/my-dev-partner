import { Stack } from "expo-router";

// Bare Stack — no guard logic here (see ../../../../_shared-mobile/stack-and-structure.md).
export default function AuthLayout() {
  return <Stack screenOptions={{ headerShown: false }} />;
}
