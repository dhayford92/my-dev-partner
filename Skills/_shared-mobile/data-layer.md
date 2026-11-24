# Data Layer — Canonical (Mobile)

Mobile **reuses** the web suite's TanStack Query conventions directly — same query-key factory
shape, same raw-`useQuery`/`useMutation` philosophy, same "no custom wrapper hook" rule. Read
[`../_shared-web/data-layer.md`](../_shared-web/data-layer.md) first; this
file only covers where mobile **must** differ and why.

## Why mobile is NOT a straight copy of the web pipeline

The web pipeline is `apiFetch → "use server" action (ActionResult<T>) → raw TanStack`. The
`ActionResult<T> = {data,error}` envelope exists **only** because Next.js server actions need a
serializable return across the server/client boundary. **Mobile has no such boundary** — the RN
app calls the API directly, in-process. Confirmed in both reference apps: every service action
either **returns the data** or **throws** — neither wraps success/failure in an envelope object.

**Canonical mobile pipeline:**

```
apiFetch (Bearer, normalized errors)  →  services/actions/{domain}.ts (throws or returns T)  →  raw useQuery/useMutation + queryKeys
```

> ❌ Do not generate `ActionResult<T>` on mobile. Do not port the web envelope over "for
> consistency" — the consistency that matters is the TanStack usage pattern, not the envelope,
> and forcing the envelope in adds a pointless unwrap step with no serialization need to justify it.

## Stage 1 — `hooks/apiFetch.ts`

A plain async function, same shape as web's (`IController`/`RequestConfig`: `method`, `url`,
`params`, `data`, `contentType`, `autoAuth`). Differences from web:

- **No cookies.** `autoAuth: true` calls `getAccessToken()` (from `services/actions/auth_actions.ts`)
  which reads from **`expo-secure-store`**, not a cookie jar.
- Same error-message extraction shape as the backend's `{detail}` contract (string, or
  FastAPI 422 array of `{msg}`), normalized into one typed `ApiError` exactly like web's
  normalizer — see `../_shared-web/api-contract.md`. Dev-only structured console
  logging for 4xx/5xx (the more mature pattern — adopt it, not a bare
  `result.detail || result.message`).
- Network-error message should be actionable (mention connectivity + server reachability), not
  generic.

Full template: [../mobile-data/references/data-hooks.md](../mobile-data/references/data-hooks.md).

## Stage 2 — service actions (`services/actions/{domain}.ts`)

Plain async functions. **Throw on failure, return the typed response on success** — no wrapper:

```ts
export async function getProviders(params?: { search?: string }): Promise<ProviderResponse[]> {
  const body = await apiFetch<PaginatedResponse<ProviderResponse>>({
    method: "GET", url: API_URLS.USERS.PROVIDERS.LIST, params, autoAuth: true,
  });
  return body.data;
}

export async function deleteAccount(reason: string): Promise<MessageResponse> {
  return apiFetch<MessageResponse>({
    method: "DELETE", url: API_URLS.USERS.PROFILE.DELETE_ACCOUNT, data: { reason }, autoAuth: true,
  });
}
```

This means **every** action — whether consumed by `useQuery` or `useMutation` — follows the same
"unwrap-or-throw" convention. There is no query-vs-mutation return-shape distinction to remember
(unlike web); `isError`/`onError` just work off whatever `apiFetch` threw.

## Stage 3 — client consumption (raw TanStack Query)

Identical philosophy to web — confirmed in both apps' real screens (e.g. a typical
`app/(tabs)/home/index.tsx`):

```tsx
const { data: user } = useQuery({
  queryKey: queryKeys.profile.me(),
  queryFn: () => getUserProfile(),
});

const deleteMutation = useMutation({
  mutationFn: () => deleteAccount(reason),
  onSuccess: () => { queryClient.clear(); router.replace(ROUTES.AUTH.WELCOME); },
  onError: (error) => show({ type: "error", message: getErrorMessage(error) }),
});
```

