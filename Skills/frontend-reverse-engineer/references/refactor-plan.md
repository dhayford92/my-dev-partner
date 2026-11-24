# Staged refactor plan — template

Order by leverage & safety. Each stage independently shippable, with replacement code and a
verification step. Keep "what IS" visible next to "what SHOULD BE".

## Summary table

| Stage | Theme | Risk | Effort | Depends on |
|-------|-------|------|--------|------------|
| 0 | Centralize fetch client + error normalizer | low | S | — |
| 1 | Standardize server actions on `ActionResult` | low | M | 0 |
| 2 | Migrate call sites to raw TanStack + queryKeys factory | med | L | 1 |
| 3 | Unify loading/error/empty via `states.tsx` | low | M | — |
| 4 | Add `error.tsx` / `not-found.tsx` / boundary | low | S | — |
| 5 | Decompose bloated pages; kill prop drilling | med | L | 2 |
| 6 | Delete dead paths (`useApi`, `useAsyncData`, bespoke fetch) | low | S | 2 |

## Per-stage block

```
### Stage 0 — Centralize the fetch client + error normalizer

WHAT IS:
  - hooks/useFetch.ts throws `result.detail || result.message` (lib/…:160) — loses codes/field errors.
  - Two ApiError classes (hooks/useFetch.ts:35, lib/actions/types.ts:130).

WHAT SHOULD BE:
  - One apiFetch that normalizes all backend error shapes → one typed ApiError (see
    ../../_shared-web/api-contract.md).

CHANGE:
  - Replace hooks/useFetch.ts with apiFetch.ts (paste canonical from frontend-scaffold assets).
  - Delete the duplicate ApiError; export one from lib/actions/types.ts.
  - Update imports (grep `from "@/hooks/useFetch"`).

REPLACEMENT CODE:
  <apiFetch.ts + types.ts from the scaffold assets>

VERIFY:
  - Type-check passes; an intentionally-failing request surfaces ApiError.code + fieldErrors;
    a 422 maps to form fields on one migrated form.

ROLLBACK: keep the old file until call sites are migrated; both can coexist one release.
```

## De-risking the risky stages

- **Auth/refresh changes**: change behind the existing cookie names; test login → protected page →
  expiry → refresh → logout before deleting the old path.
- **Query-key changes**: migrate a key and its every `invalidateQueries` together; a half-migrated
  key silently breaks cache invalidation (stale UI after mutation). Grep the key string.
- **Envelope standardization**: do it per action + its call sites in one commit, not repo-wide at
  once, so a missed unwrap is caught locally.

## What NOT to do

- No big-bang rewrite. Stages ship independently.
- Don't "improve" beyond the owner's conventions while refactoring — move toward `../../_shared-web/`,
  full stop. Extra opinions go in the optimization report, not the refactor.
