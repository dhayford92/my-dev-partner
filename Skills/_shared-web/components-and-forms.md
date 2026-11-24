# Components & Forms — Canonical

## Component tiers — the decision rule

1. **`components/ui/` — shadcn primitive.** Reach here first. Install via
   `pnpm dlx shadcn@latest add <name>`. Import `@/components/ui/<name>`. Also holds owner-built
   **extensions on the same layer** (composed from primitives): `confirm-dialog`, `crud-dialog`,
   `data-table`, `details-sheet`, `resource-page-header`, `states`, `card-grid`, `usage-meter`.
   **Named exports.**
2. **`components/page/` — layout composite.** App shell pieces: `app-sidebar`, `nav-*`,
   `site-header`, `summary-card`. Combine primitives for the frame around content.
3. **`components/custom/{domain}/` — feature component.** Domain UI (`portal/projects/project-card`,
   `reports/chart-block`). **Default export.**

**When to build custom vs extend shadcn:** if it's a primitive shadcn ships → use it. If you're
repeating the same primitive composition (dialog+confirm, RHF+field) → promote to a `ui/`
extension. Only hand-roll from scratch when no primitive fits (rare). Never fork a shadcn
primitive's file to tweak styling — wrap it.

Props: typed `interface XProps`. Icons: `lucide-react`. Compose, don't configure with mega-prop
objects. Every file that uses hooks/handlers starts with `"use client"`.

## Forms — the canonical pattern

`react-hook-form` + `zodResolver`, built on the shared field primitives. **This is not
optional boilerplate — match it exactly.**

### Field primitive — `InputField` (byte-identical across repos)

```tsx
"use client"
import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Controller, type Control } from "react-hook-form"

interface InputFieldProps {
  control: Control<any>; name: string; label: string;
  type?: string; placeholder?: string; className?: string; disabled?: boolean; min?: number;
}
export default function InputField({ control, name, label, placeholder, className, disabled, type, min }: InputFieldProps) {
  return (
    <Controller control={control} name={name} render={({ field, fieldState }) => (
      <Field data-invalid={fieldState.invalid} className={className}>
        <FieldLabel>{label}</FieldLabel>
        <Input {...field} placeholder={placeholder} disabled={disabled} type={type} min={min}
               aria-invalid={fieldState.invalid} />
        {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
      </Field>
    )} />
  )
}
```

Siblings follow the same shape: `CheckboxField`, `TextareaField`, `SelectFormField`,
`PhoneNumberField`. Live in `components/custom/common/` (product) — the whole family is
`Controller` + shadcn `Field` + `aria-invalid`/`data-invalid` + `FieldError`.

### Schemas — location & shape (`lib/schemas/{domain}.ts`)

```ts
import { z } from "zod";
import { emailSchema, passwordSchema } from "./common";   // shared building blocks

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, "Password is required"),
});
export type LoginInput = z.infer<typeof loginSchema>;
```

- **Field names are snake_case to match the backend** (`full_name`, `new_password`).
- Client-only fields (e.g. `confirmPassword`) go in a **separate `xFormSchema`** that `.extend()`s
  the API schema and `.refine()`s the cross-field rule — keeps the API payload clean.
- Export the **schema** and call `zodResolver(schema)` in the component (not a pre-built resolver).

### Form component — submit wired to a mutation

```tsx
const form = useForm<LoginInput>({ resolver: zodResolver(loginSchema), defaultValues: { email: "", password: "" } });

const mutation = useMutation({
  mutationFn: (data: LoginInput) => loginAction(data),
  onSuccess: (result) => {
    if (result.error) { toast.error(result.error); return; }
    toast.success("Signed in"); router.push("/portal/home");
  },
});

return (
  <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))} className="flex flex-col gap-4">
    <FieldGroup>
      <InputField control={form.control} name="email" label="Email" disabled={mutation.isPending} />
      <InputField control={form.control} name="password" label="Password" type="password" disabled={mutation.isPending} />
      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Signing in..." : "Login"}
      </Button>
    </FieldGroup>
  </form>
);
```

Loading/disabled: button label swaps + `disabled={mutation.isPending}` on the button **and every
field**. Success path always: check `result.error` → `toast` → invalidate/redirect/close.

### Surfacing server validation (422)

On mutation error, push `ApiError.fieldErrors` back into RHF:

```tsx
onError: (err) => {
  if (err instanceof ApiError && err.fieldErrors) {
    err.fieldErrors.forEach(({ field, message }) => form.setError(field as Path<LoginInput>, { message }));
  } else { toast.error(getErrorMessage(err)); }
}
```

### Forms inside dialogs — native association (canonical)

Use `CrudDialog` for create/edit. Associate the footer submit button with the form via the
native **`form="<id>"`** attribute — **not** `document.getElementById(id).click()`.

```tsx
<form id={formId} onSubmit={form.handleSubmit(onSubmit)}> ...fields... </form>
// in the dialog footer:
<Button type="submit" form={formId} disabled={isSubmitting}>{submitLabel}</Button>
```

## CRUD page shape (reference)

`page.tsx` owns: `useQuery` for the list, `useState` for dialog/selection, three `useMutation`s
(create/update/delete). Renders `ResourcePageHeader` (title + primary action), a card grid or
`DataTable`, `EmptyState` when empty, `CrudDialog` (create/edit) + `ConfirmDialog` (delete). See
`app/app/portal/projects/page.tsx` for the full reference implementation.
