# EAS Build & Update workflow

## Build profiles — `eas.json`

```json
{
  "cli": { "version": ">= 16.4.0", "appVersionSource": "remote" },
  "build": {
    "development": { "developmentClient": true, "distribution": "internal", "channel": "development",
                      "env": { "EXPO_PUBLIC_API_BASE_URL": "https://dev-api.example.com" } },
    "preview":     { "distribution": "internal", "channel": "preview",
                      "env": { "EXPO_PUBLIC_API_BASE_URL": "https://staging-api.example.com" } },
    "production":  { "autoIncrement": true, "channel": "production",
                      "env": { "EXPO_PUBLIC_API_BASE_URL": "https://api.example.com" } }
  },
  "submit": { "production": {} }
}
```

**Channel is mandatory on every profile.** Without it, `eas update` can't target a build
distinctly — confirmed gap in one reference app (ships OTA with no channel mapping at all).

## Running a build

```bash
eas build --profile development --platform ios      # internal dev client
eas build --profile preview --platform android       # internal testing
eas build --profile production --platform all        # store submission
```

## Publishing an OTA update

```bash
eas update --channel production --message "Fix checkout crash"
```

Only JS/asset changes ship this way — a native module addition or a config plugin change needs a
new build, not an update.

## The manual guarded update-check hook (already scaffolded)

`hooks/useOTAUpdates.ts` — checks on launch and on `AppState` foreground-return, guards against
overlapping checks, no-ops in dev/Expo Go. Call it once at the root layout. See
`../../_shared-mobile/native.md#ota-updates--the-manual-guarded-hook-canonical-confirmed-in-the-more-mature-app`
for the full source.

## Rollback — an operational runbook step, not code

There is **no in-app rollback mechanism** in either reference app. To roll back a bad OTA update:

```bash
# republish a known-good update to the same channel
eas update --channel production --message "Rollback to <good-update-id>" --republish --group <good-update-group-id>
```

Or use the EAS dashboard's "Republish" action on a prior update. Document this in the project's
`.claude/context/DECISIONS.md` or an incident runbook — it's not something `mobile-native`
generates code for.

## Versioning

- `runtimeVersion: { policy: "appVersion" }` — an OTA update is only compatible with builds
  sharing the same `version` in `app.json`. Bumping `version` requires a new native build before
  any OTA update targeting it can ship.
- `autoIncrement: true` on the `production` build profile — EAS bumps the native build number
  automatically; `version` itself is bumped manually per release.

## Env across profiles

`EXPO_PUBLIC_*` vars set in each profile's `env` block are inlined at build time and read via
`process.env.EXPO_PUBLIC_API_BASE_URL` in `libs/api-urls.ts` (see `mobile-scaffold`). For local
dev, `.env` (gitignored, copy from `.env.example`) covers `expo start`. **Never** put a secret in
an `EXPO_PUBLIC_*` var — it's bundled into the client and readable by anyone with the app binary.

## Submission

```bash
eas submit --platform ios --profile production
eas submit --platform android --profile production
```

Android submission needs a service account key (`serviceAccountKeyPath` in `eas.json`'s `submit`
block, confirmed pattern in one reference app) — keep that file out of version control
(`.easignore`/`.gitignore`).
