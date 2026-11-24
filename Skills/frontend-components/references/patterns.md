# Component & form patterns (generate verbatim)

## The field family (`components/custom/common/`)

`InputField` is the canonical primitive (see `../../_shared-web/components-and-forms.md`). Siblings share
its exact shape — `Controller` + shadcn `Field`/`FieldLabel`/`FieldError` + `aria-invalid`.

```tsx
// select-form-field.tsx
"use client";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Controller, type Control } from "react-hook-form";

interface Option { label: string; value: string }
interface Props {
  control: Control<any>; name: string; label: string;
  options: Option[]; placeholder?: string; disabled?: boolean; className?: string;
}
export default function SelectFormField({ control, name, label, options, placeholder, disabled, className }: Props) {
  return (
    <Controller control={control} name={name} render={({ field, fieldState }) => (
      <Field data-invalid={fieldState.invalid} className={className}>
        <FieldLabel>{label}</FieldLabel>
        <Select value={field.value} onValueChange={field.onChange} disabled={disabled}>
          <SelectTrigger aria-invalid={fieldState.invalid}><SelectValue placeholder={placeholder} /></SelectTrigger>
          <SelectContent>
            {options.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
          </SelectContent>
        </Select>
        {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
      </Field>
    )} />
  );
}
```
`CheckboxField` / `TextareaField` follow the same skeleton with the matching shadcn control.

## CRUD dialog with native form association

Improved `CrudDialog` — footer submit uses `type="submit" form={formId}` (no `getElementById`).

```tsx
export interface CrudDialogProps {
  open: boolean; onOpenChange: (open: boolean) => void;
  title: string; description?: string;
  formId: string;                 // ← ties the footer button to the form
  children: React.ReactNode;      // the <form id={formId}> lives here
  submitLabel?: string; isSubmitting?: boolean; error?: string | null;
}

export function CrudDialog({ open, onOpenChange, title, description, formId, children, submitLabel = "Save", isSubmitting = false, error }: CrudDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <div className="grid gap-4 py-2">{children}</div>
        {error && <p className="text-destructive text-sm">{error}</p>}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>Cancel</Button>
          <Button type="submit" form={formId} disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : submitLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

The form passed as `children` owns its own `id` + `handleSubmit`:

```tsx
function ProjectForm({ formId, defaultValues, onSubmit, disabled }: {
  formId: string; defaultValues?: Partial<ProjectInput>; onSubmit: (d: ProjectInput) => void; disabled?: boolean;
}) {
  const form = useForm<ProjectInput>({ resolver: zodResolver(projectSchema), defaultValues: { name: "", description: "", ...defaultValues } });
  return (
    <form id={formId} onSubmit={form.handleSubmit(onSubmit)} className="grid gap-4">
      <InputField control={form.control} name="name" label="Name" disabled={disabled} />
      <TextareaField control={form.control} name="description" label="Description" disabled={disabled} />
    </form>
  );
}
```

## CRUD page

`page.tsx` owns query + dialog state + mutations, renders header/grid/dialogs. This is the
reference shape (`app/app/portal/projects/page.tsx`), corrected to native `form=""`:

```tsx
"use client";
export default function ProjectsPage() {
  const qc = useQueryClient();
  const createFormId = useId();
  const [search, setSearch] = useState("");
  const debounced = useDebounce(search, 250);

  const projectsQuery = useQuery({
    queryKey: queryKeys.projects.list({ search: debounced }),
    queryFn: () => getProjects({ search: debounced || undefined }),
  });
  const projects = projectsQuery.data ?? [];

  const [createOpen, setCreateOpen] = useState(false);
  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: async (result) => {
      if (result.error) { toast.error(result.error); return; }
      await qc.invalidateQueries({ queryKey: queryKeys.projects.list() });
      setCreateOpen(false);
      toast.success("Project created successfully");
    },
  });

  if (projectsQuery.isError) return <ErrorState error={getErrorMessage(projectsQuery.error)} retry={{ onClick: () => projectsQuery.refetch() }} />;

  return (
    <section className="space-y-4">
      <ResourcePageHeader title="Projects" description="Organize your work"
        searchValue={search} onSearchChange={setSearch}
        primaryAction={{ label: "New Project", onClick: () => setCreateOpen(true) }} />

      {projectsQuery.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><CardSkeleton /><CardSkeleton /><CardSkeleton /></div>
      ) : projects.length === 0 ? (
        <EmptyState icon={FolderKanbanIcon} title="No projects yet"
          action={{ label: "Create Project", onClick: () => setCreateOpen(true) }} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {projects.map((p) => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}

      <CrudDialog open={createOpen} onOpenChange={setCreateOpen} title="Create Project"
        formId={createFormId} isSubmitting={createMutation.isPending} submitLabel="Create Project">
        <ProjectForm formId={createFormId} onSubmit={(d) => createMutation.mutate(d)} disabled={createMutation.isPending} />
      </CrudDialog>
    </section>
  );
}
```

Delete flow (`ConfirmDialog` + pessimistic mutation) is owned by `frontend-data` — see that
skill's `references/destructive-actions.md`.
