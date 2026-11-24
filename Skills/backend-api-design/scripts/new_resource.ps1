<#
.SYNOPSIS
    Generate route + controller + schema (+ model/service) stubs for a new resource.
.DESCRIPTION
    Windows-native wrapper around new_resource.py (the shared engine, so behaviour matches
    the cross-platform path exactly). Requires python on PATH.
.EXAMPLE
    .\new_resource.ps1 -Project "D:\...\my-api" -Domain core -Persona admin -Resource order -WithModel -Wire
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Project,
    [Parameter(Mandatory = $true)][ValidateSet("core", "users", "utils")][string]$Domain,
    [Parameter(Mandatory = $true)][string]$Persona,
    [Parameter(Mandatory = $true)][string]$Resource,
    [string]$Plural,
    [switch]$WithModel,
    [switch]$WithService,
    [switch]$Wire,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$engine = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "new_resource.py"

$pyArgs = @($engine, "--project", $Project, "--domain", $Domain, "--persona", $Persona, "--resource", $Resource)
if ($Plural)      { $pyArgs += @("--plural", $Plural) }
if ($WithModel)   { $pyArgs += "--with-model" }
if ($WithService) { $pyArgs += "--with-service" }
if ($Wire)        { $pyArgs += "--wire" }
if ($Force)       { $pyArgs += "--force" }

# Prefer the project's venv python if present, else system python
$venvPy = Join-Path $Project "venv\Scripts\python.exe"
$py = if (Test-Path $venvPy) { $venvPy } else { "python" }

& $py @pyArgs
