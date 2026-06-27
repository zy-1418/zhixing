# Auto-continue workflow on agent stop (Windows PowerShell)
$ErrorActionPreference = "Stop"

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }

# Resolve state file relative to project root (parent of .cursor)
$hookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $hookDir)
$statePath = Join-Path $projectRoot ".cursor\WORKFLOW_STATE.json"

if (-not (Test-Path $statePath)) { exit 0 }

try {
    $state = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    exit 0
}

if (-not $state.auto_continue) { exit 0 }

# Respect overnight mode: stop if all steps completed
$pending = @($state.steps | Where-Object { $_.status -ne "completed" })
if ($pending.Count -eq 0) {
    $state.auto_continue = $false
    $state | ConvertTo-Json -Depth 8 | Set-Content $statePath -Encoding UTF8
    exit 0
}

$currentId = $state.current_step
$steps = @($state.steps)
$current = $steps | Where-Object { $_.id -eq $currentId } | Select-Object -First 1

if (-not $current) { exit 0 }

# Mark current step done, advance pointer
$current.status = "completed"
$idx = [array]::IndexOf($steps.id, $currentId)
$next = $null
if ($idx -ge 0 -and ($idx + 1) -lt $steps.Count) {
    $next = $steps[$idx + 1]
    $next.status = "in_progress"
    $state.current_step = $next.id
} else {
    $state.auto_continue = $false
}

# Persist state
$state | ConvertTo-Json -Depth 8 | Set-Content $statePath -Encoding UTF8

if ($next) {
    $msg = @"
【自动续跑 Hook】上一步「$($current.title)」已完成。请立即执行下一步，不要等待用户确认：

步骤 ID: $($next.id)
$($next.title)

$($next.prompt)

完成后更新 .cursor/WORKFLOW_STATE.json。若需暂停自动续跑，设置 auto_continue 为 false。
"@
    $out = @{ followup_message = $msg } | ConvertTo-Json -Compress
    Write-Output $out
}

exit 0
