param(
    [ValidateSet("windows", "macos", "linux")]
    [string]$Target = "windows"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Mobile = Join-Path $Root "apps/mobile"

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Host "Flutter SDK not found. Desktop build is a documented placeholder in Cloud."
    exit 0
}

Push-Location $Mobile
try {
    flutter config --enable-$Target-desktop
    flutter build $Target
}
finally {
    Pop-Location
}
