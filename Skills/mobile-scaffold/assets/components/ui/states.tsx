import React from "react";
import { Pressable, Text, View } from "react-native";

/**
 * Minimal empty/error state kit. Neither reference app has one — keep this light-touch, don't
 * over-build into a rich system. See ../../../../_shared-mobile/states-and-motion.md.
 */

export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: { label: string; onPress: () => void };
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <View className="flex-1 items-center justify-center px-8 py-12">
      <Text className="text-center text-[16px] font-semibold text-ink-900">{title}</Text>
      {description ? (
        <Text className="mt-2 text-center text-[13px] text-ink-500">{description}</Text>
      ) : null}
      {action ? (
        <Pressable onPress={action.onPress} className="mt-4 rounded-full bg-brandBlue-500 px-5 py-2.5">
          <Text className="text-[14px] font-semibold text-white">{action.label}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

export interface ErrorStateProps {
  title?: string;
  message: string;
  retry?: () => void;
}

export function ErrorState({ title = "Something went wrong", message, retry }: ErrorStateProps) {
  return (
    <View className="flex-1 items-center justify-center px-8 py-12">
      <Text className="text-center text-[16px] font-semibold text-ink-900">{title}</Text>
      <Text className="mt-2 text-center text-[13px] text-ink-500">{message}</Text>
      {retry ? (
        <Pressable onPress={retry} className="mt-4 rounded-full border border-ink-200 px-5 py-2.5">
          <Text className="text-[14px] font-semibold text-ink-900">Try again</Text>
        </Pressable>
      ) : null}
    </View>
  );
}
