import { type PropsWithChildren } from "react";
import { SafeAreaView } from "react-native-safe-area-context";

type ScreenProps = PropsWithChildren<{ className?: string }>;

/**
 * Always SafeAreaView — never a bare View with a hardcoded top offset (confirmed bug in one
 * reference app that doesn't adapt across device notch heights).
 */
export function Screen({ children, className }: ScreenProps) {
  return <SafeAreaView className={`flex-1 bg-ink-50 ${className ?? ""}`}>{children}</SafeAreaView>;
}
