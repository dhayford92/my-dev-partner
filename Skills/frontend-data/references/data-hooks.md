# Data layer templates (generate verbatim)

## 1. Endpoint constants (`lib/constants/api-urls.ts`)

```ts
export const CORE_URLS = {
  PROJECTS: {
    LIST: buildUrl("/projects", "core"),
    CREATE: buildUrl("/projects", "core"),
    DETAIL: (id: string) => buildUrl(`/projects/${id}`, "core"),
  },
} as const;
```

## 2. Response type (`lib/models/project.ts`)

Mirrors the backend response schema — snake_case, ISO timestamps.

```ts
export interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  border_color: string | null;
  created_at: string;
  updated_at: string;
}
```

## 3. Zod schema (`lib/schemas/project.ts`)

```ts
import { z } from "zod";
export const projectSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  description: z.string().optional(),
  border_color: z.string().optional(),
});
export type ProjectInput = z.infer<typeof projectSchema>;
```

## 4. Server actions (`lib/actions/projects.ts`)

```ts
"use server";
import apiFetch from "@/hooks/apiFetch";
import { API_URLS } from "@/lib/constants/api-urls";
import { toPaginated } from "@/lib/actions/pagination";
import { type ActionResult, success, failure, getErrorMessage } from "@/lib/actions/types";
import type { ProjectResponse } from "@/lib/models/project";
import type { ProjectInput } from "@/lib/schemas/project";

// READ (used in useQuery): unwrap-or-throw so isLoading/isError work.
export async function getProjects(params?: { search?: string; page?: number; limit?: number }): Promise<ProjectResponse[]> {
  const body = await apiFetch<unknown>({ method: "GET", url: API_URLS.CORE.PROJECTS.LIST, params, autoAuth: true });
  return toPaginated<ProjectResponse>(body).data;
}

export async function getProject(id: string): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>({ method: "GET", url: API_URLS.CORE.PROJECTS.DETAIL(id), autoAuth: true });
}

// WRITE (used in useMutation): return ActionResult.
export async function createProject(input: ProjectInput): Promise<ActionResult<ProjectResponse>> {
  try {
    const res = await apiFetch<ProjectResponse>({ method: "POST", url: API_URLS.CORE.PROJECTS.CREATE, data: input, contentType: "application/json", autoAuth: true });
    return success(res);
  } catch (error) { return failure(getErrorMessage(error)); }
}

export async function deleteProject(id: string): Promise<ActionResult<void>> {
  try {
    await apiFetch({ method: "DELETE", url: API_URLS.CORE.PROJECTS.DETAIL(id), autoAuth: true });
    return success(undefined as void);
  } catch (error) { return failure(getErrorMessage(error)); }
}
```

## 5. Query keys (`lib/constants/query-keys.ts`)

```ts
projects: {
  all: ["projects"] as const,
  list: (params?: Record<string, unknown>) => [...queryKeys.projects.all, "list", params] as const,
  detail: (id: string) => [...queryKeys.projects.all, "detail", id] as const,
},
```

## 6. Consuming

```tsx
// list
const q = useQuery({ queryKey: queryKeys.projects.list({ search }), queryFn: () => getProjects({ search }) });

// create
const qc = useQueryClient();
const createMutation = useMutation({
  mutationFn: createProject,
  onSuccess: async (result) => {
    if (result.error) { toast.error(result.error); return; }
    await qc.invalidateQueries({ queryKey: queryKeys.projects.list() });
    toast.success("Project created successfully");
  },
});

// form 422 mapping
const editMutation = useMutation({
  mutationFn: (input: ProjectInput) => updateProject(id, input),
  onError: (err) => {
    if (err instanceof ApiError && err.fieldErrors) err.fieldErrors.forEach(({ field, message }) => form.setError(field as never, { message }));
    else toast.error(getErrorMessage(err));
  },
});
```

## Paginated list (with page controls)

Return the whole `Paginated<T>` from the action instead of just `.data`, key the query by page,
use `placeholderData: keepPreviousData` for smooth paging:

```ts
export async function listProjectsPaged(params: { page: number; limit: number; search?: string }): Promise<Paginated<ProjectResponse>> {
  const body = await apiFetch<unknown>({ method: "GET", url: API_URLS.CORE.PROJECTS.LIST, params, autoAuth: true });
  return toPaginated<ProjectResponse>(body);
}
```
```tsx
const q = useQuery({
  queryKey: queryKeys.projects.list({ page, search }),
  queryFn: () => listProjectsPaged({ page, limit: 50, search }),
  placeholderData: keepPreviousData,
});
// q.data.total_count / hasNextPage(q.data) drive the pager
```
