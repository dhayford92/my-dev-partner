# Skill router

Which skill for which task, plus how they combine. When two apply, the order matters — usually
design/understand before change, change before review.

## By intent

| Intent / phrasing | Skill | Then usually |
|-------------------|-------|--------------|
| "new project", "bootstrap", "spin up an API" | backend-scaffold | project-context (init) |
| "design", "architect", "plan the system", "data model for" | backend-architect | scaffold, then build skills |
| "add endpoint", "API for X", "route/controller", pagination/filtering | backend-api-design | review; project-context (API.md) |
| "new table", "model", "migration", "index", "slow query", "N+1" | backend-database | review; project-context (SCHEMA.md) |
| "login/register/logout", "reset password", "RBAC", "permissions", "tokens", "portal" | backend-auth | security; review |
| "keep docs current", "context", "PRD", "verify context" | project-context | — |
| "map this codebase", "audit architecture", "reverse engineer", "tech debt", "plan a refactor" | backend-reverse-engineer | dev-partner (agree plan); database/api-design for fixes |
| "broken", "failing", "error", "wrong result", "flaky", "500" | backend-debug | review (if fix non-trivial) |
| "review", "check my changes", "is this ready", "look over this PR" | backend-review | security (if auth/payment touched) |
| "security review", "is this secure", "injection/leak/permissions audit" | backend-security | debug (to fix a found hole) |
| "how should we…", a trade-off, "which skill" | dev-partner | the chosen skill |

## Web frontend intents

| Intent / phrasing | Skill | Then usually |
|-------------------|-------|--------------|
| "new frontend", "Next.js app", "bootstrap the UI", "set up the shell" | frontend-scaffold | project-context (init) |
| "plan the pages/components", "component architecture", "state boundaries" | frontend-architect | frontend build skills |
| "build a component", "a form", "modal/dialog", "shadcn", "field" | frontend-components | frontend-review; project-context |
| "fetch data", "query/mutation", "hook for X", "delete/remove flow", "cache" | frontend-data | frontend-review; project-context (API.md) |
| "loading state", "skeleton", "spinner", "animation", "framer", "motion" | frontend-motion | — |
| "map this frontend", "audit the UI", "prop drilling", "refactor the components" | frontend-reverse-engineer | dev-partner (agree plan); frontend build skills |
| "UI is broken", "stale data", "re-render", "hydration", "state desync" | frontend-debug | frontend-review (if fix non-trivial) |
| "review my UI change", "check this component/PR" | frontend-review | — |

## Mobile intents

| Intent / phrasing | Skill | Then usually |
|-------------------|-------|--------------|
| "new mobile app", "Expo app", "React Native project", "bootstrap the app" | mobile-scaffold | project-context (init) |
| "plan the screens/navigation", "offline strategy", "push strategy" | mobile-architect | mobile build skills |
| "build a screen", "a form", "a component", on mobile | mobile-components | mobile-review; project-context |
| "fetch data on mobile", "service action", "delete flow", "cache" (mobile) | mobile-data | mobile-review; project-context (API.md) |
| "loading state", "skeleton", "list", "animation", "haptics" (mobile) | mobile-motion | — |
| "push notifications", "biometric", "camera/location permission", "deep link", "EAS build/update" | mobile-native | mobile-review |
| "map this app", "audit the mobile codebase", "refactor the screens" | mobile-reverse-engineer | dev-partner (agree plan); mobile build skills |
| "app crashes", "native crash", "Expo Go vs build", "stale after reload" | mobile-debug | mobile-review (if fix non-trivial) |
| "review my mobile change", "check this PR" (mobile) | mobile-review | — |

## Conventions are shared, not per-skill
Every backend code-generating skill points to `../../_shared-backend/` for conventions; every web
frontend skill points to `../../_shared-web/`; every mobile skill points to
`../../_shared-mobile/`. If a convention question comes up mid-task, the answer is in the
relevant `_shared-*/` folder — don't re-derive or invent it. Where mobile explicitly reuses a web-suite
convention (TanStack Query patterns, query-key factory shape), `../../_shared-mobile/` cites
`../../_shared-web/` rather than restating it — don't restate it a third time either.

## Combinations & order

- **Greenfield build:** `backend-architect` (interview → arch doc) → `backend-scaffold` (boot the
  project) → per feature: `backend-database` (tables) + `backend-api-design` (endpoints) +
  `backend-auth` (if auth) → `backend-review` before commit → `backend-security` for auth/payment
  features. `project-context` runs throughout (init at scaffold, updated every change).
- **Feature on existing project:** `dev-partner` (confirm approach/trade-offs) → build skills →
  `backend-review` → `project-context` (SCHEMA.md/API.md/CHANGELOG.md same task).
- **Inherited/messy codebase:** `backend-reverse-engineer` (map + risk-ranked problems + staged
  plan) → `dev-partner` (agree the plan, don't unilaterally refactor) → staged fixes via
  database/api-design/auth → `backend-review` each stage.
- **Bug report:** `backend-debug` (root cause → fix → verify) → `backend-review` if the fix is
  non-trivial or touches shared code.
- **Pre-ship auth/payment:** `backend-security` (audit) → `backend-debug` (fix any hole) →
  `backend-review` (final pass).

## Full-stack combinations & order

- **Full-stack feature (new endpoint + web UI):** architect both sides against one API contract →
  backend-database/api-design/auth (build + expose) → project-context (API.md) → frontend-data
  (consume, matching the response envelope) → frontend-components (UI) → backend-review +
  frontend-review. The frontend `../../_shared-web/api-contract.md` normalizer must match what
  the backend actually returns — reconcile at the API-contract step, not after.
- **Frontend consuming an existing backend:** frontend-architect (map endpoints → pages) →
  frontend-data → frontend-components → frontend-review.
- **Multi-surface feature (backend + web + mobile from one endpoint):** architect all applicable
  surfaces against the **same** API contract in one pass — don't let mobile-architect reinterpret
  an endpoint frontend-architect already planned. Then: backend build skills → project-context
  (API.md, consumer column covers both web and mobile) → frontend-data/-components AND
  mobile-data/-components in parallel → backend-review + frontend-review + mobile-review.
- **Mobile consuming an existing backend (with or without an existing web frontend):**
  mobile-architect (map endpoints → screens; reuse the web data model where it's genuinely shared,
  don't replan it) → mobile-data → mobile-components → mobile-review.

## When NO skill fits
If the task isn't backend, web, or mobile engineering (infra, data science, a one-off script), say
so and handle it directly — don't force-fit a skill. `dev-partner`'s conduct rules still apply.

## Don't over-invoke
A one-line change with an obvious fix doesn't need the full review+security+context ceremony —
apply judgement (dev-partner rule: match effort to the task). The router is for choosing the
*right* tool, not for running all of them on everything.
