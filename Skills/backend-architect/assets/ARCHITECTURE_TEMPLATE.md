# Architecture Template

> Hand this file to any AI (or human) when planning or brainstorming a new system. Fill each
> section — the *italic prompt* under each heading says what belongs there. The structure is
> stack-agnostic, but the **Defaults** boxes are pre-filled with Denzel's canonical stacks —
> backend: FastAPI + Tortoise + PostgreSQL; web frontend: Next.js App Router + React 19 +
> Tailwind v4 + shadcn/ui + TanStack Query; mobile: Expo Router + React Native + NativeWind +
> TanStack Query — so "production-ready" means the right thing. Delete or override a default only
> with a stated reason (record it under *Open Questions* or in the ADR log).
>
> Sections **1–15 are backend**, **F1–F6 are web frontend**, **M1–M7 are mobile** (fill F/M only
> for the surfaces the system actually has), and **16 Open Questions** is shared across all
> surfaces. For a multi-surface build, plan every applicable surface against the **same** API
> surface in §6 — don't replan the contract per surface (§F6/§M7 each just map onto it).

---

## 0. Snapshot

*One paragraph: what is this system, who is it for, and what is the single most important
thing it must do well?*

- **Working name:**
- **Owner:**
- **Date:**
- **Status:** idea | designing | building | live

---

## 1. Problem statement

*What problem does this solve, and why now? What does success look like in one sentence?
What is explicitly out of scope for v1?*

---

## 2. Users & roles

*Who uses it? List each persona and what they can do. Map each persona to a technical
`user_type` and pick the authorization model.*

| Persona | Description | `user_type` | Key permissions |
|---------|-------------|-------------|-----------------|
| | | | |

> **Default authz model** — choose one (see `../../_shared-backend/auth.md`):
> - **Persona guards** (default): `user_type` in the JWT + `Current<Persona>User` deps. Best
>   for B2C / simple admin.
> - **JSON RBAC** (opt-in): org-scoped configurable roles (`frameworks × read/write/delete`).
>   Best for B2B with per-org roles.
> - **Team + Postgres RLS** (opt-in): multi-tenant SaaS with a separate admin portal JWT.

---

## 3. Core flows

