#!/usr/bin/env bash
# Bootstrap a new frontend in Denzel's Next.js stack.
# Idempotent-ish: won't clobber edited app/ files unless FORCE=1. Run from the parent dir.
# Usage: bash scaffold.sh <project-name> [--force]
set -euo pipefail

PROJECT="${1:?Usage: scaffold.sh <project-name> [--force]}"
FORCE=0; [[ "${2:-}" == "--force" ]] && FORCE=1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSET_DIR="$SCRIPT_DIR/../assets"

echo "==> Creating Next.js app: $PROJECT"
pnpm create next-app@latest "$PROJECT" --ts --app --tailwind --eslint --use-pnpm \
  --import-alias "@/*" --no-src-dir --turbopack
cd "$PROJECT"

echo "==> Installing app dependencies"
pnpm add @tanstack/react-query @tanstack/react-table react-hook-form @hookform/resolvers zod \
  sonner next-themes lucide-react @tabler/icons-react date-fns jwt-decode \
  class-variance-authority clsx tailwind-merge
pnpm add -D tw-animate-css

echo "==> Initialising shadcn/ui"
pnpm dlx shadcn@latest init --yes --base-color stone
pnpm dlx shadcn@latest add --yes button input label field card dialog alert-dialog \
  dropdown-menu sonner skeleton badge table tabs sheet separator avatar

echo "==> Copying canonical asset templates"
copy_asset() {
  local rel="$1" src="$ASSET_DIR/$1" dst="./$1"
  mkdir -p "$(dirname "$dst")"
  if [[ -f "$dst" && $FORCE -eq 0 ]]; then echo "    skip (exists): $rel"
  else cp "$src" "$dst"; echo "    wrote: $rel"; fi
}

assets=(
  "components.json" ".env.local.example"
  "lib/utils.ts" "lib/constants/api-urls.ts" "lib/constants/query-keys.ts"
  "lib/actions/types.ts" "lib/actions/pagination.ts" "lib/actions/auth.ts"
  "hooks/apiFetch.ts"
  "providers/query-provider.tsx" "providers/theme-provider.tsx"
  "components/ui/states.tsx" "components/ui/error-boundary.tsx"
  "components/custom/common/input-field.tsx"
  "app/layout.tsx" "app/globals.css" "app/error.tsx" "app/global-error.tsx" "app/not-found.tsx"
  "app/(auth)/layout.tsx" "app/(auth)/login/page.tsx" "app/(auth)/login/_components/login-form.tsx"
  "app/portal/layout.tsx" "app/portal/page.tsx"
  "middleware.ts"
)
for a in "${assets[@]}"; do copy_asset "$a"; done
[[ -f .env.local ]] || cp .env.local.example .env.local

echo ""
echo "==> Done. Next:"
echo "    1) Edit .env.local (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_SLUG)"
echo "    2) pnpm dev  — then run references/first-run.md"
