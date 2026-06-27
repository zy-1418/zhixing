param(
    [ValidateSet("flutter", "tauri")]
    [string]$Target = "flutter"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

if ($Target -eq "flutter") {
    Push-Location (Join-Path $RepoRoot "apps/mobile")
    try {
        flutter config --enable-windows-desktop
        flutter config --enable-macos-desktop
        flutter config --enable-linux-desktop
        flutter build windows --release
    }
    finally {
        Pop-Location
    }
    exit 0
}

Write-Host "Tauri desktop target is reserved for a future web shell."
Write-Host "Use apps/workflow_web, apps/graph_web, apps/canvas_web as embeddable web assets."
