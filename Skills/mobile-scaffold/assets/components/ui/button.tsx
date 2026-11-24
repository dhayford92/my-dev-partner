import { Pressable, Text, View } from "react-native";

interface ButtonProps {
  label: string;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: "primary" | "secondary";
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Button({
  label,
  onPress,
  disabled,
  loading,
  variant = "primary",
  leftIcon,
  rightIcon,
}: ButtonProps) {
  const isDisabled = disabled || loading;
  const bg = variant === "primary" ? "bg-brandBlue-500" : "bg-ink-100";
  const text = variant === "primary" ? "text-white" : "text-ink-900";

  return (
    <Pressable
      className={`h-14 w-full items-center justify-center rounded-2xl ${bg} ${isDisabled ? "opacity-60" : "opacity-100"}`}
      disabled={isDisabled}
      onPress={onPress}
      accessibilityRole="button"
    >
      <View className="flex-row items-center justify-center gap-3">
        {leftIcon}
        <Text className={`text-[18px] font-semibold ${text}`}>
          {loading ? "Please wait…" : label}
        </Text>
        {rightIcon}
      </View>
    </Pressable>
  );
}
