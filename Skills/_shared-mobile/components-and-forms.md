# Components & Forms — Canonical (Mobile)

## Component tiers — 3-tier, mirrors the web suite

Adopted as canonical:

1. **`components/ui/`** — generic primitives with no domain knowledge: `Button`, `TextField`,
   `ButtonSheet`, `Skeleton`, `Toster`, `SegmentedTabs`. Named exports where the component is a
   building block used everywhere.
2. **`components/pages/`** — screen-shell wrappers: `Screen` (SafeAreaView + theme background),
   `TopBar`/`SubHeader`. Not domain-specific; used by every screen.
3. **`components/custom/{domain}/`** — domain-specific components (a recipient card, a request
   summary row). Optional per-domain subfolder once a domain has more than a couple of components.

Reuse a `ui/` primitive before building a one-off. Promote a repeated composition (e.g. a
domain-specific card style used in three screens) to `custom/{domain}/`, not copy-pasted per screen.

## `Screen` — the base shell (always `SafeAreaView`, theme-aware)

```tsx
import { SafeAreaView } from "react-native-safe-area-context";

export function Screen({ children, className }: PropsWithChildren<{ className?: string }>) {
  return (
    <SafeAreaView className={`flex-1 bg-ink-50 ${className ?? ""}`}>
      {children}
    </SafeAreaView>
  );
}
```

**Always `SafeAreaView` from `react-native-safe-area-context`** — never a bare `View` with a
hardcoded `pt-20`-style manual offset (confirmed bug in one reference app: doesn't adapt across
different notch/safe-area heights per device).

## `Button` — the base primitive

```tsx
export function Button({ label, onPress, disabled, loading, variant = "primary", leftIcon, rightIcon }: Props) {
  const isDisabled = disabled || loading;
  return (
    <Pressable
      className={`h-14 w-full items-center justify-center rounded-2xl ${variant === "primary" ? "bg-brandBlue-500" : "bg-ink-100"} ${isDisabled ? "opacity-60" : ""}`}
      disabled={isDisabled}
      onPress={onPress}
      accessibilityRole="button"
    >
      <View className="flex-row items-center justify-center gap-3">
        {leftIcon}
        <Text className={`text-[18px] font-semibold ${variant === "primary" ? "text-white" : "text-ink-900"}`}>
          {loading ? "Please wait…" : label}
        </Text>
        {rightIcon}
      </View>
    </Pressable>
  );
}
```

`accessibilityRole="button"` on every pressable. Loading state swaps the label — same convention
as web's button loading text-swap.

## `ButtonSheet` — the canonical modal/confirm primitive

A Reanimated spring-animated bottom sheet — **this is the mobile equivalent of the web suite's
`Dialog`/`ConfirmDialog`**, confirmed near-identical in both reference apps: backdrop overlay +
sheet that self-measures its height via `onLayout` and animates up with `withSpring`, dismissible
via backdrop tap or an explicit close button, repositions above the keyboard on show/hide. Full
template: [references/patterns.md](../mobile-components/references/patterns.md#buttonsheet).

Every confirmation flow (destructive or not) uses `ButtonSheet` — **not** `Alert.alert`, confirmed
as the actual pattern in both apps for account deletion and other confirms.

## Forms — the canonical pattern (new: build the `<Controller>`-wrapped field)

**Older code often does this poorly** — wiring fields imperatively (`watch`/`setValue` into a
plain controlled `TextField`) or using no RHF/zod at
all (hand-rolled `useEffect`-based validation per field). The canonical form field going forward
is a **new, `<Controller>`-wrapped** component, closer to the web suite's `InputField`:

```tsx
// components/ui/text-field.tsx
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

export function TextField({ control, name, label, placeholder, keyboardType = "default", secureTextEntry, editable = true }: TextFieldProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field: { value, onChange, onBlur }, fieldState: { error } }) => (
        <View className="w-full">
          {label && <Text className="mb-2 text-[12px] font-semibold text-ink-500">{label}</Text>}
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
          {error?.message && <Text className="mt-2 text-[12px] text-red-500">{error.message}</Text>}
        </View>
      )}
    />
  );
}
```

Schema + form wiring — same shape as web, `zodResolver`, snake_case fields matching the API:

```tsx
const form = useForm<VerifyOTPInput>({
  resolver: zodResolver(verifyOTPSchema),
  defaultValues: { code: "", token: otpRequestMeta?.token ?? "" },
  mode: "onChange",
});

<TextField control={form.control} name="code" label="Code" keyboardType="number-pad" />

<Button
  label="Verify"
  onPress={form.handleSubmit(onSubmit)}
  loading={form.formState.isSubmitting}
  disabled={!form.formState.isValid}
/>
```

For third-party inputs that don't ref-forward cleanly with `<Controller>` (e.g. `OtpInput` from
`react-native-otp-entry`), fall back to `setValue(name, value, { shouldValidate: true })` from
`useFormContext()`/the same `useForm()` instance — keep the rest of the form on `<Controller>`.

### Keyboard handling (confirmed convention, both apps)

```tsx
<KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
  <ScrollView keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
    {/* form fields */}
  </ScrollView>
</KeyboardAvoidingView>
```

For numeric/phone keyboards on iOS, add a custom `InputAccessoryView` "Done" bar (confirmed
detail in the more mature reference app) — Android's keyboard has a built-in dismiss affordance,
iOS's numeric keyboards don't.

## Submit → mutation → cache

Same convention as web: `form.handleSubmit(onSubmit)` where `onSubmit` calls the service action
(directly, or via `useMutation` if you want `isPending`/cache-invalidation semantics). On error,
map field-specific errors back with `form.setError(fieldName, { message })`; show a toast via
`useToster()` for form-level errors.
