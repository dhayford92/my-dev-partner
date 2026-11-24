---
name: mobile-architect
description: Plan a mobile app's screen/navigation architecture, offline and sync strategy, push-notification strategy, and native-module decisions BEFORE writing code — screen inventory, route map, per-screen data requirements, state boundaries, and how it composes with the backend API surface (backend-architect) and the web frontend's data model (frontend-architect) when the same product spans multiple surfaces. Use when starting a new mobile app or feature area, or when a screen/flow is complex enough to need a plan first. Writes no implementation code. Not for building screens (mobile-components), data hooks (mobile-data), or native capability code (mobile-native).
---

# mobile-architect

Turn a product requirement into a concrete mobile build plan before any screen gets written.
Conventions come from [`../_shared-mobile/`](../_shared-mobile/README.md); the plan must be expressible in the
canonical structure (logic-in-route-file screens, 3-tier components, throw-or-return actions) —
if it isn't, that's a signal to rethink the plan, not invent new structure.

## When to use

- New mobile app, or a new feature area (e.g. "add a wallet section").
- A flow spans several screens with shared state (multi-step request/booking, KYC) and needs
  deliberate sequencing before code.
- The same product has a backend (`backend-architect`) and/or a web frontend
  (`frontend-architect`) already planned — this skill maps the mobile surface onto the *same* API
  contract and, where the product genuinely shares data model with web, the same data shapes.

Do **not** use to write screens/hooks (`mobile-components`/`mobile-data`) or bootstrap a project
(`mobile-scaffold`).

## Inputs — get context first

1. If `.claude/context/ARCHITECTURE.md`/`API.md` exist for this project, read them — they hold the
   real API surface and (if a web frontend exists) how it's already consumed.
2. If backend or web planning already happened this session, don't re-derive the API contract —
   reuse it. A mobile-only reinterpretation of an endpoint that already has a documented shape is
   a source of drift, not a fresh design.
3. If nothing exists, **interview the owner** — grouped, not one at a time:
   - Personas and which screens/tabs map to which persona.
   - Primary resources (nouns) and their list/detail/create/edit/delete needs on mobile
     specifically (not everything on web needs a mobile screen, and vice versa).
   - What must work offline or survive a flaky connection vs. what can just fail with a retry.
   - Which native capabilities are load-bearing (push, camera, location, biometrics) vs. nice-to-have.
   - Deep-link entry points (marketing links, notification taps, OAuth callbacks).
4. Never invent an endpoint, a screen, or a native capability requirement. Mark unknowns
   **[ASSUMPTION]** and confirm.

## The plan — produce these seven artifacts

Write to `.claude/context/` if the project uses it, otherwise present in chat. Templates in
[references/planning-artifacts.md](references/planning-artifacts.md).

1. **Screen & route inventory** — every screen, its route group (`(auth)`/`(tabs)`/other),
   whether it's reachable via deep link/notification tap, and its purpose. Mirrors the
   logic-in-route-file convention — no separate `features/` layer to plan around.
2. **Navigation map** — tab structure, stack nesting, modal/`ButtonSheet` vs. pushed-screen
   decisions, and where the (confirmed, documented) single-auth-gate limitation matters — flag any
   screen reachable by deep link that holds sensitive data and would benefit from its own guard.
3. **Per-screen data requirements** — which query keys, which service actions, what's fetched vs.
   derived from context.
4. **State boundaries** — server cache (TanStack Query) vs. React Context (justify each — default
   is *don't* add one) vs. local `useState`. Cite `../_shared-mobile/data-layer.md#state-boundaries`.
5. **Offline & sync strategy** — be explicit about what's actually being committed to, since
   neither reference app has NetInfo/retry-queue/offline banners today. Default recommendation:
   TanStack Query's built-in retry + `focusManager` refetch is often sufficient; only design a
   real offline queue if the product genuinely needs actions to survive being offline (confirm
   with the owner before scoping this in — it's real effort, not a checkbox).
6. **Push notification strategy** — which events trigger a push, what each notification type's
   `data` payload should carry (needed for both cache-invalidation and the new tap-routing
   pattern — see `../_shared-mobile/native.md`), and whether a notification should also show an in-app
   banner if received in foreground.
7. **Native capability & API consumption map** — table of native capability (camera/location/
   biometrics/push) → screens using it → permission timing → denial handling; plus endpoint →
   consuming screen → response type → error/pagination handling, matching the backend's actual
   contract (see `../_shared-backend/response-contract.md` and note where mobile's
   `apiFetch` normalizer diverges — see `../_shared-mobile/data-layer.md`).

## Working rules

- **Challenge over-scoped plans.** A screen needing 6 data sources and 3 native permissions is a
  candidate for splitting — say so before it's built, not in review.
- **Respect the owner's canonical mobile conventions over generic mobile best practice** — e.g.
  logic-in-route-file over a `features/` split, no `ActionResult` wrapper, no dark mode by default.
- **Structural decisions are the owner's** — new global Context, a new native dependency, an
  offline-queue commitment, a new permission the app didn't previously request. Present the
  trade-off, don't decide silently.
- Hand off cleanly: name query keys, action function names, and response model names the way
  `mobile-data`/`mobile-components` will actually generate them, so implementation matches the plan.

## Full-stack / multi-surface products

When the same product has a web frontend too: don't replan the API contract from scratch on
mobile. Reuse the endpoint list, response types, and (where genuinely shared) the domain model
`frontend-architect` already produced; only plan what's mobile-specific (native capabilities,
offline behavior, navigation shape). Divergences between what web needs from an endpoint and what
mobile needs are normal — call them out, don't force parity for its own sake.
