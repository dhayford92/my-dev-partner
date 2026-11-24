# Destructive actions (delete / deactivate / remove) — mobile

**Canonical = `ButtonSheet` confirm + pessimistic + stay-signed-in/on-screen on failure.** No
optimistic updates, no undo, unless the owner explicitly asks.

## The pattern (generate this)

```tsx
// app/(others)/more/delete-account.tsx — logic lives directly in the route file
export default function DeleteAccountScreen() {
  const { signOut } = useAuth();
  const { show } = useToster();
  const queryClient = useQueryClient();
  const [showConfirm, setShowConfirm] = useState(false);
  const [reason, setReason] = useState<string | null>(null);

  const deleteMutation = useMutation({
    mutationFn: () => deleteAccount(reason ?? ""),
    onSuccess: async () => {
      queryClient.clear();
      show({ type: "success", message: "Account deleted." });
      await signOut();
      router.replace(ROUTES.AUTH.WELCOME);
    },
    onError: (error) => {
      // Stay signed in / on this screen — a failed delete must NOT look like a successful one.
      show({ type: "error", message: getErrorMessage(error) });
    },
  });

  return (
    <Screen>
      <TopBar title="Delete account" />
      <View className="flex-1 px-5">
        {/* reason picker, warning banner, etc. */}
        <Button
          label="Delete my account"
          variant="secondary"
          disabled={!reason}
          onPress={() => setShowConfirm(true)}
        />
      </View>

      {showConfirm && (
        <ButtonSheet title="Delete account" onClose={() => setShowConfirm(false)}>
          <Text className="text-center text-[15px] text-ink-700">
            This is permanent. All your data will be deleted and cannot be recovered.
          </Text>
          <Button
            label={deleteMutation.isPending ? "Deleting..." : "Yes, delete my account"}
            onPress={() => { selectionFeedback(); deleteMutation.mutate(); }}
            loading={deleteMutation.isPending}
          />
          <Button label="Cancel" variant="secondary" onPress={() => setShowConfirm(false)} disabled={deleteMutation.isPending} />
        </ButtonSheet>
      )}
    </Screen>
  );
}
```

**The confirmed bug NOT to reproduce:** one reference app signs the user out and navigates away
even when `deleteAccount()` throws (comment: *"Continue to sign out locally even if API fails"*).
Don't generate this — a failed delete must leave the user signed in with a clear error, not a
false "success."

## Cascading UI updates

- On a full account/session-ending delete: `queryClient.clear()` (wipes the whole cache — correct
  here, since nothing should survive into whatever session comes next).
- On a partial delete (a recipient, a saved location): `invalidateQueries` the specific domain's
  `list()` **and** `removeQueries({queryKey: queryKeys.<domain>.detail(id)})` if a detail screen
  might still be mounted for that id.
- If a detail screen is currently showing the deleted resource, `router.back()` or
  `router.replace()` to the list after success — don't leave it rendering stale/deleted data.

## Deactivate / soft-remove

Same `ButtonSheet` shell, non-destructive `variant="secondary"` styling (not red), label
"Deactivate". Invalidate `list()` + `detail(id)` so status flips in place rather than the row
disappearing.

## Haptics (sparing)

`selectionFeedback()` on the confirm tap is appropriate for a destructive action — it's one of the
two confirmed real call-site patterns for haptics in this stack (see
`../../_shared-mobile/states-and-motion.md#haptics`). Don't add haptic feedback to every button; reserve it
for meaningful confirms/toggles.

## Opt-in: optimistic delete + rollback

Only when the owner explicitly wants instant feedback (e.g. removing a chip from a list). Snapshot
before mutating, roll back on error, settle by invalidating — same shape as the web suite's opt-in
pattern:

```tsx
const { mutate } = useMutation({
  mutationFn: () => deleteTag(id),
  onMutate: async () => {
    const key = queryKeys.tags.list();
    await queryClient.cancelQueries({ queryKey: key });
    const previous = queryClient.getQueryData<Tag[]>(key);
    queryClient.setQueryData<Tag[]>(key, (old) => (old ?? []).filter((t) => t.id !== id));
    return { previous, key };
  },
  onError: (error, _vars, ctx) => {
    if (ctx) queryClient.setQueryData(ctx.key, ctx.previous);
    show({ type: "error", message: getErrorMessage(error) });
  },
  onSettled: (_d, _e, _v, ctx) => { if (ctx) queryClient.invalidateQueries({ queryKey: ctx.key }); },
});
```
