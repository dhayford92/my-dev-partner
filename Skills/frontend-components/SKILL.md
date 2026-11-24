---
name: frontend-components
description: Generate components and forms that match Denzel's conventions exactly — the 3-tier decision (shadcn primitive vs ui/ extension vs custom feature component), folder/naming/props rules, and the full form pattern (react-hook-form + zod, the InputField family, schema location, native form="" dialog submit, loading/disabled states, and wiring a form's success path to a mutation + cache invalidation). Use whenever building a new component, a form, or a CRUD page UI. Every output includes a working example wired to a real or stubbed server action. Do not use for the data hooks themselves (frontend-data) or bootstrapping (frontend-scaffold).
---

# frontend-components

Build components and forms that are indistinguishable from the existing codebase. Conventions and
the full rationale live in
[`../_shared-web/components-and-forms.md`](../_shared-web/components-and-forms.md) — read it; this skill is
the generation procedure on top of it.

## Before generating

- Know the tier (below). Reuse a shadcn primitive or an existing `ui/` extension before writing
  anything new. Check `components/ui/` for `confirm-dialog`, `crud-dialog`, `data-table`,
  `details-sheet`, `resource-page-header`, `states`, `card-grid` — they probably already cover it.
- Match the surrounding files' import style (`@/` only), export style, and `"use client"` usage.
- Field/schema field names are **snake_case** (they map to the backend payload).

## The 3-tier decision

1. **shadcn primitive** (`components/ui/<name>`) — need a button, input, dialog, table? Install:
   `pnpm dlx shadcn@latest add <name>`. Never hand-roll what shadcn ships.
2. **`ui/` extension** — you're repeating the same primitive composition (dialog+confirm,
   RHF+field, page header+search). Promote it to a named-export `ui/` component. Compose the
   primitive; never fork its file.
3. **`custom/{domain}/` feature component** — domain-specific UI (a `ProjectCard`, a
   `ReportShareDialog`). Default export, typed `interface XProps`, lives under the feature domain.

`page/` composites (sidebar, headers) are for app-shell framing only.

## Forms — generate exactly this shape

The canonical form is RHF + `zodResolver` + the `InputField` family. Full template and the
422→field-error mapping are in
[`../_shared-web/components-and-forms.md`](../_shared-web/components-and-forms.md#forms--the-canonical-pattern).
Non-negotiables when you generate a form:

- Schema in `lib/schemas/{domain}.ts`: `export const xSchema = z.object({...})` +
  `export type XInput = z.infer<typeof xSchema>`. Reuse `emailSchema`/`passwordSchema` from
  `common.ts`. Client-only fields (confirm password) → separate `xFormSchema` with `.refine()`.
- Fields via `InputField` / `CheckboxField` / `TextareaField` / `SelectFormField` — never raw
  `<Input>` + manual error wiring.
- Submit: `form.handleSubmit((d) => mutation.mutate(d))`. On success, check `result.error` →
  `toast` → invalidate/redirect/close. On error, map `ApiError.fieldErrors` back via
  `form.setError`.
- Loading: swap the submit button label + `disabled={mutation.isPending}` on the button **and
  every field**.

### Forms inside dialogs — native `form=""` (canonical, replaces the old hack)

Do **not** use `document.getElementById(id).click()`. Associate the footer button with the form
by id. Generate `CrudDialog` (or use the existing one) so its submit button is
`type="submit" form={formId}`:

```tsx
// CrudDialog footer:
<Button type="submit" form={formId} disabled={isSubmitting}>
  {isSubmitting ? "Saving..." : submitLabel}
</Button>

// the form the dialog wraps:
<form id={formId} onSubmit={form.handleSubmit(onSubmit)} className="grid gap-4">
  <InputField control={form.control} name="name" label="Name" disabled={isSubmitting} />
</form>
```

Detail + the full `CrudDialog` template:
[references/patterns.md](references/patterns.md#crud-dialog-with-native-form-association).

## CRUD page assembly

`page.tsx` owns the query, dialog/selection `useState`, and the create/update/delete mutations;
it renders `ResourcePageHeader` + a card grid or `DataTable` + `EmptyState` + `CrudDialog`
(create/edit) + `ConfirmDialog` (delete). Reference implementation and a full generated example
are in [references/patterns.md](references/patterns.md#crud-page). The data hooks it calls come
from `frontend-data`; the destructive flow is documented there too.

## Every generated component ships with a working example

When you generate a component or form, also produce a minimal usage example wired to a **real or
stubbed** server action, so it compiles and renders. Stub shape:

```ts
"use server";
export async function createThing(input: ThingInput): Promise<ActionResult<Thing>> {
  // return success(mock) — replace with apiFetch when the endpoint exists
}
```

## Verify

If the dev server is available, render the component/page and confirm: it mounts without console
errors, the form validates (empty submit → zod errors), disabled/loading states toggle, and a
successful submit fires the toast. Use the preview tools; don't ask the user to check manually.

## Anti-patterns (do not generate)

- Raw `<Input>` + manual `<p className="error">` — use `InputField`.
- `useApi.ts` / `useApiQuery` / `useAsyncData` — deprecated (see `../_shared-web/data-layer.md`).
- `document.getElementById(id).click()` dialog submit — use native `form=""`.
- Forking a shadcn primitive to restyle it — wrap it in a `ui/` extension instead.
- Inline toast color styles (`{style:{background:'green'}}`) — use default sonner variants.
