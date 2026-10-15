<#
    Scorched Earth launcher

    Examples:
      .\run_scorched_earth.ps1
      .\run_scorched_earth.ps1 -Test
      .\run_scorched_earth.ps1 -SmokeTest
      .\run_scorched_earth.ps1 -SkipInstall
#>

[CmdletBinding()]
param(
    [switch]$Test,
    [switch]$SmokeTest,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectRoot

if (-not $SkipInstall) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    py -m pip install -r requirements.txt
}

if ($Test) {
    Write-Host "Running tests..." -ForegroundColor Cyan
    py -m unittest discover -s tests -v
    exit $LASTEXITCODE
}

if ($SmokeTest) {
    Write-Host "Running Pygame smoke test..." -ForegroundColor Cyan
    $env:SDL_VIDEODRIVER = "dummy"
    $env:SDL_AUDIODRIVER = "dummy"
    py scorched_earth.py --smoke-test
    exit $LASTEXITCODE
}

Write-Host "Starting Scorched Earth..." -ForegroundColor Green
py scorched_earth.py
exit $LASTEXITCODE

