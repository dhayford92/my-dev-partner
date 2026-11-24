---
name: mobile-components
description: Generate mobile screens, components, and forms matching Denzel's Expo Router conventions exactly — the 3-tier component structure (ui/pages/custom), logic-in-route-file screen architecture (no separate features/ layer), the canonical <Controller>-wrapped form field family, keyboard handling, and the ButtonSheet confirm/modal pattern. Use whenever building a new screen, a form, or a reusable mobile component. Every output matches the extracted conventions and wires cleanly to a real or stubbed service action. Do not use for the data hooks themselves (mobile-data), native capability code (mobile-native), or bootstrapping (mobile-scaffold).
---

# mobile-components

Build screens and components indistinguishable from the reference codebases. Conventions and full
rationale live in
[`../_shared-mobile/components-and-forms.md`](../_shared-mobile/components-and-forms.md) and
[`../_shared-mobile/stack-and-structure.md`](../_shared-mobile/stack-and-structure.md) — read them; this skill is
the generation procedure on top of them.

## Screen architecture — logic lives in the route file

**Canonical (owner's explicit choice): no `features/` delegation layer.** A screen's route file
under `app/` contains its hooks, data fetching, and JSX directly:

```tsx
// app/(tabs)/requests/index.tsx
export default function RequestsScreen() {
  const { data } = useQuery({ queryKey: queryKeys.requests.list("current"), queryFn: () => getRequests("current") });
  return ( /* full JSX tree here */ );
}
```

Don't generate a parallel `features/{domain}/screens/*.tsx` file that the route re-exports — that
pattern exists in one reference app but was **not** chosen as canonical. Keep the route file itself
as the screen; extract a component only when it's reused across more than one screen (then it goes
in `components/custom/{domain}/`, not a screen-local `features/` folder).

## The 3-tier component decision

1. **`components/ui/`** — generic, no domain knowledge: `Button`, `TextField`, `ButtonSheet`,
   `Skeleton`, `Toster`, `SegmentedTabs`. Reach here first.
2. **`components/pages/`** — screen-shell wrappers used by every screen: `Screen`
   (`SafeAreaView`-based), `TopBar`/`SubHeader`.
3. **`components/custom/{domain}/`** — domain-specific, reused across ≥2 screens in that domain.

Full primitives and rationale: [references/patterns.md](references/patterns.md).

## Forms — the canonical `<Controller>`-wrapped pattern

**This is new relative to both reference apps** (per the owner's decision — neither app's exact
form-wiring style was kept). Always:

- `react-hook-form` + `zodResolver`, schema in `services/schemas/{domain}.ts`
  (`export const xSchema = z.object({...}); export type XInput = z.infer<typeof xSchema>;`),
  snake_case fields matching the API payload.
- Fields via **`<Controller>`-wrapped** components (`TextField` and its siblings —
  `CheckboxField`, `SelectField`) — never a plain `TextInput` with manual `value`/`onChangeText`
  wiring and hand-rolled validation.
- `mode: "onChange"` on `useForm` (confirmed convention — validate as the user types).
- Submit: `form.handleSubmit(onSubmit)`; `loading={form.formState.isSubmitting}` or
  `mutation.isPending` on the `Button`; `disabled` while invalid or submitting.
- For a third-party input that can't ref-forward through `<Controller>` cleanly (e.g. an OTP
  entry widget), fall back to `setValue(name, value, {shouldValidate:true})` from the same
  `useForm()` instance — keep every other field on `<Controller>`.

Full field family + a complete form example: [references/patterns.md](references/patterns.md#forms).

## Keyboard handling (always)

```tsx
<KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
  <ScrollView keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
    {/* fields */}
  </ScrollView>
</KeyboardAvoidingView>
```

Add a custom iOS `InputAccessoryView` "Done" bar for numeric/phone keyboards (Android's keyboard
already has a dismiss affordance; iOS's numeric keyboards don't) — see
[references/patterns.md](references/patterns.md#ios-done-accessory).

## Confirmation & modal UX — `ButtonSheet`, never `Alert.alert`

Confirmed canonical in both reference apps for every confirm/modal need, destructive or not. Full
template: [references/patterns.md](references/patterns.md#buttonsheet-usage). The destructive
mutation wiring itself (pessimistic update, error handling) belongs to `mobile-data` — this skill
only owns the `ButtonSheet` UI shell.

## Every generated screen/component ships wired to a real or stubbed action

```ts
export async function createThing(input: ThingInput): Promise<ThingResponse> {
  return apiFetch<ThingResponse>({ method: "POST", url: API_URLS.CORE.THINGS.CREATE, data: input, autoAuth: true });
  // or, before the endpoint exists: return { id: "stub", ...input } as ThingResponse;
}
```

## Verify

If a dev build/Expo Go is available, render the screen and confirm: it mounts without a
red-screen error, the form validates (empty submit → zod errors under fields), keyboard
avoidance doesn't cover the active field, and a successful submit shows a toast via `useToster()`.
Use the device/simulator; don't claim this from a type-check alone.

## Anti-patterns (do not generate)

- A `features/{domain}/` screen-delegation layer.
- Plain `TextInput` + manual `useState`/`useEffect` validation instead of `<Controller>` + zod.
- `Alert.alert` for confirmation — use `ButtonSheet`.
- `StyleSheet.create` where NativeWind `className` can express the same styling (reserve
  `StyleSheet` for Reanimated-driven `style` props that `className` can't express).
- Dark-mode branching (`useColorScheme`) unless the specific project has opted into it.