*List the 3–7 flows that define the product (e.g. "client places order → vendor accepts →
delivery → payment settled"). For each, note the trigger, the actors, the happy path, and
the main failure modes. These become the endpoints and the background jobs.*

1.
2.
3.

---

## 4. System components

*What are the moving parts? Which are in-process (FastAPI sub-apps, services, schedulers) and
which are external (DB, Redis, Spaces, Resend, payment/SMS providers, AI)? A simple boxes-and-
arrows list is enough.*

> **Default topology:** one FastAPI app, three mounted sub-apps (`/users`, `/core`,
> `/utils`), PostgreSQL, Redis, APScheduler in-process, DigitalOcean Spaces for files, Resend
> for email. Bare-metal `uvicorn`.

- In-process:
- External services:

---

## 5. Data flow

*Trace how a request moves through the system for the primary flow: client → route → auth
guard → controller → services/models → DB, plus any async side-effects (background email,
activity log, scheduled follow-up). Call out where transactions and idempotency matter.*

---

## 6. API surface

*List the endpoints grouped by domain. Use the canonical URL shape
`/{domain}/api/v1/{persona}/{feature}`. Mark auth requirement and rate limits.*

| Method | Path | Persona / auth | Rate limit | Purpose |
|--------|------|----------------|------------|---------|
| POST | `/users/api/v1/client/auth/login` | public | `LOGIN` | authenticate |
| | | | | |

> **Defaults:** snake_case JSON; success `{message, data?}`; list
> `{data, current_page, page_limit, total_count}`; errors via `HTTPException` → default
> `{detail}` + `X-Error-Code` header; ISO-8601 UTC timestamps. (See `../../_shared-backend/response-contract.md`.)

---

## 7. Database schema

*List tables with key columns, types, relations, and indexes. Every table: UUID PK,
`created_at`/`updated_at` (UTC), nullable `deleted_at` for soft delete, snake_case plural
name. Note which columns are indexed and why, and any `unique`/`unique_together`.*

| Table | Key columns | Relations | Indexes | Notes |
|-------|-------------|-----------|---------|-------|
| | | | | |

> **Defaults:** Tortoise ORM + Aerich migrations; `CharEnumField` for statuses; JSON columns
> for flexible metadata; tenant scope column (`team_id`/`organization_id`) if multi-tenant.
> (See `../../_shared-backend/database.md`.)

---

## 8. Auth model

*Token type & lifetime, refresh strategy, password/verification/reset flows, and the
persona/permission model. Note any second token type (OTP, portal, invite).*

> **Defaults:** JWT HS256 (python-jose), 60-min access, 30-day stateless refresh + Redis
> denylist, bcrypt cost 12, `HTTPBearer` → `AuthContext` → persona guards. (See
> `../../_shared-backend/auth.md`.)

- Login method(s):
- Verification / reset:
- Second token types:
- Authz model (from §2):

---

## 9. Caching strategy

*What is cached, where, and how is it invalidated? Redis is available — use it for the token
denylist, rate-limit counters, and any hot read-through cache. State TTLs and invalidation
triggers so the cache can't drift.*

| Cached data | Store | Key | TTL | Invalidated when |
|-------------|-------|-----|-----|------------------|
| Token denylist | Redis | `token:denied:{jti}` | token life | (auto-expire) |
| | | | | |

---

## 10. Background jobs

*What runs on a schedule or async? Use APScheduler (cron/interval). List each job: trigger,
cadence, what it does, and failure behaviour.*

| Job | Trigger | Cadence | Does | On failure |
|-----|---------|---------|------|------------|
| | | | | |

> **Default:** APScheduler in the lifespan; stable `id=`, `replace_existing=True`; jobs call
> `*Scheduler` service methods. Never Celery. (See `../../_shared-backend/email-jobs-storage.md`.)

---

## 11. Third-party integrations

*Every external dependency: provider, purpose, auth/secrets, failure mode, and whether it's
on the critical path. Include email (Resend), storage (DO Spaces), and any payment/SMS/AI/KYC
providers.*

| Provider | Purpose | Secrets (env) | Critical path? | Failure handling |
|----------|---------|---------------|----------------|------------------|
| Resend | transactional email | `MAIL_API_KEY` | no (async) | log + swallow |
| DO Spaces | file storage | `BUCKET_*` | varies | 4xx on bad file |
| | | | | |

---

## 12. Error & logging strategy

*How errors surface to the client and how they're recorded. Two logging systems: dev/error
(stdlib logger + Sentry) and admin activity (audit trail). Note what gets redacted.*

> **Defaults:** errors raised as `HTTPException(status_code, detail, headers?)` → FastAPI's
> default `{detail}` body, machine codes via `X-Error-Code` header from the `ErrorCodes`
> catalog (no global handlers); stdlib `logger` everywhere (no `print`); Sentry when `SENTRY_DSN` set;
> `ActivityService` → `ActivityLog` for every mutation; PII redaction on logged/audited data;
> `X-Request-ID` correlation IDs. (See `../../_shared-backend/logging.md`, `../../_shared-backend/response-contract.md`.)

- Extra `ErrorCodes` this system needs:
- Activity events to audit:
- PII fields to redact:

---

## 13. Scaling considerations

*Where does this break at 10×/100× load? Identify the likely bottleneck (DB connections, hot
tables, N+1s, synchronous external calls, single-process scheduler) and the first mitigation.
Note read/write ratio and any table expected to grow unbounded (activity logs, events).*

---

## 14. Security considerations

*Threats and mitigations: auth/permission boundaries, input validation, injection surfaces,
secrets handling, rate limiting, PII exposure, privilege escalation, webhook signature
verification. Note which endpoints are public and how they're protected.*

> **Defaults:** rate-limit auth/OTP/reset endpoints; validate all input via pydantic;
> parameterised ORM queries only; secrets in `.env` (never committed); redact PII in logs;
> verify provider webhook signatures; persona/permission checks at both route and (for RBAC)
> service level.

---

## 15. Deployment topology

*Where and how does this run? Environments, process model, how migrations are applied, how
secrets are delivered, how the scheduler is handled with multiple processes.*

> **Default:** bare-metal `uvicorn main:app` on a DigitalOcean droplet; `.env` on the host;
> `aerich upgrade` on deploy; single scheduler process (if scaling to multiple workers, run
> the scheduler in exactly one). Docker + CI are optional add-ons, not the default.

- Environments (dev / staging / prod):
- Process model:
- Migration & secret delivery:

---

---

# Part II — Frontend

*Fill F1–F6 only if the system has a UI. Conventions and the fully-worked patterns live in
`../../_shared-web/`. Plan against the same API surface as §6.*

## F1. Page & route inventory

*Every route, its group, protection, and persona. Which pages are list/detail/create-edit-delete
of which resource. This mirrors §2 personas and §6 endpoints onto screens.*

| Route | Group | Protected | Persona | Purpose |
|-------|-------|-----------|---------|---------|
| `/login` | `(auth)` | no | — | authenticate |
| `/portal/<resource>` | `portal` | yes | | list + CRUD |
| `/portal/<resource>/[id]` | `portal` | yes | | detail |

> **Defaults:** App Router route groups — `(auth)` (unauth flows), `portal` (protected, middleware-
> gated), public/marketing, `shared/[token]` (token-gated). `middleware.ts` gates `/portal/*` on
> token presence + proactive refresh. (See `../../_shared-web/stack-and-structure.md`.)

## F2. Component architecture

*For the main pages, the component tree in the 3 tiers, and where each piece lives.*

> **Defaults (3 tiers):** `components/ui/` shadcn primitives + owner extensions (`confirm-dialog`,
> `crud-dialog`, `data-table`, `resource-page-header`, `states`, the `InputField` field family);
> `components/page/` shell composites (sidebar, headers); `components/custom/{domain}/` feature
> components. Reuse a primitive/extension before building new. (See
> `../../_shared-web/components-and-forms.md`.)

- Heavy pages & their trees:
- New `ui/` extensions this system needs:

## F3. State boundaries

*Classify each piece of state: server cache, global client, or local.*

| State | Classification | Where | Justification |
|-------|----------------|-------|---------------|
| | server cache | TanStack Query | API data |
| | global client | React Context | app-wide, hydrated from server (justify each) |
| | local | `useState` | page-scoped |

> **Defaults:** server data → TanStack Query; global client state → React Context, sparingly (no
> Zustand/Redux); local → `useState`. Auth/session → httpOnly cookies. (See
> `../../_shared-web/data-layer.md`.)

## F4. Forms & validation

*Which forms exist, where their schemas live, and how they submit.*

> **Defaults:** react-hook-form + `zodResolver`; the `InputField` field family; zod schemas in
> `lib/schemas/{domain}.ts` (snake_case, matching the API payload); client-only fields in a
> separate `xFormSchema`; native `form=""` dialog submit; submit → `useMutation` → check
> `result.error` → toast + invalidate; 422 → map `ApiError.fieldErrors` onto fields. (See
> `../../_shared-web/components-and-forms.md`.)

- Key forms & their schemas:

## F5. Loading & animation strategy

*Which loading pattern per surface, and where motion lives vs stays static.*

> **Defaults:** loading via the `states.tsx` kit — skeleton for list/detail, spinner for full-
> screen, inline label-swap for buttons; `isLoading`/`isError`/empty gated in-component (no
> `loading.tsx`). Motion by surface: framer-motion for marketing entrance/scroll, CSS `ly-*`
> keyframes for subtle product motion, static for admin/data-dense UI. (See
> `../../_shared-web/states-and-motion.md`.)

- Real-time / streamed surfaces (SSE/websocket):
- Deliberately static areas:

## F6. API consumption

*How the frontend consumes the §6 API surface: the fetch pipeline, error/pagination handling, and
auth token flow. Map endpoints → consuming pages/hooks.*

> **Defaults:** `apiFetch` (Bearer via cookie, **normalized errors**) → `lib/actions/*` server
> actions returning `ActionResult<T>` → raw `useQuery`/`useMutation` + `queryKeys` factory. Backend
> error contract is FastAPI `{detail}` + an `X-Error-Code` header (§12); this frontend deliberately
> **branches on HTTP status and does not consume the header** — the normalizer yields a typed
> `ApiError` (status + 422 field errors) and still tolerates a legacy `{error:{…}}` body. A
> pagination adapter normalizes the list envelope. Tokens in httpOnly cookies with proactive
> `jwt-decode` refresh. (See `../../_shared-web/api-contract.md`.)

| Endpoint (from §6) | Consuming page/hook | Response type | Notes |
|--------------------|--------------------|---------------|-------|
| | | | |

> **Contract check:** the frontend's error/pagination handling must match what the backend §6/§12
> actually returns. Backend sends `{detail}` + `X-Error-Code`; this frontend uses only the status
> (a client-side choice, not a backend gap). Pagination is `{data,current_page,page_limit,total_count}`.
> Where a backend still diverges (structured error bodies; non-canonical pagination), record the
> migration as an ADR — don't paper over it per client.

---

# Part III — Mobile

*Fill M1–M7 only if the system has a mobile app (Expo Router / React Native). Conventions and the
fully-worked patterns live in `../../_shared-mobile/`. Plan against the same API surface as §6
— reuse the endpoint list and response types from Part I/§F6 where the product genuinely shares
data model with web; only plan what's mobile-specific here.*

## M1. Screen & route inventory

*Every screen, its route group, whether it's reachable via deep link/notification tap, and its
purpose. Mirrors §2 personas and §6 endpoints onto screens.*

| Screen | Route | Group | Deep-link/notification entry? | Purpose |
|--------|-------|-------|-------------------------------|---------|
| Welcome | `/(auth)/welcome` | `(auth)` | no | authenticate |
| Home | `/(tabs)/home` | `(tabs)` | | |

> **Defaults:** Expo Router file-based groups — `(auth)` (unauth flows), `(tabs)` (authenticated
> tab group), other pushed-stack groups for detail/settings screens. Logic lives directly in the
> route file (no separate `features/` delegation layer). **`app/index.tsx` is the ONLY auth
> gate** — nested layouts carry no guard logic; a deep link into a nested authenticated screen is
> not blocked by the framework. (See `../../_shared-mobile/stack-and-structure.md`.)

## M2. Component architecture

*For the main screens, the component tree in the 3 tiers, and where each piece lives.*

> **Defaults (3 tiers):** `components/ui/` generic primitives (`Button`, `TextField`,
> `ButtonSheet`, `Skeleton`, `Toster`); `components/pages/` screen-shell wrappers (`Screen` —
> always `SafeAreaView`); `components/custom/{domain}/` domain-specific components. Reuse a
> primitive before building new. (See `../../_shared-mobile/components-and-forms.md`.)

- Heavy screens & their trees:
- New `ui/` primitives this system needs:

## M3. State boundaries

*Classify each piece of state: server cache, global client, or local.*

| State | Classification | Where | Justification |
|-------|-----------------|-------|----------------|
| | server cache | TanStack Query | API data |
| | global client | React Context | app-wide, hydrated on launch (justify each) |
| | local | `useState` | screen-scoped |

> **Defaults:** server data → TanStack Query; global client state → React Context, sparingly
> memoized (no Zustand/Redux); local → `useState`. Auth session → `expo-secure-store` (tokens) +
> `AsyncStorage` (everything else). (See `../../_shared-mobile/data-layer.md`.)

## M4. Forms & validation

*Which forms exist, where their schemas live, and how they submit.*

> **Defaults:** react-hook-form + `zodResolver`; the `<Controller>`-wrapped `TextField` family
> (`CheckboxField`/`SelectField`); zod schemas in `services/schemas/{domain}.ts` (snake_case,
> matching the API payload); `KeyboardAvoidingView` + `keyboardShouldPersistTaps="handled"`;
> submit → `useMutation`/direct action call → toast via `useToster()` + invalidate; 422 → map
> `ApiError.fieldErrors` onto fields. (See `../../_shared-mobile/components-and-forms.md`.)

- Key forms & their schemas:

## M5. Loading & motion strategy

*Which loading pattern per context, and where motion lives vs. stays static.*

> **Defaults:** `Skeleton` (list/card content) · `ActivityIndicator` (blocking async, no
> meaningful skeleton shape) · inline button label-swap (mutations). Motion is light and sparing:
> Reanimated spring for the `ButtonSheet` primitive, `FadeIn` on the splash/auth-gate screen,
> optional staggered `FadeInDown` for short lists only. Haptics (`expo-haptics`) on
> confirm-taps/selection changes only — not globally. No dark mode by default. (See
> `../../_shared-mobile/states-and-motion.md`.)

- Screens needing pull-to-refresh / infinite scroll (new ground — neither reference app has this):
- Deliberately static areas:

## M6. Offline & push notification strategy

*What's committed to for offline resilience, and the push notification contract.*

> **Default offline stance:** TanStack Query's built-in retry + `AppState`→`focusManager`
> foreground-refetch is usually sufficient — commit to write-queueing only for a named feature
> that genuinely needs it, not as a blanket default. (See `../../_shared-mobile/data-layer.md`.)

| Notification `data.type` | Triggers on backend | Invalidates (client) | Routes to (tap) |
|---------------------------|----------------------|------------------------|-----------------|
| | | | |

> **Rule:** every notification type gets both an invalidation target and a routing target,
> decided together. (See `../../_shared-mobile/native.md`.)

## M7. Native capabilities & API consumption

*Native capability → screens → permission timing → denial handling; plus endpoint → consuming
screen → response type → error/pagination handling.*

> **Defaults:** request permission at the point of need; **always** handle denial (in-app message
> + `Linking.openSettings()`, never a bare `alert()`); a required permission uses the full-screen
> "Gate" overlay pattern. `apiFetch` (Bearer via `expo-secure-store`, normalized `{detail}`
> errors) → `services/actions/*` (throws or returns — **no `ActionResult` wrapper**, unlike web) →
> raw `useQuery`/`useMutation` + `queryKeys`. EAS: explicit `channel` per build profile + the
> manual guarded OTA-update hook; API base URL from `EXPO_PUBLIC_API_BASE_URL` per profile, never
> hardcoded. (See `../../_shared-mobile/native.md`, `../../_shared-mobile/data-layer.md`.)

| Capability | Screens | Permission timing | Denial handling |
|------------|---------|--------------------|------------------|
| | | | |

| Endpoint (from §6) | Consuming screen/action | Response type | Notes |
|---------------------|--------------------------|----------------|-------|
| | | | |

> **Contract check:** mobile's error handling must match what the backend §6/§12 actually
> returns, same as web's §F6 check. Note explicitly where mobile's handling diverges from web's
> (e.g. mobile ignores the `X-Error-Code` header the same way web does, mobile has no
> `ActionResult` envelope) — these are deliberate platform choices, not bugs; record them as an
> ADR if non-obvious rather than letting them look like an oversight.

---

## 16. Open questions

*Everything undecided or assumed, any surface. Anything here that stays unresolved is a risk.
Convert resolved ones into ADR entries (`.claude/context/DECISIONS.md`).*

-
-
