#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting Zhixing API on :8080 ..." -ForegroundColor Cyan
Set-Location (Join-Path $Root "services\api")
if (-not (Test-Path ".env")) {
    Copy-Item (Join-Path $Root ".env.example") ".env"
}
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
