# Authorization models

Authorization is **project-dependent**. Pick ONE model per project; don't mix silently.

## (a) Persona guards — DEFAULT
`user_type` in the JWT + `Current<Persona>User` dependencies (in `libs/auth.py`, ships with
scaffold). Super-admin re-checks the admin model's `role` enum. No permission table.

Use for: B2C apps, simple admin consoles.

```python
@router.get("/admin/users", ...)
async def list_users(auth: CurrentAdminUser): ...     # 403 if not an admin
```

## (b) Org-scoped JSON RBAC — opt-in
For B2B where each organization configures roles. Assets in `assets/rbac/`.

**Model** (`role_model.py`): `UserRoleModel` with `permissions = {module: {read, write,
delete}}` (JSON), scoped to an `organization` FK, `unique_together=(organization, name)`, M2M
to users, `has_permission(module, action)`. `DEFAULT_ROLE_LIST` for seeding.

**Check** (`permission_checks.py`): authorization is data-driven, so it runs **inside the
controller** (a route dependency can't know the module/action for every handler):

```python
class ComplianceController:
    @staticmethod
    async def update(item_id, body, email, request):
        perm = await UserPermissionChecks.has_client_user_permission(email, "compliance", "write")
        if not perm:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permission")
        org_id = perm["organization_id"]
        item = await ComplianceModel.get_or_none(id=item_id, organization_id=org_id)  # ALWAYS scope
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not found")
        ...
```

**Rules:**
- The route still carries a persona guard (`CurrentClientUser`) to prove *who*; the controller
  check proves *what they may do*.
- **Always scope every query by the returned `organization_id`** — this is the tenant boundary.
- Seed roles per org with `seed_rbac.py`.

Wire: register `role_model` in `ORM_MODELS`; drop `permission_checks.py` into
`services/auth/`; add the `roles` M2M + `organization` FK to your user model; migrate.

## (c) Team + Postgres RLS — opt-in
For multi-tenant SaaS. Assets in `assets/rls/`.

- JWT carries `team_id`; the auth dependency puts it on `AuthContext`.
- **Every platform query filters by `team_id`.**
- **Postgres RLS** enforces isolation at the DB even if a query forgets: define policies in a
  migration and call `set_rls_context(user_id, team_id)` inside the request transaction.

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY team_isolation ON orders
    USING (team_id = current_setting('app.team_id', true)::uuid);
```
```python
async with in_transaction():
    await set_rls_context(str(auth.user_id), str(auth.team_id))
    rows = await OrderModel.filter(team_id=auth.team_id)   # belt-and-suspenders
```

`SET LOCAL` is transaction-scoped, so set the context inside the same transaction as the
queries. Admin portal routes use a **separate** portal JWT and have **no** team scope — see
[portal-access.md](portal-access.md).

## Choosing
| Signal | Model |
|--------|-------|
| One user type or a few fixed personas | (a) persona guards |
| Customers configure roles per organization | (b) JSON RBAC |
| Strict tenant isolation, DB-enforced | (c) team + RLS |

Surface the choice and confirm it before building auth (structural decision — see
`dev-partner`). Encode the answer in `.claude/context/DECISIONS.md` via `project-context`.
