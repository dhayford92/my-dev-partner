# Destructive actions (delete / deactivate / remove)

**Canonical = pessimistic + confirm + invalidate. No optimism, no undo** unless the owner asks.

## The pattern (generate this)

A dedicated `Delete<Resource>` component owns the mutation; the parent owns the open state +
selected row.

```tsx
"use client";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { deleteProject } from "@/lib/actions/projects";
import { queryKeys } from "@/lib/constants/query-keys";
import { getErrorMessage } from "@/lib/actions/types";

export function DeleteProject({ id, name, open, onOpenChange }: {
  id: string; name: string; open: boolean; onOpenChange: (o: boolean) => void;
}) {
  const qc = useQueryClient();
  const { mutate, isPending } = useMutation({
    mutationFn: () => deleteProject(id),
    onSuccess: async (result) => {
      if (result.error) { toast.error(result.error); return; }
      await qc.invalidateQueries({ queryKey: queryKeys.projects.list() });
      toast.success("Project deleted");
      onOpenChange(false);
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  });

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      variant="destructive"
      title="Delete project"
      description={`Delete "${name}"? This also removes its data sources, datasets, visualizations, and reports. This cannot be undone.`}
      confirmLabel="Delete project"
      isLoading={isPending}
      onConfirm={() => mutate()}
    />
  );
}
```

`ConfirmDialog` (shadcn `AlertDialog` wrapper) already: shows the destructive icon, disables both
buttons while `isLoading`, swaps the confirm label to "Processing…". Regenerate it from
`app/components/ui/confirm-dialog.tsx` if the project lacks it.

## Cascading UI updates

- Invalidate the resource's own `list()` **and** every dependent domain's `list()` the delete
  cascades to (e.g. deleting a project → invalidate `projects.list`, `dataSources.list`,
  `datasets.list`, `reports.list`).
- If a detail page is open for the deleted resource, `router.push` back to the list after success.
- Remove any `detail(id)` cache entry: `qc.removeQueries({ queryKey: queryKeys.projects.detail(id) })`.

## Deactivate / soft-remove

Same flow, non-destructive `variant="default"` (amber, not red), label "Deactivate". The action
hits a `PATCH .../deactivate` (or `DELETE` for soft delete) and invalidates `list()` + `detail(id)`
so status flips in place.

## Opt-in: optimistic delete + rollback

Only when the owner explicitly wants instant feedback (e.g. removing a chip from a long list).
Snapshot, cancel in-flight, optimistically remove, roll back on error, settle by invalidating.
Note: the `useMutation` callbacks receive `queryClient` from the closure — never call
`useQueryClient()` inside them.

```tsx
const qc = useQueryClient();
const { mutate } = useMutation({
  mutationFn: () => deleteTag(id),
  onMutate: async () => {
    const key = queryKeys.tags.list();
    await qc.cancelQueries({ queryKey: key });
    const previous = qc.getQueryData<Tag[]>(key);
    qc.setQueryData<Tag[]>(key, (old) => (old ?? []).filter((t) => t.id !== id));
    return { previous, key };
  },
  onError: (err, _vars, ctx) => {
    if (ctx) qc.setQueryData(ctx.key, ctx.previous);
    toast.error(getErrorMessage(err));
  },
  onSettled: (_d, _e, _v, ctx) => { if (ctx) qc.invalidateQueries({ queryKey: ctx.key }); },
});
```

Undo (rarer): keep the deleted item in the `onSuccess` toast (`toast(..., { action: { label: "Undo",
onClick: () => restore() } })`) and call a restore action; only build it if the backend supports
restore.
