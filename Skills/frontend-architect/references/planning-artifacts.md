# Planning artifact templates

Fill these in. Keep them terse — a plan, not prose.

## 1. Route map

| Route | Group | Layout | Protected | Persona | Notes |
|-------|-------|--------|-----------|---------|-------|
| `/login` | `(auth)` | auth | no | — | redirect to `/portal` if authed |
| `/portal` | `portal` | portal shell | yes | client | home |
| `/portal/<resource>` | `portal` | portal shell | yes | client | list + CRUD |
| `/portal/<resource>/[id]` | `portal` | portal shell | yes | client | detail |
| `/shared/[token]` | — | none | no (token) | public | token-gated view |

## 2. Page inventory (one block per page)

```
Page: /portal/projects
Purpose: list + create/edit/delete projects
Queries:   queryKeys.projects.list({search})  ← getProjects (unwrap-or-throw)
Mutations: createProject / updateProject / deleteProject  → invalidate projects.list
Dialogs:   CrudDialog (create, edit) · ConfirmDialog (delete, destructive)
States:    isLoading → CardSkeleton grid · isError → error screen (retry) · empty → EmptyState
Components: ResourcePageHeader, ProjectCard (custom/portal/projects), ProjectForm
```

## 3. Component tree (per page)

```
ProjectsPage (page.tsx — owns query + dialog state + mutations)
├─ ResourcePageHeader            [ui] title + primaryAction(onClick)
├─ grid
│  └─ ProjectCard[]              [custom] props: project, onEdit(p), onDelete(p)
├─ CrudDialog (create)           [ui] children: ProjectForm(onSubmit)
├─ CrudDialog (edit)             [ui] children: ProjectForm(defaultValues, onSubmit)
└─ ConfirmDialog (delete)        [ui] onConfirm, isLoading
```
Flag: prop-drilling > 2 levels → consider context or composition.

## 4. Data requirements (per page)

| Query/Mutation | Key | Action | Shape | Invalidates | Notes |
|----------------|-----|--------|-------|-------------|-------|
| list | `projects.list(params)` | `getProjects` | `ProjectResponse[]` (unwrap) | — | debounced search |
| create | — | `createProject` | `ActionResult<Project>` | `projects.list` | toast on `.error` |
| delete | — | `deleteProject` | `ActionResult<void>` | `projects.list` | pessimistic + ConfirmDialog |

## 5. State boundaries

| State | Classification | Where | Justification |
|-------|----------------|-------|---------------|
| project list | server cache | TanStack Query | API data |
| active team / profile | global client | React Context | needed app-wide, hydrated from server |
| dialog open, selected row | local | `useState` in page | page-scoped |

Rule: new global Context needs an explicit reason. Default is server-cache or local.

## 6. API consumption map

| Endpoint | Mount | Pages | Request | Response type | Errors / pagination |
|----------|-------|-------|---------|---------------|---------------------|
| `GET /projects` | core | projects | `?search&page&limit` | `PaginatedResponse<ProjectResponse>` | `toPaginated`; 401→login |
| `POST /projects` | core | projects | `CreateProjectInput` | `ProjectResponse` | 422→field errors |
| `DELETE /projects/{id}` | core | projects | — | `SuccessResponse` | 404→toast |

Cite `../../_shared-backend/response-contract.md` for envelope shapes and `../../_shared-web/api-contract.md`
for the real (divergent) backend reality + normalizer.
