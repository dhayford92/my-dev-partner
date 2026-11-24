import { Controller, type Control } from "react-hook-form";
import { Text, TextInput, View } from "react-native";

interface TextFieldProps {
  control: Control<any>;
  name: string;
  label?: string;
  placeholder?: string;
  keyboardType?: "default" | "number-pad" | "phone-pad" | "email-address";
  secureTextEntry?: boolean;
  editable?: boolean;
}

/** The canonical Controller-wrapped field — see ../../../../_shared-mobile/components-and-forms.md#forms. */
export function TextField({
  control,
  name,
  label,
  placeholder,
  keyboardType = "default",
  secureTextEntry,
  editable = true,
}: TextFieldProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field: { value, onChange, onBlur }, fieldState: { error } }) => (
        <View className="w-full">
          {label ? <Text className="mb-2 text-[12px] font-semibold text-ink-500">{label}</Text> : null}
          <TextInput
            className={`h-14 w-full rounded-2xl border px-4 text-[18px] text-ink-900 ${error ? "border-red-400" : "border-ink-200"}`}
            placeholder={placeholder}
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            keyboardType={keyboardType}
            secureTextEntry={secureTextEntry}
            editable={editable}
            returnKeyType="done"
          />
          {error?.message ? <Text className="mt-2 text-[12px] text-red-500">{error.message}</Text> : null}
        </View>
      )}
    />
  );
}
