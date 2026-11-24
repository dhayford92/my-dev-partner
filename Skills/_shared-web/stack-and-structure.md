# Frontend Stack & Structure — Canonical (Single Source of Truth)

This folder is the **one place** the conventions for Denzel's Next.js frontend stack are
written down. Every skill under `frontend-web/` points here instead of restating. Change a
convention **here** and every skill inherits it.

> Extracted from production web apps (multi-tenant SaaS portal, admin/ops console, marketing
> site) — and reconciled
> by the owner. Where repos disagreed, the owner picked one canonical variant; losing variants
> are marked "❌ not this" so skills never regenerate them.

## Stack (always)

- **Framework:** Next.js **App Router** (`next@16`), **React 19.2.3**, **TypeScript** (strict).
- **Package manager:** **pnpm** (`pnpm dev|build|start|lint`).
- **Styling:** **Tailwind v4** (CSS-first), `tw-animate-css`. See [styling.md](styling.md).
- **UI kit:** **shadcn/ui** (CLI-installed), Radix primitives, **lucide-react** (+ `@tabler/icons-react`).
- **Utilities:** `class-variance-authority`, `clsx`, `tailwind-merge` (the `cn()` helper).

### App-only stack (product apps, not marketing sites)

- **Server cache:** `@tanstack/react-query@5`. See [data-layer.md](data-layer.md).
- **Forms:** `react-hook-form` + `zod` + `@hookform/resolvers`. See [components-and-forms.md](components-and-forms.md).
- **Tables:** `@tanstack/react-table`.
- **Toasts:** `sonner`. **Theme:** `next-themes`. **Charts:** `recharts` (+ `chart.js` where needed).

### Marketing-only stack

- **`framer-motion`** for entrance/scroll choreography. NOT used in product apps
  (product uses CSS keyframes — see [states-and-motion.md](states-and-motion.md)).

## Canonical decisions at a glance

| Area | Canonical | ❌ Not this |
|------|-----------|-------------|
| Data-layer folder | `lib/actions,models,schemas,constants` | `services/actions,...` (older split) |
| Custom-component folder | `components/custom/{domain}/` | `components/customs/` (typo variant) |
| Server-action envelope | `ActionResult<T> = {data,error}` | `ResponseModel {status,message,data}` |
| Client fetching | raw `useQuery`/`useMutation` + server action + `queryKeys` | `useApi.ts` wrappers / `useAsyncData` (both deprecated) |
| QueryClient | SSR-singleton, `staleTime: 60_000` | `useState(() => new QueryClient)` with `staleTime: 0` |
| Token refresh | proactive `jwt-decode` exp check in `getAccessToken` | trust-until-401 |
| Cookie `sameSite` | `lax` | `strict` |
| shadcn style / baseColor | `new-york` / `stone` | — (brand color is a placeholder) |
| Form submit in dialogs | native `form="<id>"` association | `document.getElementById(id).click()` |
| Route-level errors | real `error.tsx` + `not-found.tsx` + error boundary | in-component only (today's gap) |

## Folder tree (product app)

```
app/
├─ (auth)/               # unauthenticated flows (login, onboarding, reset) + its own layout
├─ (landing-page)/       # optional public marketing pages
├─ portal/               # PROTECTED app; middleware-gated; portal/layout.tsx = shell
│  └─ <feature>/
│     ├─ page.tsx        # owns data fetching, dialog state, mutations
│     ├─ _components/    # route-private components
│     └─ [id]/page.tsx   # detail route
├─ shared/[token]/       # optional public token-gated views
├─ layout.tsx            # root: fonts + ThemeProvider + QueryProvider + Toaster
├─ error.tsx             # route error boundary (see api-contract.md)
├─ not-found.tsx
└─ globals.css           # Tailwind v4 tokens (styling.md)
components/
├─ ui/                   # shadcn primitives + owner extensions (states, confirm-dialog, ...)
├─ page/                 # layout composites (app-sidebar, nav-*, site-header)
└─ custom/{domain}/      # feature components by domain
hooks/                   # use-mobile, useDebounce, feature hooks (NO useApi/useAsyncData)
providers/               # query-provider, theme-provider, (user-provider for global context)
lib/
├─ actions/              # "use server" modules; call apiFetch; return ActionResult<T>
├─ models/               # response TypeScript types (mirror backend response schemas)
├─ schemas/              # zod schemas (xSchema + XInput; shared common.ts)
├─ constants/            # api-urls.ts, query-keys.ts, config.ts
└─ utils.ts              # cn(), formatDate(), ...
middleware.ts            # protects /portal/*; proactive refresh
```

**Path aliases (all repos, `tsconfig` + `components.json`):** `@/components`, `@/components/ui`,
`@/lib`, `@/lib/utils`, `@/hooks`. **Always `@/` imports — never `../../`.**

## `cn()` helper — verbatim (`lib/utils.ts`)

```ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)) }
```

## Marketing site (thinner — do not force product conventions onto it)

A marketing site legitimately has no data layer, forms, query client, `next-themes`, or design
tokens. It uses `app/components/` (co-located), bespoke inline-hex palette, a manual
`DarkModeToggle`, and heavy framer-motion. Treat absent product patterns as **N/A**, not as
inconsistency. Skills that generate product code must not template these landing-only choices.
