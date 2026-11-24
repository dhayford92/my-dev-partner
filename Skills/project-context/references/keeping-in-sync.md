# Keeping context in sync with code

The context is only useful if it's true. Two failure modes to prevent: **drift** (code moves,
docs don't) and **false convergence** (docs "fixed" to match a wrong code change, or vice-versa).

## Update in the same task
The single most important habit: the diff that changes a model/route/component also changes the
matching context file. If they're separate commits/tasks, drift creeps in. Never answer "I'll
update the docs later."

## When code and context disagree — STOP and flag
If you find the code contradicts the context (a column the docs don't mention, a route the docs
say is admin-only but the guard is `CurrentUser`, an integration the docs claim that isn't
wired), do **not** silently rewrite the docs to match, and do **not** assume the code is right.

Surface it:
> "`API.md` documents `DELETE /core/api/v1/admin/examples/{id}` as super-admin only, but
> `example_router.py` guards it with `CurrentAdminUser`. Which is correct — should I tighten the
> guard or update the doc?"

The context might be recording an intended invariant the code violates (a bug), or the code
moved and the doc is stale. Only the user knows which. Fix the actual discrepancy, then sync.

## Documenting reality, not intentions
`SCHEMA.md`/`API.md`/`ARCHITECTURE.md` describe what IS built and running. Planned work goes in
`OVERVIEW.md` "out of scope" or a `DECISIONS.md` ADR marked `proposed`. This keeps the "reads
like the running system" guarantee.

## Removed things
`verify_context.py` catches code→docs gaps (undocumented tables/routes) but not docs→code
staleness (a table you deleted, still in `SCHEMA.md`). When you delete a model/route, remove its
context entry in the same task, and note the removal in `CHANGELOG.md`.

## After a big change / handoff
1. `verify_context.py` → resolve every drift item.
2. Skim `OVERVIEW.md` + `ARCHITECTURE.md` for now-false statements.
3. Confirm the newest `CHANGELOG.md` entry reflects the latest work.
