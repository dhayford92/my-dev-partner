---
name: mobile-reverse-engineer
description: Map an existing mobile app's real architecture as actually built, trace navigation and data flow through screens, identify problem areas (over-fetching, missed offline handling, unnecessary re-renders, unhandled permission states, unguarded deep links) ranked by risk, and produce a staged refactor plan with production-grade replacement code. Use when inheriting or auditing an unfamiliar Expo/React Native app, before a big refactor, or when a mobile codebase has drifted from convention. Always separates what IS from what SHOULD BE — never launders the current state into the recommendation.
---

# mobile-reverse-engineer

Reconstruct what a mobile app actually does — not what its docs claim — then chart the path to
what it should be. Convention baseline for "should be" is [`../_shared-mobile/`](../_shared-mobile/README.md);
deviations from it are findings, not new normal.

## Golden rule

**Separate "what IS" from "what SHOULD BE" in every artifact.** If auth guarding only happens at
the root `index.tsx` with nothing at nested layouts, say so plainly before recommending anything.

## Phase 1 — Map what IS

Read broadly; don't sample. Produce:

1. **Stack & structure actual** — Expo SDK/RN/Router versions vs. `../_shared-mobile/stack-and-structure.md`'s
   canonical set; screen architecture (logic-in-route-file vs. a `features/` split — note which
   this codebase actually uses); component folder shape.
2. **Navigation map** — every route group, what `_layout.tsx` files actually guard (read them —
   don't assume; the confirmed reality in both reference apps was that only the root `index.tsx`
   gates auth at all).
3. **Data flow trace** — for the main flows, follow one request end to end: screen → action →
   `apiFetch` → backend, and back. Note whether actions use the throw-or-return convention or
   something else (an `ActionResult`-style wrapper ported from web would be a finding).
4. **Storage audit** — where are tokens actually stored? (`AsyncStorage` vs `expo-secure-store` —
   grep for `SecureStore`; its absence is itself a finding, not something to assume away.)
5. **Native capability audit** — push (registration + listeners + does tap routing exist?),
   permissions (denial handling present?), EAS config (channels set? env vars used or hardcoded
   URLs?).
6. **Convention adherence table** — for each `../_shared-mobile/` convention: Followed / Partial /
   Violated, with `file:line` evidence.

Use `Grep`/`Glob` to quantify: how many screens use `<Controller>`-wrapped fields vs. manual
`useState` validation; how many `Alert.alert` calls vs. `ButtonSheet`; whether `useColorScheme`
appears at all; whether `AsyncStorage` or `SecureStore` holds the access token. Cite `file:line`.

## Phase 2 — Identify problem areas (ranked by risk)

Rank by **risk = impact × likelihood-of-causing-a-bug**. For each: the problem, every site it
occurs (not just one), why it's risky, and the blast radius. Recurring categories in this stack:

| Category | What to look for |
|----------|-------------------|
| Auth/token security | tokens in `AsyncStorage` instead of `SecureStore`; a blanket `clear()` on logout instead of removing only auth keys |
| Navigation guard gaps | deep-link-reachable screens with no auth check beyond the root gate |
| Data-layer drift | an `ActionResult`-style wrapper ported from web; inline query-key arrays; missing `invalidateQueries` after a mutation |
| Destructive-action correctness | signing out / treating an action as successful when its mutation actually errored |
| Re-render cost | unmemoized context values; inline object/array/callback props into list row components |
| Missed offline/permission handling | no denial UX (bare `alert()`); no network-error differentiation; permission requested with no fallback |
| Push notification gaps | listeners that invalidate but never route (or vice versa); no cold-start tap handling |
| Bundle/perf | heavy libs imported into the root layout; `FlatList` without `keyExtractor`/without windowing tuned for a huge list |
| EAS/build hygiene | missing channels; hardcoded API URLs; no per-profile env |

Full checklist: [references/audit-checklist.md](references/audit-checklist.md).

## Phase 3 — Staged refactor plan (with real code)

Ordered by leverage & safety, each stage independently shippable, with the actual replacement
code (matching `../_shared-mobile/`) and a verification step (on-device, not just a type-check).

Template: [references/refactor-plan.md](references/refactor-plan.md).

## Working rules

- **Evidence or it didn't happen** — every claim cites `file:line`.
- **Don't invent intent.** If you can't tell why something was built a way, say "unclear intent"
  and ask.
- **Target `../_shared-mobile/`, not generic React Native best practice.**
- Distinguish **must-fix** (security/correctness/crash risk) from **should-fix** (consistency)
  from **nice-to-have**.
- Plans and writes replacement code; land it stage by stage with the owner, don't sweep silently.
