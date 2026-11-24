# Architecture — {{PROJECT_NAME}}

> System design, components, and data flow. Update whenever a component, service boundary,
> integration, or background job is added/changed/removed — in the same task as the change.

## Stack
FastAPI · Tortoise ORM + Aerich · PostgreSQL · Redis · APScheduler · SlowAPI · python-jose ·
bcrypt · Resend · boto3 (DigitalOcean Spaces).
<!-- Note any project-specific additions (Stripe, OpenAI, SumSub, Expo, etc.). -->

## Components
<!-- The mounted sub-apps and what lives in each; the services in src/services/. -->
- `/users` —
- `/core` —
- `/utils` —
- Services:

## Data flow
<!-- Trace the primary flow: request → guard → controller → services/models → DB, plus async
side-effects (email, activity log, scheduled follow-up). -->

## Background jobs (APScheduler)
| Job | Trigger | Cadence | Does |
|-----|---------|---------|------|
| | | | |

## Third-party integrations
| Provider | Purpose | Critical path? | Failure handling |
|----------|---------|----------------|------------------|
| Resend | email | no (async) | log + swallow |
| DO Spaces | storage | varies | 4xx on bad file |
| | | | |

## Authorization model
<!-- persona guards | org-scoped JSON RBAC | team + Postgres RLS. See ../../../_shared-backend/auth.md
     in the Skills library. -->

---

# Frontend
<!-- Fill this section only if the project has a frontend. Conventions: ../../../_shared-web/ in
     the Skills library. If the component/page inventory gets large, move it to COMPONENTS.md and
     link it here. -->

## Stack (frontend)
Next.js App Router · React 19 · TypeScript · Tailwind v4 · shadcn/ui · TanStack Query ·
react-hook-form + zod · sonner. <!-- note additions: framer-motion, recharts, puck, etc. -->

## Route / page map
<!-- Groups: (auth) | portal (protected) | public/marketing | shared. Mark protection + persona. -->
| Route | Group | Protected | Persona | Purpose |
|-------|-------|-----------|---------|---------|
| `/login` | (auth) | no | — | authenticate |
| `/portal/...` | portal | yes | | |

## Component tree (major pages)
<!-- Per heavy page: the 3-tier breakdown (ui / page / custom) + where state lives. -->

## State boundaries
<!-- server cache (TanStack Query) vs global client (React Context — justify each) vs local. -->

## Data-fetch flow
<!-- apiFetch (Bearer, normalized errors) → lib/actions/* (ActionResult) → raw useQuery/useMutation
     + queryKeys factory. Note any deviation. Error/pagination handling per
     ../../../_shared-web/api-contract.md. -->

---

# Mobile
<!-- Fill this section only if the project has a mobile app (Expo Router / React Native).
     Conventions: ../../../_shared-mobile/ in the Skills library. If the screen/navigation
     inventory gets large, move it to SCREENS.md and link it here. -->

## Stack (mobile)
Expo Router · React Native · TypeScript · NativeWind (Tailwind v3) · TanStack Query ·
react-hook-form + zod · expo-secure-store · expo-notifications.
<!-- note additions: expo-location, expo-image-picker, expo-local-authentication, i18next, etc. -->

## Screen / route map
<!-- Groups: (auth) | (tabs) | other pushed-stack groups. Mark whether reachable via deep link or
     notification tap. Screens carry their own logic directly (no features/ delegation layer),
     unless this project has explicitly chosen otherwise — say which. -->
| Screen | Route | Group | Deep-link/notification entry? | Purpose |
|--------|-------|-------|-------------------------------|---------|
| Welcome | `/(auth)/welcome` | `(auth)` | no | authenticate |
| Home | `/(tabs)/home` | `(tabs)` | | |

## Auth gate
<!-- Confirm where auth is actually guarded — the canonical baseline is ONLY app/index.tsx (no
     guard at nested layouts). If this project added guards elsewhere, document exactly where;
     if it hasn't, don't imply protection that isn't there. -->

## Component tree (major screens)
<!-- Per screen: the 3-tier breakdown (ui / pages / custom) + where state lives. -->

## State boundaries
<!-- server cache (TanStack Query) vs global client (React Context — justify each) vs local. -->

## Data-fetch flow
<!-- apiFetch (Bearer via expo-secure-store, normalized errors) → services/actions/* (throws or
     returns — no ActionResult wrapper) → raw useQuery/useMutation + queryKeys factory. Note the
     AppState→focusManager foreground-refetch wiring is present. Error/pagination handling per
     ../../../_shared-mobile/data-layer.md. -->

## Offline & push strategy
<!-- What's committed to for offline (see ../../../_shared-mobile/native.md — most apps need only
     TanStack's default retry, not a write-queue). Push notification types: which invalidate which
     queries, which route where on tap (both must be decided together per type). -->

## Native capabilities in use
<!-- Push, biometrics, camera, location, deep links — which, and permission-denial UX for each. -->

## EAS config
<!-- Build profiles + channels, whether the manual OTA-update hook is wired, per-profile env vars
     (never a hardcoded API base URL). -->

_Last updated: {{DATE}}_
