# First-run verification & troubleshooting

Never claim the scaffold works without walking this. Report what you actually observed.

## Checklist

| # | Step | Expected | Needs backend? |
|---|------|----------|----------------|
| 1 | `pnpm dev` | Compiles with **zero** TS/console errors | no |
| 2 | Open `/` then `/login` | Login form renders; empty submit → zod errors under fields | no |
| 3 | Open `/portal` while logged out | **Redirects to `/login`** (middleware) | no |
| 4 | Throw in a page body (`throw new Error("x")`) | `app/error.tsx` renders with "Try again" | no |
| 5 | Visit a bogus path `/nope` | `app/not-found.tsx` renders | no |
| 6 | Log in with valid creds | Cookies set (`<slug>_access_token` etc.); lands on `/portal`; the "Backend connection" card shows the `/me` payload | **yes** |
| 7 | Toggle system dark mode | Tokens flip; toasts follow theme | no |

If the backend isn't running, verify 1–5 + 7 and state that 6 is pending a live API.

## Verifying in the browser (agent)

Use the preview tools, not manual instructions to the user:
1. `preview_start { name: "<app>" }` (add a `.claude/launch.json` running `pnpm dev` on port 3000).
2. `read_console_messages` / `preview_logs` → confirm no errors (step 1).
3. `navigate` to `/login`, `read_page` → confirm the form and labels (step 2).
4. `navigate` to `/portal`, `read_page` → confirm redirect to `/login` (step 3).
5. Screenshot the rendered shell for the report.

## Common issues

- **`Module not found: @/components/ui/field`** — run `pnpm dlx shadcn@latest add field`. The
  `field` primitive backs `InputField`; the init step lists it, but verify it landed.
- **`sonner` Toaster unstyled / missing** — `pnpm dlx shadcn@latest add sonner` (overwrites the
  bare package's default). Root layout must render `<Toaster />` inside the providers.
- **Cookies not set after login** — `setTokenCookies` only runs in a `"use server"` action; make
  sure the login mutation calls `loginAction`, not a client fetch. Check the backend actually
  returns `{ access_token, refresh_token, expires_in }`.
- **Redirect loop on `/portal`** — the access token JWT can't be decoded (`getAccessToken` treats
  it as expired). Confirm the backend issues a standard JWT and `NEXT_PUBLIC_API_URL` is correct.
- **CORS errors** — the backend must allow the app origin; unrelated to the scaffold.
- **Hydration warning on `<html>`** — expected with `next-themes`; `suppressHydrationWarning` is
  already set on the root `<html>`.

## After first run

- Set the brand color: replace `--primary` / `--primary-foreground` (light + dark) in
  `app/globals.css`.
- Add the app shell (sidebar): `pnpm dlx shadcn@latest add sidebar`, build `components/page/
  app-sidebar.tsx`, wrap `portal/layout.tsx` in `SidebarProvider`.
- Generate features with `frontend-components` and `frontend-data` — both build on these files.
