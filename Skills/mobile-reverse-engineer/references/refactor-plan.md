# Staged refactor plan — template (mobile)

Order by leverage & safety. Each stage independently shippable, with replacement code and an
on-device verification step. Keep "what IS" visible next to "what SHOULD BE."

## Summary table

| Stage | Theme | Risk | Effort | Depends on |
|-------|-------|------|--------|------------|
| 0 | Move tokens to `expo-secure-store` | med (migration) | S | — |
| 1 | Fix destructive-action error handling (stop false-success) | high | S | — |
| 2 | Standardize data layer on throw-or-return (drop any `ActionResult` port) | low | M | — |
| 3 | Add `channel` + env to every `eas.json` build profile | low | S | — |
| 4 | Add permission-denial UX (settings deep-link, not `alert()`) | low | M | — |
| 5 | Decompose bloated screens; memoize context values | med | M | 2 |
| 6 | Add deep-link-target auth checks beyond the root gate | med | M | — |

## Per-stage block

```
### Stage 0 — Move tokens to expo-secure-store

WHAT IS:
  - services/actions/auth_actions.ts:169 stores access_token/refresh_token via DataStorage
    (AsyncStorage) — unencrypted at rest.

WHAT SHOULD BE:
  - TokenStorage (expo-secure-store) for access_token/refresh_token; DataStorage (AsyncStorage)
    stays for everything else. See ../../_shared-mobile/data-layer.md#token-storage.

CHANGE:
  - Introduce TokenStorage alongside DataStorage (see mobile-scaffold/assets/libs/storage.ts).
  - Migrate existing installed-base tokens: on first launch after the update, if a token exists in
    AsyncStorage under the old key, read it once, write it to SecureStore, delete the AsyncStorage
    copy. Don't just switch reads and orphan existing logged-in users.

REPLACEMENT CODE:
  <TokenStorage from mobile-scaffold/assets/libs/storage.ts>

VERIFY (on-device):
  - Fresh install → login → confirm token readable via TokenStorage.get, absent from AsyncStorage.
  - Existing logged-in install → update → confirm session survives (migration path ran) and the
    old AsyncStorage key is gone afterward.

ROLLBACK: keep the migration read-path (check AsyncStorage as a fallback) for one release cycle
before removing it, so a rollback of the app itself doesn't strand sessions.
```

## De-risking the risky stages

- **Token storage migration**: must not log out the entire existing install base on update — the
  migration read-path (check the old location once, move it) is not optional.
- **Data-layer standardization**: migrate one domain's actions + their call sites together in one
  commit, not repo-wide at once, so a missed unwrap is caught locally.
- **Auth-gate hardening**: adding a check to one deep-link-reachable screen at a time, verified via
  an actual deep link test (not just the happy in-app-navigation path), since deep-link behavior
  differs from normal navigation and is easy to think you've tested when you haven't.

## What NOT to do

- No big-bang rewrite. Stages ship independently.
- Don't "improve" beyond `../../_shared-mobile/` conventions while refactoring — extra opinions go in the
  Phase 4-style optimization report, not silently into the fix.
