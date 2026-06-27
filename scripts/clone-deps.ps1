#Requires -Version 5.1
<#
.SYNOPSIS
  Shallow-clone vendor open-source repos for 知行 (Zhixing).
#>
param(
    [switch]$SkipDify
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Vendor = Join-Path $Root "vendor"
New-Item -ItemType Directory -Force -Path $Vendor | Out-Null

function Clone-Shallow {
    param([string]$Url, [string]$Dir, [string]$Branch = "main")
    $dest = Join-Path $Vendor $Dir
    if (Test-Path (Join-Path $dest ".git")) {
        Write-Host "[skip] $Dir already cloned"
        return
    }
    Write-Host "[clone] $Url -> $Dir"
    git clone --depth 1 --branch $Branch $Url $dest 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[retry] $Dir without branch pin"
        git clone --depth 1 $Url $dest
    }
}

Write-Host "=== Zhixing vendor clone ===" -ForegroundColor Cyan

if (-not $SkipDify) {
    Clone-Shallow "https://github.com/langgenius/dify.git" "dify" "main"
}

Clone-Shallow "https://github.com/tldraw/tldraw.git" "tldraw" "main"
Clone-Shallow "https://github.com/meilisearch/meilisearch.git" "meilisearch" "main"

# MetaGPT 已存在于 G:\MetaGPT，创建 junction 引用
$metaLink = Join-Path $Vendor "metagpt"
if (-not (Test-Path $metaLink)) {
    if (Test-Path "G:\MetaGPT") {
        cmd /c mklink /J `"$metaLink`" `"G:\MetaGPT`" 2>&1
        Write-Host "[link] vendor/metagpt -> G:\MetaGPT"
    } else {
        Write-Warning "G:\MetaGPT not found; clone MetaGPT manually"
    }
}

Write-Host "=== Done ===" -ForegroundColor Green
Get-ChildItem $Vendor | Select-Object Name, Mode
