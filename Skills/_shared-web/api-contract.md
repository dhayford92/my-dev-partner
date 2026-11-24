# API Contract — Error Normalizer, Pagination, Auth

The backend contract is documented in `../_shared-backend/response-contract.md` and
`../_shared-backend/auth.md`. **But those docs describe only one backend style.** Verified against
the real code, real backends **disagree**, so the frontend must normalize defensively
rather than assume one shape.

## The real backend reality

**Backend contract** (per `../_shared-backend/response-contract.md`): FastAPI default `{ detail }` body
(string; `[{loc,msg,type}]` for 422) **+ a machine code in the `X-Error-Code` response header**
drawn from `ErrorCodes`. Real backends are often mid-migration onto it, so expect these shapes:

| Backend | Error body | `X-Error-Code` header | Pagination shape |
|---------|-----------|-----------------------|------------------|
| Variant A | `{ detail: string }` | ✅ yes (`OTP_EXPIRED`, …) | `{ items, total, page, page_size, has_next }` |
| Variant B | `{ detail: string }`; 422 `{ detail: [{loc,msg,type}] }` | not yet | `{ data, total, limit, page }` |
| Variant C (legacy) | `{ error: { code, message, details } }` (legacy) | code in body | `{ data, current_page, page_limit, total_count }` |

> **Frontend decision (owner, 2026-07): this frontend branches on HTTP status and does NOT consume
> the `X-Error-Code` header.** The backend still sends it — the client just doesn't depend on it.
> `ApiError.code` is derived from the status (`HTTP_404`, `VALIDATION_ERROR`); use status for
> control flow and the `detail` string for display. The normalizer still parses a
> legacy `{error:{…}}` body until it migrates.

Consequence: **branch on status, not on codes.** Use HTTP status (401/403 → auth, 404 → not-found,
409 → conflict, 422 → field errors, 429 → rate limit) and the `detail` string for display. Still
normalize the three pagination shapes into one.
>
> *If you later want code-based UX (e.g. distinguish `OTP_EXPIRED` from `OTP_INVALID`, both 400),
> read the `X-Error-Code` header in `normalizeError` — the backend already sends it. It's an
> intentional client choice not to today, not a backend gap.*

## `ApiError` — typed, normalized (`lib/actions/types.ts`)

```ts
export interface FieldError { field: string; message: string }

export class ApiError extends Error {
  readonly code: string;              // "RESOURCE_NOT_FOUND" | "HTTP_404" | "VALIDATION_ERROR" | ...
  readonly status: number;
  readonly details?: Record<string, unknown>;
  readonly fieldErrors?: FieldError[]; // populated for 422 so forms can map errors back
  constructor(message: string, code = "UNKNOWN_ERROR", status = 500,
              details?: Record<string, unknown>, fieldErrors?: FieldError[]) {
    super(message);
    this.name = "ApiError";
    this.code = code; this.status = status; this.details = details; this.fieldErrors = fieldErrors;
  }
  isAuth()  { return this.code.startsWith("AUTH_") || this.status === 401 || this.status === 403 }
  is(code: string) { return this.code === code }
}
```

## The normalizer (`hooks/apiFetch.ts` — non-2xx branch)

Accepts every real shape and returns one `ApiError`. This is the load-bearing fix over the
repos' `result.detail || result.message`.

```ts
function normalizeError(status: number, body: any): ApiError {
  // 1. Legacy structured (transitional): { error: { code, message, details } }
  if (body?.error && typeof body.error === "object") {
    const { code, message, details } = body.error;
    const fieldErrors = Array.isArray(details?.errors)
      ? details.errors.map((e: any) => ({ field: e.field, message: e.message }))
      : undefined;
    return new ApiError(message ?? "Request failed", code ?? `HTTP_${status}`, status, details, fieldErrors);
  }
  // 2. FastAPI default validation (422): { detail: [{ loc, msg, type }] }
  if (Array.isArray(body?.detail)) {
    const fieldErrors = body.detail.map((e: any) => ({
      field: Array.isArray(e.loc) ? e.loc.slice(1).join(".") : String(e.loc),
      message: e.msg,
    }));
    return new ApiError("Request validation failed", "VALIDATION_ERROR", status, { errors: body.detail }, fieldErrors);
  }
  // 3. FastAPI default HTTPException (canonical): { detail: "..." }
  if (typeof body?.detail === "string") return new ApiError(body.detail, `HTTP_${status}`, status);
  // 4. Last resort
  return new ApiError(body?.message ?? `Request failed with status ${status}`, `HTTP_${status}`, status);
}
```
Called as `normalizeError(response.status, body)` in `apiFetch`.

Rate limiting stays explicit: `429` → `new ApiError("Rate limit exceeded…", "AUTH_RATE_LIMITED", 429)`.

## Pagination adapter (`lib/actions/pagination.ts`)

Frontend-canonical shape = `{ data, current_page, page_limit, total_count }`.
Adapt whatever the backend sent:

```ts
export interface Paginated<T> { data: T[]; current_page: number; page_limit: number; total_count: number }

export function toPaginated<T>(body: any): Paginated<T> {
  const data = body.data ?? body.items ?? [];
  return {
    data,
    current_page: body.current_page ?? body.page ?? 1,
    page_limit:   body.page_limit  ?? body.limit ?? body.page_size ?? data.length,
    total_count:  body.total_count ?? body.total ?? data.length,
  };
}
export const hasNextPage = (p: Paginated<unknown>) =>
  p.current_page * p.page_limit < p.total_count;
```

List server actions call `toPaginated` before returning, so client code always sees one shape.

## Consuming errors on the client

- **Toasts:** `toast.error(getErrorMessage(err))` where `getErrorMessage` returns
  `err instanceof ApiError ? err.message : "An unexpected error occurred"`.
- **Forms (422):** map `ApiError.fieldErrors` back onto RHF — see
  [components-and-forms.md](components-and-forms.md#surfacing-server-validation).
- **Auth:** `err.isAuth()` drives redirect-to-login / refresh. Query retry skips 401/403/404.

## Auth & tokens (frontend side)

Backend token model: JWT HS256, **access 60 min / refresh 30 days**, `Authorization: Bearer`,
personas via `user_type` claim (`client|vendor|admin|super_admin`); multi-tenant setups add `team_id` +
portal claims. Full detail: `../_shared-backend/auth.md`.

Frontend responsibilities:

- Tokens live in **httpOnly cookies** set by a `"use server"` auth action
  (`<app>_access_token`, `<app>_refresh_token`); `sameSite: 'lax'`, `secure` in prod. Access
  cookie `maxAge = expires_in`; refresh `maxAge = 30d`. A non-httpOnly `<app>_session` indicator
  (optional) lets client code know it's logged in.
- `apiFetch({ autoAuth: true })` reads the access cookie and attaches `Bearer`.
- **Proactive refresh (canonical):** `getAccessToken()` decodes `exp` with
  `jwt-decode`; if expired and a refresh cookie exists, it calls `refreshTokenAction` and returns
  the new access token; else clears cookies. `middleware.ts` also refreshes on `/portal/*` entry.
- Login/register/OAuth/accept-invite actions call `setTokenCookies(access, refresh, expires_in)`.
- Token response body shape: `{ access_token, refresh_token, token_type, expires_in }`.
