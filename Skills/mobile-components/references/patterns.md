# Component & form patterns (generate verbatim)

## The field family (`components/ui/`)

`TextField` is the canonical primitive (full source in
`../../mobile-scaffold/assets/components/ui/text-field.tsx`). Siblings share its exact shape —
`Controller` + themed container + inline error text.

### `CheckboxField`

```tsx
import { Controller, type Control } from "react-hook-form";
import { Pressable, Text, View } from "react-native";

interface CheckboxFieldProps {
  control: Control<any>;
  name: string;
  label: string;
}

export function CheckboxField({ control, name, label }: CheckboxFieldProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field: { value, onChange } }) => (
        <Pressable onPress={() => onChange(!value)} className="flex-row items-center gap-3 py-2">
          <View className={`h-6 w-6 items-center justify-center rounded-lg border-2 ${value ? "border-brandBlue-500 bg-brandBlue-500" : "border-ink-200"}`}>
            {value ? <Text className="text-[12px] font-bold text-white">✓</Text> : null}
          </View>
          <Text className="flex-1 text-[15px] text-ink-900">{label}</Text>
        </Pressable>
      )}
    />
  );
}
```

### `SelectField` (native picker, platform-adaptive)

```tsx
import { Controller, type Control } from "react-hook-form";
import { Platform, Text, View } from "react-native";
import { Picker } from "@react-native-picker/picker";

interface Option { label: string; value: string }
interface SelectFieldProps {
  control: Control<any>;
  name: string;
  label?: string;
  options: Option[];
}

export function SelectField({ control, name, label, options }: SelectFieldProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field: { value, onChange }, fieldState: { error } }) => (
        <View className="w-full">
          {label ? <Text className="mb-2 text-[12px] font-semibold text-ink-500">{label}</Text> : null}
          <View className={`rounded-2xl border ${error ? "border-red-400" : "border-ink-200"} ${Platform.OS === "ios" ? "" : "overflow-hidden"}`}>
            <Picker selectedValue={value} onValueChange={onChange}>
              {options.map((o) => <Picker.Item key={o.value} label={o.label} value={o.value} />)}
            </Picker>
          </View>
          {error?.message ? <Text className="mt-2 text-[12px] text-red-500">{error.message}</Text> : null}
        </View>
      )}
    />
  );
}
```

## Forms — full example

```tsx
const schema = z.object({
  full_name: z.string().min(1, "Name is required"),
  accepts_terms: z.boolean().refine((v) => v === true, "You must accept the terms"),
});
type FormInput = z.infer<typeof schema>;

export default function CompleteAccountScreen() {
  const { show } = useToster();
  const form = useForm<FormInput>({
    resolver: zodResolver(schema),
    defaultValues: { full_name: "", accepts_terms: false },
    mode: "onChange",
  });

  const mutation = useMutation({
    mutationFn: (values: FormInput) => completeAccount(values),
    onSuccess: () => router.replace(ROUTES.HOME.ROOT),
    onError: (error) => show({ type: "error", message: getErrorMessage(error) }),
  });

  return (
    <Screen>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
        <ScrollView keyboardShouldPersistTaps="handled" contentContainerClassName="px-6 py-8 gap-4">
          <TextField control={form.control} name="full_name" label="Full name" />
          <CheckboxField control={form.control} name="accepts_terms" label="I accept the terms" />
          <Button
            label="Continue"
            onPress={form.handleSubmit((v) => mutation.mutate(v))}
            loading={mutation.isPending}
            disabled={!form.formState.isValid}
          />
        </ScrollView>
      </KeyboardAvoidingView>
    </Screen>
  );
}
```

## iOS Done accessory

For numeric/phone-pad keyboards on iOS, add a "Done" bar (Android has one built in):

```tsx
const accessoryId = useId();
const showIosDoneBar = Platform.OS === "ios" && (keyboardType === "number-pad" || keyboardType === "phone-pad");

{showIosDoneBar ? (
  <InputAccessoryView nativeID={accessoryId}>
    <View className="flex-row justify-end border-t border-ink-200 bg-ink-50 px-3 py-2">
      <Pressable onPress={() => Keyboard.dismiss()} hitSlop={12}>
        <Text className="text-[17px] font-semibold text-brandBlue-500">Done</Text>
      </Pressable>
    </View>
  </InputAccessoryView>
) : null}
<TextInput inputAccessoryViewID={showIosDoneBar ? accessoryId : undefined} ... />
```

## ButtonSheet usage

Full component source: `../../mobile-scaffold/assets/components/ui/button-sheet.tsx`.

```tsx
const [open, setOpen] = useState(false);

<Button label="Delete" onPress={() => setOpen(true)} variant="secondary" />

{open && (
  <ButtonSheet title="Delete item" onClose={() => setOpen(false)}>
    <Text className="text-center text-[15px] text-ink-700">
      Are you sure? This cannot be undone.
    </Text>
    <Button label={deleteMutation.isPending ? "Deleting..." : "Yes, delete"}
            onPress={() => deleteMutation.mutate()}
            loading={deleteMutation.isPending} />
    <Button label="Cancel" variant="secondary" onPress={() => setOpen(false)} />
  </ButtonSheet>
)}
```

The mutation itself (pessimistic, stay-signed-in/on-screen on failure) is `mobile-data`'s
responsibility — see `../../mobile-data/references/destructive-actions.md`.

## Full screen assembly (list + create sheet)

Logic lives directly in the route file — no `features/` delegation:

```tsx
// app/(tabs)/recipients/index.tsx
export default function RecipientsScreen() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: queryKeys.recipients.list(),
    queryFn: getRecipients,
  });
  const [createOpen, setCreateOpen] = useState(false);

  return (
    <Screen>
      <TopBar title="Recipients" />
      <View className="flex-1 px-5">
        <Button label="Add recipient" onPress={() => setCreateOpen(true)} />
        {isLoading ? (
          <Skeleton className="mt-4 h-20 w-full" />
        ) : isError ? (
          <ErrorState message="Couldn't load recipients." retry={refetch} />
        ) : data && data.length === 0 ? (
          <EmptyState title="No recipients yet" action={{ label: "Add one", onPress: () => setCreateOpen(true) }} />
        ) : (
          <FlatList data={data} keyExtractor={(r) => r.id} renderItem={({ item }) => <RecipientCard recipient={item} />} />
        )}
      </View>

      {createOpen && (
        <ButtonSheet title="New recipient" onClose={() => setCreateOpen(false)}>
          <RecipientForm onSuccess={() => setCreateOpen(false)} />
        </ButtonSheet>
      )}
    </Screen>
  );
}
```