## The one real mobile-specific TanStack adaptation: foreground refetch

Browsers get `visibilitychange` for free; React Native doesn't. **Both reference apps wire this
identically** in the root layout — this is required, not optional, boilerplate:

```tsx
import { AppState, type AppStateStatus, Platform } from "react-native";
import { focusManager } from "@tanstack/react-query";

function onAppStateChange(status: AppStateStatus) {
  if (Platform.OS !== "web") focusManager.setFocused(status === "active");
}

useEffect(() => {
  const sub = AppState.addEventListener("change", onAppStateChange);
  return () => sub.remove();
}, []);
```

Without this, `refetchOnWindowFocus`-equivalent behavior never fires on a native foreground return.

## QueryClient — module-level singleton (not created in render)

```tsx
const queryClient = new QueryClient();   // module scope, created ONCE

export default function RootLayout() {
  return <QueryClientProvider client={queryClient}>...</QueryClientProvider>;
}
```

> ❌ **Confirmed bug in one reference app:** `<QueryClientProvider client={new QueryClient()}>`
> written inline in JSX recreates the client on every render of the component it's in. Always
> hoist to module scope (there's no SSR concern on mobile, so this is simpler than web's
> SSR-singleton pattern — just a plain module-level `const`).

## Query keys — identical factory shape to web

```ts
export const queryKeys = {
  profile: {
    all: ["profile"] as const,
    me: () => [...queryKeys.profile.all, "me"] as const,
  },
  // domain: { all, list(params?), detail(id) } — same shape as web, confirmed in both apps
} as const;
```

**Named export `queryKeys`** (lowercase, matches web). Not `QueryKeys`.

## Token storage — `expo-secure-store` (canonical; both apps currently use AsyncStorage)

```ts
import * as SecureStore from "expo-secure-store";

export const TokenStorage = {
  async set(key: string, value: string) { await SecureStore.setItemAsync(key, value); },
  async get(key: string) { return SecureStore.getItemAsync(key); },
  async remove(key: string) { await SecureStore.deleteItemAsync(key); },
};
```

Use `SecureStore` **only** for `access_token`/`refresh_token`. General cache/preferences (last
region picked, onboarding-seen flags, cached notification token) stay in plain `AsyncStorage` via
a `DataStorage` class (`get`/`set`/`remove`/`clear`, JSON stringify/parse — both apps' shape,
confirmed identical). `expires_in` is stored as an **absolute Unix timestamp** (`now + ttl`) so
`getAccessToken()` can compare directly against `Date.now()` without decoding the JWT:

```ts
export async function getAccessToken(): Promise<string | null> {
  const expiresAt = await AsyncCache.get<number>("expires_in");
  if (expiresAt && expiresAt > Math.floor(Date.now() / 1000)) {
    return TokenStorage.get("access_token");
  }
  const refreshed = await refreshAccessToken();
  return refreshed?.access_token ?? null;
}
```

`clearAuthData()` removes **only** the auth-related keys explicitly (`access_token`,
`refresh_token`, `expires_in`, cached `user`) — never a blanket `AsyncStorage.clear()`/wipe-all,
which would also destroy unrelated cached preferences. `refreshAccessToken()` returns early
(`null`) if no refresh token is present rather than calling the endpoint with an undefined body.

## State boundaries

- **Server data** → TanStack Query, always.
- **Global client state** → React Context (`AuthProvider`, `NotificationProvider`, and per-domain
  providers like a `LocationProvider`/`CurrencyProvider` where the product needs one) — **memoize
  the context value** (`useMemo`) so consumers don't re-render on every provider render; a
  confirmed miss in one reference app.
- **Local UI state** → `useState`.
- No Zustand/Redux in either reference app — don't introduce one by default.

## On sign-out: clear the query cache

`signOut()`/logout should call `queryClient.clear()` **before** clearing local auth state, so no
stale cached data from the previous session survives into the next login (confirmed present in
one reference app, missing in the other — make it standard).
