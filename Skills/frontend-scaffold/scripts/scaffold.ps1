<#
.SYNOPSIS
  Bootstrap a new frontend in Denzel's Next.js stack. Idempotent-ish: won't clobber edited
  app/ files unless -Force. Run from the parent directory the project should live in.
.EXAMPLE
  pwsh scripts/scaffold.ps1 my-app
  pwsh scripts/scaffold.ps1 my-app -Force
#>
param(
  [Parameter(Mandatory = $true)][string]$ProjectName,
  [switch]$Force
)
$ErrorActionPreference = "Stop"
$AssetDir = Join-Path $PSScriptRoot "..\assets"

Write-Host "==> Creating Next.js app: $ProjectName" -ForegroundColor Cyan
pnpm create next-app@latest $ProjectName --ts --app --tailwind --eslint --use-pnpm --import-alias "@/*" --no-src-dir --turbopack
Set-Location $ProjectName

Write-Host "==> Installing app dependencies" -ForegroundColor Cyan
pnpm add `@tanstack/react-query `@tanstack/react-table react-hook-form `@hookform/resolvers zod `
  sonner next-themes lucide-react `@tabler/icons-react date-fns jwt-decode `
  class-variance-authority clsx tailwind-merge
pnpm add -D tw-animate-css

Write-Host "==> Initialising shadcn/ui" -ForegroundColor Cyan
pnpm dlx shadcn@latest init --yes --base-color stone
pnpm dlx shadcn@latest add --yes button input label field card dialog alert-dialog `
  dropdown-menu sonner skeleton badge table tabs sheet separator avatar

Write-Host "==> Copying canonical asset templates" -ForegroundColor Cyan
function Copy-Asset($rel) {
  $src = Join-Path $AssetDir $rel
  $dst = Join-Path (Get-Location) $rel
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  if ((Test-Path $dst) -and -not $Force) {
    Write-Host "    skip (exists): $rel" -ForegroundColor DarkYellow
  } else {
    Copy-Item $src $dst -Force
    Write-Host "    wrote: $rel" -ForegroundColor Green
  }
}

# Data layer + providers + shell + auth
$assets = @(
  "components.json",
  ".env.local.example",
  "lib\utils.ts", "lib\constants\api-urls.ts", "lib\constants\query-keys.ts",
  "lib\actions\types.ts", "lib\actions\pagination.ts", "lib\actions\auth.ts",
  "hooks\apiFetch.ts",
  "providers\query-provider.tsx", "providers\theme-provider.tsx",
  "components\ui\states.tsx", "components\ui\error-boundary.tsx",
  "components\custom\common\input-field.tsx",
  "app\layout.tsx", "app\globals.css", "app\error.tsx", "app\global-error.tsx", "app\not-found.tsx",
  "app\(auth)\layout.tsx", "app\(auth)\login\page.tsx", "app\(auth)\login\_components\login-form.tsx",
  "app\portal\layout.tsx", "app\portal\page.tsx",
  "middleware.ts"
)
foreach ($a in $assets) { Copy-Asset $a }

if (-not (Test-Path ".env.local")) { Copy-Item ".env.local.example" ".env.local" }

Write-Host "`n==> Done. Next:" -ForegroundColor Cyan
Write-Host "    1) Edit .env.local (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_SLUG)"
Write-Host "    2) pnpm dev  — then run the first-run checklist in references/first-run.md"
