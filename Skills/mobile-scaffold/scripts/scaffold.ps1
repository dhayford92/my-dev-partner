<#
.SYNOPSIS
  Bootstrap a new Expo Router app in Denzel's mobile stack. Run from the parent directory the
  project should live in.
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

Write-Host "==> Creating Expo Router app: $ProjectName" -ForegroundColor Cyan
npx create-expo-app@latest $ProjectName --template default@latest
Set-Location $ProjectName

Write-Host "==> Installing dependencies" -ForegroundColor Cyan
npx expo install `
  @tanstack/react-query nativewind tailwindcss tailwind-merge react-hook-form zod `
  @hookform/resolvers @react-native-async-storage/async-storage expo-secure-store `
  expo-notifications expo-device expo-constants expo-updates expo-splash-screen `
  expo-status-bar expo-haptics expo-web-browser react-native-heroicons `
  react-native-safe-area-context react-native-screens react-native-gesture-handler `
  react-native-reanimated react-native-svg

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

$assets = @(
  "app.json", "eas.json", "babel.config.js", "metro.config.js", "tailwind.config.js",
  "global.css", ".env.example",
  "libs\storage.ts", "libs\utils.ts", "libs\api-urls.ts", "libs\query_keys.ts", "libs\routes.ts",
  "hooks\apiFetch.ts", "hooks\registerForPushNotificationsAsync.ts", "hooks\useOTAUpdates.ts",
  "services\actions\auth_actions.ts", "services\actions\profile_actions.ts",
  "providers\auth-provider.tsx", "providers\notification-provider.tsx",
  "components\ui\button.tsx", "components\ui\text-field.tsx", "components\ui\button-sheet.tsx",
  "components\ui\skeleton.tsx", "components\ui\states.tsx", "components\ui\toster.tsx",
  "components\pages\screen.tsx",
  "app\_layout.tsx", "app\index.tsx",
  "app\(auth)\_layout.tsx", "app\(auth)\welcome.tsx",
  "app\(tabs)\_layout.tsx", "app\(tabs)\home\_layout.tsx", "app\(tabs)\home\index.tsx"
)
foreach ($a in $assets) { Copy-Asset $a }

if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }

Write-Host "`n==> Done. Next:" -ForegroundColor Cyan
Write-Host "    1) Set app.json bundle identifiers + eas.json project ID"
Write-Host "    2) Edit .env (EXPO_PUBLIC_API_BASE_URL)"
Write-Host "    3) npx expo start — then run references/first-run.md"
