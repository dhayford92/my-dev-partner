# Loading state templates

All from `components/ui/states.tsx`. Match the skeleton to the real layout to avoid shift.

## Query gating (the standard block)

```tsx
if (query.isLoading) return <ListSkeleton count={6} />;
if (query.isError)   return <ErrorState error={getErrorMessage(query.error)} retry={{ onClick: () => query.refetch() }} />;
if (items.length === 0) return <EmptyState icon={InboxIcon} title="Nothing here yet" description="Create your first one." action={{ label: "Create", onClick: openCreate }} />;
return <List items={items} />;
```

## Card grid loading (mirror the real grid)

```tsx
{query.isLoading ? (
  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
    {Array.from({ length: 8 }).map((_, i) => <CardSkeleton key={i} />)}
  </div>
) : ( /* real grid, same classes */ )}
```

## Table loading

```tsx
<div className="divide-y rounded-md border">
  {Array.from({ length: pageSize }).map((_, i) => <TableRowSkeleton key={i} columns={columns.length} />)}
</div>
```

## Bespoke loading screen (feature-specific)

When a page has a distinctive layout (detail header + tabs + chart), write a
`*-loading-screen.tsx` that skeletons that exact shape rather than a generic list. Keep it in the
feature's `_components/`. Compose from `Skeleton` + the `states.tsx` skeleton helpers.

## Button / mutation inline

```tsx
<Button type="submit" disabled={mutation.isPending}>
  {mutation.isPending ? "Saving..." : "Save changes"}
</Button>
```
Never overlay a spinner on a form; swap the label + disable.

## Detail route not-found

Detail query 404 → render `NotFoundState` (not `ErrorState`):

```tsx
if (query.isError && (query.error as ApiError)?.status === 404)
  return <NotFoundState action={{ label: "Back to list", onClick: () => router.push("/portal/projects") }} />;
```
