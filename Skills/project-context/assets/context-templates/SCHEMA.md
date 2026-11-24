# Database Schema — {{PROJECT_NAME}}

> Current tables, key columns, relations, and indexes. This must match the Tortoise models
> exactly. Update in the same task as any model/migration change. `verify` mode diffs this
> file against the models and flags drift.

## Tables
<!-- One row per table. Keep table names identical to `class Meta: table = "..."`. -->

### `<table_name>`
<!-- purpose -->
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| ... | | |
| created_at / updated_at | timestamptz | UTC |
| deleted_at | timestamptz? | soft delete |

**Relations:** <!-- FKs / M2M, with related_names -->
**Indexes:** <!-- indexed columns, unique constraints, composite indexes -->

<!-- Repeat per table. -->

## Enums
<!-- StrEnums used by CharEnumField columns. -->

_Last updated: {{DATE}}_
