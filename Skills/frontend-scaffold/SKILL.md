---
name: frontend-scaffold
description: Bootstrap a new frontend in Denzel's Next.js App Router stack (React 19, Tailwind v4, shadcn/ui, TanStack Query, server-action data layer with a typed error normalizer, cookie-based JWT auth with proactive refresh, sonner, and route-level error boundaries) so it boots and renders a working authenticated shell on first run. Use at the very start of any new frontend project, or when adding the standard skeleton (data layer, auth, providers, protected routes) to a bare Next app. Produces runnable scripts plus drop-in asset templates — not prose.
---

# frontend-scaffold

Stand up a new frontend that **boots and renders a working shell on first run**, wired to the
backend's response envelope and auth model. Conventions come from
[`../_shared-web/`](../_shared-web/README.md) — cite them, don't restate them.

## When to reach for this

- New frontend project in this stack → run the whole thing.
- Bare `create-next-app` that needs the standard skeleton → run steps 3–6 only.
- Adding one missing piece (e.g. the error boundary) → copy that asset from `assets/`.

Not for planning page/component architecture (that's `frontend-architect`) or generating
feature code (`frontend-components`, `frontend-data`).

## What it produces

```
app/{layout,error,not-found,global-error}.tsx  app/globals.css
app/(auth)/login/{page,_components/login-form}.tsx   app/(auth)/layout.tsx
app/portal/{layout,page}.tsx                    middleware.ts
components/ui/*  (shadcn primitives + states.tsx + error-boundary.tsx)
hooks/apiFetch.ts
lib/actions/{types,pagination,auth}.ts  lib/constants/{api-urls,query-keys}.ts  lib/utils.ts
providers/{query-provider,theme-provider}.tsx
components.json  .env.local
```

## Procedure

Run the script for the platform, then verify. The script is idempotent-ish: it won't overwrite
`app/` files you've edited unless you pass `--force`.

### 1. Create the Next app + install deps

```bash
# from the parent dir where the project should live
bash scripts/scaffold.sh <project-name>        # macOS/Linux/Git-Bash
# or, on Windows PowerShell:
pwsh scripts/scaffold.ps1 <project-name>
```

The script runs `pnpm create next-app` (TS, App Router, Tailwind, `@/*` alias, no `src/`),
then installs the **app dependency set** from `../_shared-web/stack-and-structure.md`:

```
@tanstack/react-query @tanstack/react-table react-hook-form @hookform/resolvers zod \
sonner next-themes lucide-react @tabler/icons-react date-fns jwt-decode \
class-variance-authority clsx tailwind-merge
```

### 2. Initialise shadcn + primitives

```bash
pnpm dlx shadcn@latest init            # style: new-york, baseColor: stone, cssVariables: true
pnpm dlx shadcn@latest add button input label field card dialog alert-dialog dropdown-menu \
  sonner skeleton badge table tabs sheet separator avatar
```

Then overwrite `components.json` with `assets/components.json` (locks aliases + config from
[styling.md](../_shared-web/styling.md)).

### 3. Drop in the data layer + providers (assets/)

Copy verbatim — these ARE the canonical implementations behind
[data-layer.md](../_shared-web/data-layer.md) and [api-contract.md](../_shared-web/api-contract.md):

- `hooks/apiFetch.ts` — fetch client + **error normalizer** (handles all 3 backend error shapes).
- `lib/actions/types.ts` — `ActionResult<T>`, `ApiError`, `getErrorMessage`.
- `lib/actions/pagination.ts` — `toPaginated` adapter.
- `lib/actions/auth.ts` — cookie set/clear, `getAccessToken` with **proactive `jwt-decode`
  refresh**, `login/logout/refresh` actions.
- `lib/constants/api-urls.ts` — env-based base URL, mount split, cookie names, endpoint groups.
- `lib/constants/query-keys.ts` — `queryKeys` factory seed.
- `providers/query-provider.tsx` — **SSR-singleton** QueryClient.
- `providers/theme-provider.tsx` — `next-themes` wrapper.
- `lib/utils.ts` — `cn`, `formatDate`.

### 4. Shell, states & error boundaries

- `components/ui/states.tsx` — the shared state kit (`LoadingState`/`EmptyState`/`ErrorState`/
  skeletons) from [states-and-motion.md](../_shared-web/states-and-motion.md).
- `components/ui/error-boundary.tsx` + `app/error.tsx` + `app/global-error.tsx` +
  `app/not-found.tsx` — real route-level error handling (the gap in today's repos).
- `app/layout.tsx` — root: fonts + `ThemeProvider` + `QueryProvider` + `<Toaster position="top-center" />`.
- `app/globals.css` — Tailwind v4 tokens (neutral placeholder brand color).

### 5. Auth flow + protected routes

- `middleware.ts` — gates `/portal/*` on token presence, refreshes when only the refresh cookie
  is present, bounces authed users off `/login`.
- `app/(auth)/layout.tsx` + `app/(auth)/login/` — a working login form (RHF + zod + `InputField`
  + `loginAction`).
- `app/portal/layout.tsx` — server component: `getAccessToken()` guard + shell.
- `app/portal/page.tsx` — a home shell that renders and calls one authed action as the smoke test.

### 6. Configure env

Write `.env.local` from `assets/.env.local.example`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_SLUG=app          # cookie namespace → app_access_token, app_refresh_token
```

## First-run verification (required — never claim success without it)

Full checklist in [references/first-run.md](references/first-run.md). Minimum:

1. `pnpm dev` starts with **zero** TypeScript/console errors.
2. `/` and `/login` render; the login form shows and validates (empty submit → zod errors).
3. `/portal` while unauthenticated **redirects to `/login`** (middleware works).
4. Force a thrown error in a page → `app/error.tsx` renders (boundary works).
5. With the backend running, a successful login sets cookies and lands on `/portal` with the
   home shell rendered from a real authed request.

Report what you actually observed. If the backend isn't available, verify 1–4 and say 5 is
pending a running API.

## Cross-skill contract

Everything generated here is drop-in compatible with the backend response envelope, pagination,
and auth model. Feature code from `frontend-components` / `frontend-data` builds on exactly these
files. Do not diverge from the asset templates — if a convention needs to change, change it in
`../_shared-web/` first.
