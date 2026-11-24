# Components — {{PROJECT_NAME}}

> Frontend component/page inventory. Create this file only when the frontend section of
> ARCHITECTURE.md gets too large. Update in the same task as any page/major-component change.
> Conventions: ../../../_shared-web/ in the Skills library. Delete this file if the project has no frontend.

## Page inventory
<!-- Per page: route, purpose, data sources (server actions), mutations, dialogs, states. -->

### <page name> — `/portal/<route>`
- **Data:** `queryKeys.<domain>.list(...)` ← `get<Domain>` (unwrap-or-throw)
- **Mutations:** `create<Domain>` / `update<Domain>` / `delete<Domain>` → invalidate `<domain>.list`
- **Dialogs:** CrudDialog (create/edit) · ConfirmDialog (delete)
- **States:** loading (skeleton) · error (ErrorState + retry) · empty (EmptyState)
- **Components:** ResourcePageHeader, `<Domain>Card` (custom/<domain>), `<Domain>Form`

## Shared UI extensions (`components/ui/`)
<!-- Owner-built extensions beyond raw shadcn: confirm-dialog, crud-dialog, data-table,
     resource-page-header, states, card-grid, details-sheet, the InputField field family. -->
| Component | Purpose |
|-----------|---------|
| | |

## Providers / global state
<!-- React contexts (team/profile/etc.), what they hold, where hydrated. -->

_Last updated: {{DATE}}_
