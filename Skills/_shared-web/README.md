# `./` — Canonical Frontend Conventions

The **single source of truth** for Denzel's Next.js frontend stack. Every skill under
`frontend-web/` cites these files instead of restating conventions. Change a convention
**here** and every skill inherits it.

> Extracted from production web apps (a SaaS portal, an admin console, a marketing site) —
> and reconciled with the owner. Losing variants are marked "❌ not this" so skills never
> regenerate them.

## Files

| File | Covers |
|------|--------|
| [stack-and-structure.md](stack-and-structure.md) | Framework, deps, folder tree, aliases, route groups, canonical decisions table |
| [data-layer.md](data-layer.md) | `apiFetch` → server actions (`ActionResult`) → raw TanStack Query; queryKeys; state boundaries |
| [api-contract.md](api-contract.md) | **Error normalizer** + **pagination adapter** (reconciles 3 divergent backends); `ApiError`; auth/token handling |
| [components-and-forms.md](components-and-forms.md) | 3-tier components; `InputField` family; zod schemas; form→mutation; native `form=""` dialogs; 422→field errors |
| [states-and-motion.md](states-and-motion.md) | `states.tsx` kit; which loading pattern where; motion by surface (framer vs CSS keyframes vs static) |
| [styling.md](styling.md) | Tailwind v4 tokens, dark mode, shadcn config, responsive conventions |

## Backend contract (cross-stack)

For the API this frontend consumes, cite the backend suite's shared docs:
`../_shared-backend/response-contract.md` (envelopes) and `../_shared-backend/auth.md`
(JWT/persona model). **Caveat:** those docs describe one backend style only; the real backends diverge
— see [api-contract.md](api-contract.md) for the verified reality and the normalizer that handles it.

## Canonical decisions at a glance

See the table in [stack-and-structure.md](stack-and-structure.md#canonical-decisions-at-a-glance).
Headline rulings: `ActionResult` envelope · raw TanStack (no `useApi`/`useAsyncData`) ·
SSR-singleton QueryClient · proactive `jwt-decode` refresh · native `form=""` dialogs ·
real `error.tsx`/`not-found.tsx` + error boundary.
