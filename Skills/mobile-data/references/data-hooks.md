# Data layer templates (generate verbatim)

## 1. Endpoint constants (`libs/api-urls.ts`)

```ts
export const CORE_URLS = {
  RECIPIENTS: {
    LIST: buildUrl("/recipients", "core"),
    CREATE: buildUrl("/recipients", "core"),
    DETAIL: (id: string) => buildUrl(`/recipients/${id}`, "core"),
    DELETE: (id: string) => buildUrl(`/recipients/${id}`, "core"),
  },
} as const;
```

## 2. Response type (`services/models/recipient.ts`)

```ts
export interface RecipientResponse {
  id: string;
  full_name: string;
  payout_type: string;
  created_at: string;
}
```

## 3. Zod schema (`services/schemas/recipient.ts`)

```ts
import { z } from "zod";
export const createRecipientSchema = z.object({
  full_name: z.string().min(1, "Name is required"),
  payout_type: z.enum(["bank", "mobile_money", "cash_pickup"]),
});
export type CreateRecipientInput = z.infer<typeof createRecipientSchema>;
```

## 4. Service action (`services/actions/recipient_actions.ts`)

```ts
import apiFetch from "@/hooks/apiFetch";
import { API_URLS } from "@/libs/api-urls";
import type { RecipientResponse } from "@/services/models/recipient";
import type { CreateRecipientInput } from "@/services/schemas/recipient";

// Throw-or-return — no ActionResult wrapper. Same convention for query AND mutation actions.
export async function getRecipients(): Promise<RecipientResponse[]> {
  const body = await apiFetch<{ data: RecipientResponse[] }>({
    method: "GET",
    url: API_URLS.CORE.RECIPIENTS.LIST,
    autoAuth: true,
  });
  return body.data;
}

export async function createRecipient(input: CreateRecipientInput): Promise<RecipientResponse> {
  return apiFetch<RecipientResponse>({
    method: "POST",
    url: API_URLS.CORE.RECIPIENTS.CREATE,
    data: input,
    contentType: "application/json",
    autoAuth: true,
  });
}

export async function deleteRecipient(id: string): Promise<void> {
  await apiFetch<void>({ method: "DELETE", url: API_URLS.CORE.RECIPIENTS.DETAIL(id), autoAuth: true });
}
```

## 5. Query keys (`libs/query_keys.ts`)

```ts
recipients: {
  all: ["recipients"] as const,
  list: () => [...queryKeys.recipients.all, "list"] as const,
  detail: (id: string) => [...queryKeys.recipients.all, "detail", id] as const,
},
```

## 6. Consuming

```tsx
// list
const { data, isLoading, isError, refetch } = useQuery({
  queryKey: queryKeys.recipients.list(),
  queryFn: getRecipients,
});

// create
const queryClient = useQueryClient();
const createMutation = useMutation({
  mutationFn: createRecipient,
  onSuccess: async () => {
    await queryClient.invalidateQueries({ queryKey: queryKeys.recipients.list() });
    show({ type: "success", message: "Recipient added." });
    setCreateOpen(false);
  },
  onError: (error) => show({ type: "error", message: getErrorMessage(error) }),
});

// 422 field-error mapping
const editMutation = useMutation({
  mutationFn: (input: CreateRecipientInput) => updateRecipient(id, input),
  onError: (error) => {
    if (error instanceof ApiError && error.fieldErrors) {
      error.fieldErrors.forEach(({ field, message }) => form.setError(field as never, { message }));
    } else {
      show({ type: "error", message: getErrorMessage(error) });
    }
  },
});
```

## Paginated list

```ts
export interface Paginated<T> { data: T[]; current_page: number; page_limit: number; total_count: number }

export async function listRequests(params: { page: number; limit: number }): Promise<Paginated<RequestResponse>> {
  return apiFetch<Paginated<RequestResponse>>({
    method: "GET", url: API_URLS.CORE.REQUESTS.LIST, params, autoAuth: true,
  });
}
```
```tsx
const q = useQuery({
  queryKey: queryKeys.requests.list("current"),
  queryFn: () => listRequests({ page: 1, limit: 50 }),
});
// FlatList — not FlashList (neither reference app uses it). onEndReached for infinite scroll
// if a screen needs it; neither app currently implements pagination-on-scroll, so treat it as
// new per-screen work, not an extraction.
<FlatList
  data={q.data?.data ?? []}
  keyExtractor={(r) => r.id}
  renderItem={({ item }) => <RequestCard request={item} />}
  onEndReachedThreshold={0.4}
/>
```
