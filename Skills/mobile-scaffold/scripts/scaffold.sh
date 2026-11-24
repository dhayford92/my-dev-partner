#!/usr/bin/env bash
# Bootstrap a new Expo Router app in Denzel's mobile stack. Run from the parent dir.
# Usage: bash scaffold.sh <project-name> [--force]
set -euo pipefail

PROJECT="${1:?Usage: scaffold.sh <project-name> [--force]}"
FORCE=0; [[ "${2:-}" == "--force" ]] && FORCE=1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSET_DIR="$SCRIPT_DIR/../assets"

echo "==> Creating Expo Router app: $PROJECT"
npx create-expo-app@latest "$PROJECT" --template default@latest
cd "$PROJECT"

echo "==> Installing dependencies"
npx expo install \
  @tanstack/react-query nativewind tailwindcss tailwind-merge react-hook-form zod \
  @hookform/resolvers @react-native-async-storage/async-storage expo-secure-store \
  expo-notifications expo-device expo-constants expo-updates expo-splash-screen \
  expo-status-bar expo-haptics expo-web-browser react-native-heroicons \
  react-native-safe-area-context react-native-screens react-native-gesture-handler \
  react-native-reanimated react-native-svg

echo "==> Copying canonical asset templates"
copy_asset() {
  local rel="$1" src="$ASSET_DIR/$1" dst="./$1"
  mkdir -p "$(dirname "$dst")"
  if [[ -f "$dst" && $FORCE -eq 0 ]]; then echo "    skip (exists): $rel"
  else cp "$src" "$dst"; echo "    wrote: $rel"; fi
}

assets=(
  "app.json" "eas.json" "babel.config.js" "metro.config.js" "tailwind.config.js"
  "global.css" ".env.example"
  "libs/storage.ts" "libs/utils.ts" "libs/api-urls.ts" "libs/query_keys.ts" "libs/routes.ts"
  "hooks/apiFetch.ts" "hooks/registerForPushNotificationsAsync.ts" "hooks/useOTAUpdates.ts"
  "services/actions/auth_actions.ts" "services/actions/profile_actions.ts"
  "providers/auth-provider.tsx" "providers/notification-provider.tsx"
  "components/ui/button.tsx" "components/ui/text-field.tsx" "components/ui/button-sheet.tsx"
  "components/ui/skeleton.tsx" "components/ui/states.tsx" "components/ui/toster.tsx"
  "components/pages/screen.tsx"
  "app/_layout.tsx" "app/index.tsx"
  "app/(auth)/_layout.tsx" "app/(auth)/welcome.tsx"
  "app/(tabs)/_layout.tsx" "app/(tabs)/home/_layout.tsx" "app/(tabs)/home/index.tsx"
)
for a in "${assets[@]}"; do copy_asset "$a"; done
[[ -f .env ]] || cp .env.example .env

echo ""
echo "==> Done. Next:"
echo "    1) Set app.json bundle identifiers + eas.json project ID"
echo "    2) Edit .env (EXPO_PUBLIC_API_BASE_URL)"
echo "    3) npx expo start — then run references/first-run.md"
