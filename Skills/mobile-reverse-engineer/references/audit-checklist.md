# Audit checklist & probes (mobile)

Concrete greps/reads to quantify the current state. Cite `file:line` for every finding.

## Navigation & auth

- Read every `_layout.tsx` — does any nested layout (`(auth)`, `(tabs)`, etc.) have redirect/guard
  logic, or is the root `index.tsx` the only gate? (Confirmed reality in both reference apps: only
  the root.) Which deep-link-reachable screens would be exposed if so?
- Grep `Redirect` and `router.replace` to find every navigation-based guard actually in the code.
- Screen architecture: grep for a `features/` directory — present means the thin-route pattern is
  in use; absent means logic lives in route files (the owner's chosen canonical).

## Storage & tokens

- Grep `SecureStore` — present or absent? If absent, where are `access_token`/`refresh_token`
  actually stored (`AsyncStorage`, plain state, elsewhere)?
- Does `clearAuthData()`/logout call a blanket `AsyncStorage.clear()`, or remove only the
  auth-specific keys?
- Does the token-refresh path check for a missing refresh token before calling the endpoint, or
  send `refresh_token: undefined`?

## Data layer

- Grep `ActionResult` — if present on mobile, that's ported web convention, not the mobile
  canonical (throw-or-return).
- Count `useQuery(`/`useMutation(` call sites vs. any custom wrapper hook — is there a parallel
  data-fetching abstraction that shouldn't exist?
- Inline query-key arrays (`useQuery({queryKey: ['x', id]})`) vs. the `queryKeys` factory.
- For every mutation, is there a matching `invalidateQueries`?
- Is the `AppState`→`focusManager` wiring present in the root layout? (Its absence means
  foreground-refetch silently doesn't work — an easy-to-miss, hard-to-diagnose gap.)
- Is the `QueryClient` created inline in JSX (`<QueryClientProvider client={new QueryClient()}>`)
  instead of hoisted to module scope? (Confirmed bug pattern — recreates the client every render.)

## Forms & components

- Grep `useState` + manual validation `useEffect` in form components vs. `useForm`/`zodResolver`
  + `<Controller>`.
- `Alert.alert` call count vs. `ButtonSheet` usage — which is the actual confirm pattern here?
- Component folder shape: is there a real `ui/`/`pages/`/`custom/` 3-tier, or a flat dump?

## Destructive actions

- For each delete/deactivate flow: on the mutation's `onError`, does the code still sign the user
  out / navigate away / show a false-success state? (Confirmed bug pattern in one reference app —
  check for the exact anti-pattern, not just its presence in one file.)

## Native capabilities

- Push: does the response-listener (tap) do anything beyond `invalidateQueries`? Is there a
  `getLastNotificationResponseAsync()` cold-start check?
- Permissions: grep `alert(` near a permission `status !== "granted"` branch — bare alert with no
  settings deep-link is the confirmed anti-pattern.
- `useColorScheme`/`darkMode` — present or absent, and is it complete (branches consistently) or
  partial (present in some components, hardcoded colors in others)?

## EAS / build hygiene

- `eas.json` — does every build profile have an explicit `channel`? An `env` block?
- Grep the API base URL constant — a literal string, or `process.env.EXPO_PUBLIC_*`?
- `app.json`/`app.config.ts` — static or dynamic, and if dynamic, is the dynamism actually used
  (env-conditional logic) or just unnecessary complexity?

## Perf smells

- `FlatList` usage without `keyExtractor`, or with inline anonymous `renderItem` functions
  recreated every render.
- Context providers passing a fresh object literal as `value` each render (missing `useMemo`).
- Reanimated `entering`/`exiting` animations applied to every row of a long `FlatList` (fights
  virtualization).
- Heavy libraries (maps, charts, editors) imported at the root layout instead of the screen that
  actually needs them.

## Output of the audit

A convention-adherence table (Followed/Partial/Violated + evidence) and a ranked problem list feed
directly into `references/refactor-plan.md`.
