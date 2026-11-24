<#
.SYNOPSIS
    Aerich migration helper (Windows-native). Wraps the safe migrate/upgrade workflow.
.DESCRIPTION
    Runs from the project root (or pass -Project). Uses the project's venv python if present.
    Actions:
      migrate   -Name "desc"   generate a migration from model changes
      upgrade                  apply pending migrations
      downgrade                roll back the last migration
      history                  list applied migrations
      init                     first-time aerich init + init-db
.EXAMPLE
    .\db.ps1 -Action migrate -Name "add_order_table" -Project "D:\...\my-api"
    .\db.ps1 -Action upgrade
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet("migrate","upgrade","downgrade","history","init")][string]$Action,
    [string]$Name,
    [string]$Project = "."
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path $Project
Push-Location $root
try {
    $venvPy = Join-Path $root "venv\Scripts\python.exe"
    $py = if (Test-Path $venvPy) { $venvPy } else { "python" }

    switch ($Action) {
        "init" {
            & $py -m aerich init -t configs.database.tortoise_config
            & $py -m aerich init-db
        }
        "migrate" {
            if (-not $Name) { throw "Provide -Name 'description' for migrate." }
            & $py -m aerich migrate --name $Name
            Write-Host "`n>> REVIEW the generated SQL under migrations/models/ before 'upgrade'." -ForegroundColor Yellow
            Write-Host ">> On LIVE data, read references/safe-migrations.md first." -ForegroundColor Yellow
        }
        "upgrade"   { & $py -m aerich upgrade }
        "downgrade" { & $py -m aerich downgrade }
        "history"   { & $py -m aerich history }
    }
}
finally {
    Pop-Location
}
