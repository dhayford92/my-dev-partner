---
name: project-context
description: >-
  Own and continuously maintain the per-project context PRD under .claude/context/ (OVERVIEW,
  ARCHITECTURE, SCHEMA, API, DECISIONS/ADR log, CHANGELOG) so any AI or teammate can understand
  the project without reading the codebase. Creates the context on project start, and — this is
  the core rule — updates the affected context file(s) as PART OF THE SAME task that changed the
  code, never as a separate pass. Keeps files diff-friendly and factual, never lets context
  drift from code, and flags when reality and the docs disagree. Includes a verify mode that
  audits the context against the actual models/routers and reports staleness. USE THIS whenever
  starting a project, and after ANY change to models, endpoints, architecture, integrations, or
  decisions — updating context is not optional and not deferred. Also use to bootstrap context
  for an existing project or to run a staleness audit.
---

# project-context

Own the project's living context so it never drifts from the code. The context lives in
`.claude/context/` and is the source any AI reads to understand the project **without** opening
the codebase.

## The files

**One project, one context — all surfaces.** A repo spanning backend, web frontend, and/or mobile
has a single `.claude/context/`; `ARCHITECTURE.md` and `API.md` each carry a section per surface
present.

```
.claude/context/
├── OVERVIEW.md      product purpose, users, core flows (surface-agnostic)
├── ARCHITECTURE.md  BACKEND: system design, jobs, integrations, data flow
│                    WEB: page/route map, component tree, state boundaries, data-fetch flow
│                    MOBILE: screen/nav map, offline/push strategy, native capabilities
├── SCHEMA.md        current DB schema + relations (must match the models)
├── API.md           endpoint inventory + contracts (must match routers) AND, per endpoint,
│                    which web page/hook AND/OR mobile screen/action consumes it
├── COMPONENTS.md    (optional) web component/page inventory — add when the web section of
│                    ARCHITECTURE.md gets unwieldy
├── SCREENS.md       (optional) mobile screen/navigation inventory — same trigger, mobile side
├── DECISIONS.md     ADR log — decision, alternatives, rationale, date (all surfaces)
└── CHANGELOG.md     append-only record of changes, newest first, absolute dates
```

## The non-negotiable rule
**When you change code, update the affected context file(s) in the SAME task — never as a
separate pass the user must request.**

| You changed… | Update… |
|--------------|---------|
| a model / migration | `SCHEMA.md` (+ `CHANGELOG.md`) |
| a route / controller contract | `API.md` backend section (+ `CHANGELOG.md`) |
| a backend service / integration / job | `ARCHITECTURE.md` backend section (+ `CHANGELOG.md`) |
| a page / route / major component / state boundary (web) | `ARCHITECTURE.md` web section or `COMPONENTS.md` (+ `CHANGELOG.md`) |
| a screen / nav change / offline or push strategy (mobile) | `ARCHITECTURE.md` mobile section or `SCREENS.md` (+ `CHANGELOG.md`) |
| how a surface consumes an endpoint (new hook/action, new page/screen calling it) | `API.md` (the consumer column, web and/or mobile) (+ `CHANGELOG.md`) |
| product purpose / persona / flow | `OVERVIEW.md` (+ `CHANGELOG.md`) |
| a non-obvious choice (or reversal), any surface — including a deliberate mobile-vs-web divergence | `DECISIONS.md` (new ADR) + `CHANGELOG.md` |

Every code-changing task ends with: "which context file did this touch?" If the answer is
"none," say why. If you can't update it in the same task, say so explicitly — don't silently skip.

## Initialize (project start)
```powershell
python .\scripts\init_context.py --project "D:\...\my-api" --name "My API"
# web frontend repo → also scaffold the component inventory file:
python .\scripts\init_context.py --project "D:\...\app" --name "App" --with-frontend
# mobile repo → also scaffold the screen inventory file:
python .\scripts\init_context.py --project "D:\...\mobile-app" --name "App" --with-mobile
# a repo with both:
python .\scripts\init_context.py --project "D:\...\monorepo" --name "App" --with-frontend --with-mobile
```
Creates `.claude/context/` from the templates (auto-detects the name from `.env` `APP_NAME`).
`--with-frontend` additionally creates `COMPONENTS.md`; `--with-mobile` additionally creates
`SCREENS.md`. The `ARCHITECTURE.md`/`API.md` templates already carry web AND mobile sections, so
no extra flags are needed for those regardless of which surfaces the project has — just fill in
the sections that apply and leave the rest as "N/A, no such surface."
Idempotent — won't clobber existing files without `--force`. Then fill `OVERVIEW.md` first (it
can't be derived from code), and populate `SCHEMA.md`/`API.md` from the current models/routers.

