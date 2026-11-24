# Data Layer — Canonical

The data flow is a **three-stage pipeline**. Learn the boundary; it is the most-misunderstood
part of this stack.

```
apiFetch (HTTP client, attaches Bearer)  →  lib/actions/* ("use server", returns ActionResult<T>)  →  raw useQuery/useMutation (client, queryKeys factory)
```

The custom layer that TanStack Query does NOT give you is stages 1–2: a fetch client that
auto-attaches the auth cookie server-side, plus a typed `{data,error}` server-action envelope.
Stage 3 is **plain TanStack Query** — no wrapper.

> ❌ **Deprecated, do not generate:** `hooks/useApi.ts` (`useApiQuery`/`useApiMutation`) and
> `hooks/useAsyncData.ts`. The owner's own note marks `useApi` as "optional"; it never won
> adoption and `useAsyncData` has no caching. Canonical is **raw `useQuery`/`useMutation`**.

## Stage 1 — the fetch client (`hooks/apiFetch.ts`)

A plain async function (not a React hook). Attaches the Bearer token from httpOnly cookies when
`autoAuth: true`, and normalizes errors via [api-contract.md](api-contract.md). Used only inside
`"use server"` actions.

```ts
export interface RequestConfig {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  url: string;
  params?: Record<string, string | number | boolean | undefined | null>;
  data?: unknown;
  token?: string;
  contentType?: "application/json" | "multipart/form-data";
  autoAuth?: boolean;   // true → pull access token from cookies (server actions)
}
```

Rules: `multipart/form-data` → do NOT set `Content-Type` (let fetch set the boundary); `204` →
return `null`; on non-2xx **throw a normalized `ApiError`** (see api-contract.md), never a bare
`Error`. This is the one fix over today's repos, which throw `result.detail || result.message` —
the normalizer instead yields a typed `ApiError` carrying the HTTP status and parsed 422 field
errors. This frontend branches on **HTTP status** and does not consume the backend's `X-Error-Code`
header (an intentional client choice — see api-contract.md).

## Stage 2 — server actions (`lib/actions/{domain}.ts`)

`"use server"` modules. Each function calls `apiFetch`, unwraps the backend body, and returns a
canonical **`ActionResult<T>`** (`lib/actions/types.ts`):

```ts
export type ActionResult<T> =
  | { data: T; error: null }
  | { data: null; error: string };

export const success = <T>(data: T): ActionResult<T> => ({ data, error: null });
export const failure = <T>(error: string): ActionResult<T> => ({ data: null, error });
```

Pattern (from `app/lib/actions/auth.ts`):

```ts
"use server";
export async function getProjects(params?: { search?: string }): Promise<ActionResult<ProjectResponse[]>> {
  try {
    const res = await apiFetch<PaginatedResponse<ProjectResponse>>({
      method: "GET", url: API_URLS.CORE.PROJECTS.LIST, params, autoAuth: true,
    });
    return success(res.data);                     // unwrap pagination envelope → items
  } catch (error) {
    return failure(error instanceof Error ? error.message : "Failed to load projects");
  }
}
```

Auth actions additionally set/clear cookies (see [api-contract.md](api-contract.md#auth--tokens)).

## Stage 3 — client consumption (raw TanStack Query)

**Queries** (from `app/app/portal/projects/page.tsx`):

```tsx
const projectsQuery = useQuery({
  queryKey: [...queryKeys.projects.list(), { search: debouncedSearch }],
  queryFn: () => getProjects({ search: debouncedSearch || undefined }),
});
const projects = projectsQuery.data ?? [];
```

**Mutations** — check `result.error` inline, toast, invalidate:

```tsx
const queryClient = useQueryClient();
const createMutation = useMutation({
  mutationFn: createProject,
  onSuccess: async (result) => {
    if (result.error) { toast.error(result.error); return; }
    await queryClient.invalidateQueries({ queryKey: queryKeys.projects.list() });
    toast.success("Project created successfully");
  },
});
```

> Server actions return `ActionResult`, so `queryFn`/`mutationFn` resolve even on API failure.
> A query's `queryFn` should therefore **unwrap and throw** if you want `isError` to fire, OR
> return the whole `ActionResult` and read `.error`. Canonical: actions used in `useQuery`
> return the **unwrapped data or throw** (so `isError`/`isLoading` work); actions used in
> `useMutation` return `ActionResult` and the `onSuccess` checks `.error`. Keep it consistent
> per action and document which it is.

## Query keys — factory (`lib/constants/query-keys.ts`)

Hierarchical factory. **Named export `queryKeys`.** Every cache read/write/invalidate goes
through it — never inline string arrays.

```ts
export const queryKeys = {
  projects: {
    all: ['projects'] as const,
    list: (params?: Record<string, unknown>) => [...queryKeys.projects.all, 'list', params] as const,
    detail: (id: string) => [...queryKeys.projects.all, 'detail', id] as const,
  },
  // teams, datasets, ... same shape: all / list(params) / detail(id)
} as const;
```

## QueryClient provider (`providers/query-provider.tsx`) — SSR-singleton

```tsx
'use client'
import { isServer, QueryClient, QueryClientProvider } from '@tanstack/react-query'

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { staleTime: 60_000 } } })
}
let browserQueryClient: QueryClient | undefined
function getQueryClient() {
  if (isServer) return makeQueryClient()
  return (browserQueryClient ??= makeQueryClient())
}
export default function QueryProvider({ children }: { children: React.ReactNode }) {
  return <QueryClientProvider client={getQueryClient()}>{children}</QueryClientProvider>
}
```

## Endpoint constants (`lib/constants/api-urls.ts`)

Centralized. Mirrors the backend's mount split (`/users`, `/core`, `/utils`) + `/api/v1`. Build
full URLs with a helper; expose grouped constants (`API_URLS.AUTH.LOGIN`,
`API_URLS.CORE.PROJECTS.DETAIL(id)`). Cookie names are namespaced (`<app>_access_token`). Base
URL from `process.env.NEXT_PUBLIC_API_URL` — **not hardcoded** (today's repos hardcode prod; the
scaffold fixes this).

## State boundaries

- **Server cache** → TanStack Query (all API data).
- **Global client state** → React Context, **sparingly** (e.g. `UserTeamProvider` for
  team/profile/usage, hydrated from server props, synced on `router.refresh`). No Zustand/Redux.
- **Local UI state** → `useState`.
