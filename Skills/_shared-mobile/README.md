# `./` — Canonical Mobile Conventions

The **single source of truth** for Denzel's Expo/React Native stack. Every skill under
`frontend-mobile/` cites these files instead of restating conventions. Change a convention
**here** and every skill inherits it.

> Extracted from production mobile apps and reconciled with the owner. Losing variants are marked "❌ not this." This suite is a sibling of `../_shared-backend/` and
> `../_shared-web/`; where mobile reuses a web-suite convention verbatim, these files **cite**
> `../_shared-web/` rather than restating it.

## Files

| File | Covers |
|------|--------|
| [stack-and-structure.md](stack-and-structure.md) | Expo/RN/Router versions, folder tree, path alias, canonical decisions table, the auth-gate mechanism |
| [data-layer.md](data-layer.md) | Mobile's throw-or-return action pattern (no `ActionResult`), `apiFetch`, `focusManager` foreground-refetch, `expo-secure-store` token storage, query-keys |
| [components-and-forms.md](components-and-forms.md) | 3-tier components (`ui`/`pages`/`custom`), `Screen`/`Button`/`ButtonSheet`, the new `<Controller>`-wrapped form field |
| [states-and-motion.md](states-and-motion.md) | Skeleton/loading patterns, `FlatList` (not FlashList), sparing Reanimated/haptics use, dark mode opt-out |
| [native.md](native.md) | Push notifications, permissions, EAS build/update, biometric auth (new), notification-tap routing (new), deep linking |

## Canonical decisions at a glance

See the table in [stack-and-structure.md](stack-and-structure.md#canonical-decisions-at-a-glance).
Headline rulings: logic lives in route files (no `features/` split) · 3-tier components ·
`<Controller>`-wrapped form fields (new) · `expo-secure-store` for tokens (new) · no dark mode ·
no `ActionResult` envelope on mobile · `queryKeys` (lowercase) · EAS channels + manual OTA hook
combined · pessimistic/stay-signed-in destructive-action error handling.
