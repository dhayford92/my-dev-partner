# Planning artifact templates (mobile)

Fill these in. Keep them terse — a plan, not prose.

## 1. Screen & route inventory

| Screen | Route | Group | Deep-link/notification entry? | Purpose |
|--------|-------|-------|-------------------------------|---------|
| Welcome | `/(auth)/welcome` | `(auth)` | no | request OTP |
| Home | `/(tabs)/home` | `(tabs)` | notification tap (`type: "auth"`) | dashboard |
| Request detail | `/(sub)/requests/[id]` | `(sub)` | notification tap (`type: "request_status_update"`) | view one request |

## 2. Navigation map

```
app/
├─ (auth)/          welcome → otp → (complete-account, if new user)
├─ (tabs)/
│  ├─ home/          index, [drill-down screens as nested stack]
│  └─ <tab2>/
└─ (sub)/            pushed screens outside the tab bar (detail views, settings sub-pages)
```

- Modal vs. pushed screen: use `ButtonSheet` for confirms/short forms; a real route (pushed stack
  screen) for anything with its own back-navigation need or that should be deep-linkable.
- **Guard gap check:** for each screen reachable by deep link/notification, ask — does landing
  here while unauthenticated leak anything or crash? If yes, flag it; the single root-level auth
  gate won't catch it (see `../../_shared-mobile/stack-and-structure.md`).

## 3. Per-screen data requirements

| Screen | Query key | Action | Mutations | Notes |
|--------|-----------|--------|-----------|-------|
| Home | `queryKeys.profile.me()` | `getMe` (throw-or-return) | — | smoke-tested by scaffold |
| Request detail | `queryKeys.requests.detail(id)` | `getRequestDetail(id)` | `cancelRequest(id)` | cancel = destructive, see mobile-data |

## 4. State boundaries

| State | Classification | Where | Justification |
|-------|-----------------|-------|----------------|
| request list/detail | server cache | TanStack Query | API data |
| current draft (multi-step flow) | in-memory Context | `RequestProvider` | spans multiple screens, not persisted |
| auth session | global client + SecureStore | `AuthProvider` | needed app-wide, survives restart |
| selected sheet/dialog open | local | `useState` in the screen | screen-scoped |

Rule: a new global Context needs a stated reason (spans >1 screen, or survives navigation).
Default is server-cache or local.

## 5. Offline & sync strategy

State explicitly, per feature, one of:
- **A. No special handling** — TanStack's default retry + refetch-on-foreground is enough (the
  confirmed default in both reference apps for nearly everything).
- **B. Read resilience only** — cache `staleTime` tuned so stale data displays instead of a blank
  screen while offline; no write-queueing.
- **C. Write queueing** — a mutation attempted offline is queued and retried on reconnect. This is
  new ground (neither reference app has it) — only commit to this for a specific, named feature
  the owner confirms needs it, not as a blanket default.

## 6. Push notification strategy

| Notification `data.type` | Triggers on backend | Invalidates (client) | Routes to (tap) | Foreground banner? |
|---------------------------|----------------------|------------------------|-----------------|---------------------|
| `auth` | profile/verification change | `profile.me()` | `/(tabs)/home` | no |
| `request_status_update` | request status change | `requests.detail(id)` | `/(sub)/requests/[id]` | yes |

Every row needs both the invalidation target and the route target decided together — see
`../../_shared-mobile/native.md#push-notifications`.

## 7. Native capability & API consumption map

| Capability | Screens | Permission timing | Denial handling |
|------------|---------|--------------------|------------------|
| Camera | recipient photo, profile photo | at point of use (tap icon) | inline message + `Linking.openSettings()` |
| Location | delivery address | onboarding gate (if required) + ad hoc | gate blocks core flow; ad hoc shows inline prompt |
| Biometrics | app-unlock (optional) | user-enabled setting, checked at auth gate | falls back to normal session flow |

| Endpoint | Screens | Response type | Error/pagination handling |
|----------|---------|----------------|----------------------------|
| `GET /core/api/v1/client/requests` | Request list | `PaginatedResponse<RequestResponse>` | mobile `apiFetch` normalizer; see `../../_shared-mobile/data-layer.md` |
