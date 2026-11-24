# Loading state templates (mobile)

## Query gating (the standard block)

```tsx
if (query.isLoading) return <Skeleton className="h-20 w-full" />;
if (query.isError)   return <ErrorState message={getErrorMessage(query.error)} retry={() => query.refetch()} />;
if (items.length === 0) return <EmptyState title="Nothing here yet" />;
return <FlatList data={items} ... />;
```

## List skeleton (mirror the real row shape)

```tsx
{query.isLoading ? (
  <View className="gap-3">
    {Array.from({ length: 5 }).map((_, i) => (
      <View key={i} className="flex-row items-center gap-3 rounded-2xl border border-ink-100 p-4">
        <Skeleton className="h-10 w-10 rounded-full" />
        <View className="flex-1 gap-2">
          <Skeleton className="h-3 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </View>
      </View>
    ))}
  </View>
) : (
  <FlatList data={items} ... />
)}
```

## Feature-specific skeleton screen (confirmed pattern, both apps)

For a screen with a distinctive layout (header + card + list), write a bespoke
`*-loading-screen.tsx` that skeletons that exact shape, composed from the `Skeleton` primitive —
same convention as web's bespoke loading screens.

## Button/mutation inline

```tsx
<Button label={mutation.isPending ? "Saving…" : "Save"} loading={mutation.isPending} onPress={onSubmit} />
```

For an operation with no meaningful button (e.g. a background sync trigger), use `ActivityIndicator`:

```tsx
{isPending ? <ActivityIndicator size="small" /> : null}
```

## Pull-to-refresh & pagination

Not present in either reference app today — add deliberately when a screen needs it, matching
this shape:

```tsx
const q = useInfiniteQuery({
  queryKey: queryKeys.requests.list("current"),
  queryFn: ({ pageParam }) => listRequests({ page: pageParam, limit: 20 }),
  initialPageParam: 1,
  getNextPageParam: (lastPage) =>
    lastPage.current_page * lastPage.page_limit < lastPage.total_count
      ? lastPage.current_page + 1
      : undefined,
});

<FlatList
  data={q.data?.pages.flatMap((p) => p.data) ?? []}
  keyExtractor={(r) => r.id}
  renderItem={renderItem}
  refreshControl={<RefreshControl refreshing={q.isRefetching} onRefresh={() => q.refetch()} />}
  onEndReached={() => q.hasNextPage && q.fetchNextPage()}
  onEndReachedThreshold={0.4}
  ListFooterComponent={q.isFetchingNextPage ? <ActivityIndicator className="py-4" /> : null}
/>
```

## Detail-route not-found

```tsx
if (query.isError && (query.error as ApiError)?.status === 404) {
  return <EmptyState title="Not found" description="This item doesn't exist or was removed." action={{ label: "Go back", onPress: () => router.back() }} />;
}
```
