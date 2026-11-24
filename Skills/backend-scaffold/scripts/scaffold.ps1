<#
.SYNOPSIS
    Scaffold a new FastAPI + Tortoise backend from the template, then boot it and verify /health.

.DESCRIPTION
    Windows-native (PowerShell). Copies assets/template into a target directory, replaces the
    project-name token, creates a venv, installs deps, optionally starts Postgres+Redis via
    docker compose, runs Aerich migrations, seeds, boots uvicorn, and curls /health.

.PARAMETER Name
    Human project name, e.g. "My API". Written into .env APP_NAME.

.PARAMETER Path
    Target directory to create the project in (default: .\<slug>-api).

.PARAMETER WithDocker
    Start Postgres+Redis from docker-compose.dev.yml before migrating (default: $true if docker present).

.PARAMETER SkipVerify
    Skip the boot + /health check.

.EXAMPLE
    .\scaffold.ps1 -Name "My API" -Path "D:\Main\Desktop\API Systems\my-api"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Path,
    [nullable[bool]]$WithDocker,
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"
$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateDir = Join-Path (Split-Path -Parent $scriptDir) "assets\template"

if (-not (Test-Path $templateDir)) { throw "Template not found at $templateDir" }

# Derive slug + target path
$slug = ($Name.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if (-not $Path) { $Path = Join-Path (Get-Location) "$slug-api" }
if (Test-Path $Path) { throw "Target path already exists: $Path" }

Write-Host "==> Scaffolding '$Name' into $Path" -ForegroundColor Cyan

# 1. Copy template
Copy-Item -Recurse -Path $templateDir -Destination $Path
Get-ChildItem -Path $Path -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 2. .env from .env.example, set APP_NAME
$envExample = Join-Path $Path ".env.example"
$envFile    = Join-Path $Path ".env"
Copy-Item $envExample $envFile
(Get-Content $envFile) -replace '^APP_NAME=.*', "APP_NAME=$Name" | Set-Content -Encoding utf8 $envFile

# Fill README token
$readme = Join-Path $Path "README.md"
if (Test-Path $readme) {
    (Get-Content $readme) -replace '\{\{APP_NAME\}\}', $Name | Set-Content -Encoding utf8 $readme
}

# 3. Virtualenv + deps
Write-Host "==> Creating virtualenv + installing dependencies" -ForegroundColor Cyan
Push-Location $Path
try {
    python -m venv venv
    $py  = Join-Path $Path "venv\Scripts\python.exe"
    & $py -m pip install --upgrade pip | Out-Null
    & $py -m pip install -r requirements.txt

    # 4. Infra (Postgres + Redis)
    $dockerAvailable = [bool](Get-Command docker -ErrorAction SilentlyContinue)
    if ($null -eq $WithDocker) { $WithDocker = $dockerAvailable }
    if ($WithDocker) {
        if (-not $dockerAvailable) { throw "-WithDocker requested but docker is not installed." }
        Write-Host "==> Starting Postgres + Redis (docker compose)" -ForegroundColor Cyan
        docker compose -f docker-compose.dev.yml up -d
        Write-Host "    waiting for Postgres..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 6
    } else {
        Write-Host "==> Skipping docker; ensure Postgres + Redis in .env are reachable." -ForegroundColor Yellow
    }

    # 5. Migrations
    Write-Host "==> Running Aerich migrations" -ForegroundColor Cyan
    & $py -m aerich init -t configs.database.tortoise_config
    & $py -m aerich init-db

    # 6. Seed
    Write-Host "==> Seeding default roles + super admin" -ForegroundColor Cyan
    & $py -m scripts.seed

    # 7. Verify boot + health
    if (-not $SkipVerify) {
        Write-Host "==> Booting app + checking /health" -ForegroundColor Cyan
        $proc = Start-Process -FilePath $py -ArgumentList "-m","uvicorn","main:app","--port","8000" `
                    -PassThru -WindowStyle Hidden
        try {
            $ok = $false
            for ($i = 0; $i -lt 20; $i++) {
                Start-Sleep -Seconds 1
                try {
                    $resp = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
                    if ($resp.status -eq "healthy") {
                        Write-Host "==> HEALTH OK: $($resp | ConvertTo-Json -Compress)" -ForegroundColor Green
                        $ok = $true; break
                    } elseif ($resp.status) {
                        Write-Host "    health=$($resp.status) checks=$($resp.checks | ConvertTo-Json -Compress)" -ForegroundColor DarkYellow
                    }
                } catch { }
            }
            if (-not $ok) { throw "Health check did not return 'healthy' within 20s. See checks above." }
        } finally {
            if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
        }
    }

    Write-Host "`nDONE. Project at $Path" -ForegroundColor Green
    Write-Host "  cd `"$Path`"; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload" -ForegroundColor Gray
}
finally {
    Pop-Location
}