## Verify (audit staleness)
```powershell
python .\scripts\verify_context.py --project "D:\...\my-api"   # add --strict for CI exit code
```
Reads the real models + routers and reports:
- context files missing,
- **tables in code not documented in `SCHEMA.md`**,
- **routes in code not documented in `API.md`**,
- CHANGELOG staleness (code changed after the last entry).

Run it after a batch of changes, before a handoff, or whenever you suspect drift. See
[references/verify-mode.md](references/verify-mode.md) for what it can and can't catch.

## Writing rules
- **Factual and current**, not aspirational. Document what IS, not what's planned (plans go in
  OVERVIEW "out of scope" or a DECISION).
- **Diff-friendly**: short lines, tables, one fact per row — so updates are small diffs.
- **Match the code exactly**: table names identical to `Meta.table`; paths identical to the
  router prefixes.
- **Flag disagreements**: if the code contradicts the context (e.g. a column the docs don't
  mention, or vice-versa), surface it to the user — don't quietly "fix" the docs to match a
  possibly-wrong code change, or vice-versa. See [references/keeping-in-sync.md](references/keeping-in-sync.md).

## Web frontend sections — what goes where

- **`ARCHITECTURE.md` (web section):** route/page map (groups, protection), the component tree for
  major pages (3-tier: `ui`/`page`/`custom`), state boundaries (server-cache vs React context vs
  local), and the data-fetch flow (`apiFetch → server action → TanStack`). Mirror the shape
  `frontend-architect` produces.
- **`API.md` (consumer column):** for each endpoint, record which web page/hook calls it and the
  `lib/models` response type it maps to. Flag any endpoint the web frontend consumes with a
  response shape that doesn't match the backend (the error/pagination drift is a live example).
- **`COMPONENTS.md`:** only when the web section of `ARCHITECTURE.md` outgrows it — a full
  component/page inventory (page → components → data sources → dialogs/states).

## Mobile sections — what goes where

- **`ARCHITECTURE.md` (mobile section):** screen/route map (route groups, the confirmed
  root-only auth-gate reality — don't overstate guard coverage that isn't there), the 3-tier
  component breakdown (`ui`/`pages`/`custom`), state boundaries, the throw-or-return data-fetch
  flow, offline strategy, and push-notification strategy (invalidation + routing per type — see
  `../_shared-mobile/native.md`). Mirror the shape `mobile-architect` produces.
- **`API.md` (consumer column):** for each endpoint, record which mobile screen/action calls it
  and the `services/models` response type — alongside the web consumer column, so the doc shows
  the contract from every surface that touches it. Flag any endpoint where mobile's `apiFetch`
  normalizer handling diverges from what web or the backend actually returns.
- **`SCREENS.md`:** only when the mobile section of `ARCHITECTURE.md` outgrows it — a full
  screen/navigation inventory (screen → components → data sources → sheets/states → native
  capabilities used).
- **Mobile-vs-web divergences:** where mobile intentionally differs from web for platform reasons
  (e.g. no dark mode, no `ActionResult` wrapper, `expo-secure-store` instead of cookies), note the
  divergence in `DECISIONS.md` if it's non-obvious — don't let it look like an oversight.

## Relationship to other skills
- `backend-architect` produces the initial backend `ARCHITECTURE.md` + seeds `DECISIONS.md`;
  `frontend-architect` produces the web sections; `mobile-architect` produces the mobile sections
  (page/screen/component/state plan for each).
- `backend-database` / `backend-api-design` changes → `SCHEMA.md` / `API.md`; `frontend-components`
  / `frontend-data` changes → `ARCHITECTURE.md` web section / `COMPONENTS.md` / `API.md` consumer
  column; `mobile-components` / `mobile-data` changes → `ARCHITECTURE.md` mobile section /
  `SCREENS.md` / `API.md` consumer column — all in the same task (this skill enforces that).
- Backend conventions live in `../_shared-backend/`; web frontend conventions in
  `../_shared-web/`; mobile conventions in `../_shared-mobile/`. Conventions
  never go in per-project context.

Details: [references/maintenance-workflow.md](references/maintenance-workflow.md).
