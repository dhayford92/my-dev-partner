# Screens — {{PROJECT_NAME}}

> Mobile screen/navigation inventory. Create this file only when the mobile section of
> ARCHITECTURE.md gets too large. Update in the same task as any screen/navigation change.
> Conventions: ../../../_shared-mobile/ in the Skills library. Delete this file if the project has
> no mobile app.

## Screen inventory
<!-- Per screen: route, purpose, data sources (service actions), mutations, sheets, states,
     native capabilities used. Logic lives directly in the route file — no features/ delegation
     layer — unless this project has explicitly chosen otherwise (say so if it has). -->

### <screen name> — `/(tabs)/<route>`
- **Data:** `queryKeys.<domain>.list(...)` ← `get<Domain>` (throw-or-return, no ActionResult)
- **Mutations:** `create<Domain>` / `delete<Domain>` → invalidate `<domain>.list`
- **Sheets:** `ButtonSheet` (create/confirm) — not `Alert.alert`
- **States:** loading (`Skeleton`) · error (`ErrorState` + retry) · empty (`EmptyState`)
- **Native:** e.g. camera permission (denial → settings deep-link), push tap routes here for `type: "..."`

## Shared UI primitives (`components/ui/`)
<!-- Owner-built primitives: Button, TextField (+ CheckboxField/SelectField), ButtonSheet,
     Skeleton, Toster, states.tsx. -->
| Component | Purpose |
|-----------|---------|
| | |

## Providers / global state
<!-- AuthProvider, NotificationProvider, and any domain providers (Location, Currency, ...) — what
     they hold, whether the value is memoized, where hydrated (SecureStore/AsyncStorage). -->

## Native capability map
<!-- Capability → screens using it → permission timing → denial handling. -->
| Capability | Screens | Permission timing | Denial handling |
|------------|---------|--------------------|------------------|
| | | | |

_Last updated: {{DATE}}_
