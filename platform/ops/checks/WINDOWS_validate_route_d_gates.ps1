param(
    [string]$RepoRoot = "",
    [switch]$SkipSweep,
    [switch]$KeepHistory
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..\\..")).Path
}

$bashPath = "C:\\Program Files\\Git\\bin\\bash.exe"
$repoUnix = $RepoRoot -replace "\\", "/"
if ($repoUnix -match "^([A-Za-z]):") {
    $drive = $Matches[1].ToLower()
    $repoUnix = "/$drive" + $repoUnix.Substring(2)
}

$results = @()

function Add-Result {
    param(
        [string]$Gate,
        [string]$Check,
        [bool]$Pass,
        [string]$Evidence
    )
    $script:results += [pscustomobject]@{
        gate = $Gate
        check = $Check
        status = if ($Pass) { "PASS" } else { "FAIL" }
        evidence = $Evidence
    }
}

function Test-RepoPath {
    param([string]$RelativePath)
    return (Test-Path (Join-Path $RepoRoot $RelativePath))
}

function Sanitize-Text {
    param([string]$Value)
    if ($null -eq $Value) {
        return ""
    }
    $text = (($Value | Out-String).Trim())
    $esc = [char]27
    $text = $text -replace ([regex]::Escape($esc) + "\[[0-9;]*m"), ""
    $text = $text -replace "\r?\n+", " "
    $text = $text -replace "\|", "/"
    return $text
}

Set-Location $RepoRoot

# G1 - Baseline Approved
$canonicalBuckets = @(
    "platform",
    "core",
    "rzl_database",
    "rzl_persona",
    "rzl_gpt_apps",
    "plugins",
    "rzl_gdrive"
)
foreach ($bucket in $canonicalBuckets) {
    $ok = Test-RepoPath $bucket
    Add-Result -Gate "G1" -Check "bucket '$bucket' exists" -Pass $ok -Evidence ($(if ($ok) { "ok" } else { "missing" }))
}

$manifestPath = "platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml"
$manifestOk = Test-RepoPath $manifestPath
Add-Result -Gate "G1" -Check "manifest present" -Pass $manifestOk -Evidence $manifestPath

# G2 - Design Frozen
$g2Artifacts = @(
    "platform/architecture/ROADMAP_route_d_staged_execution_v1.md",
    "platform/governance/rules/RULESET_route_d_phase_gates_v1.md",
    "platform/governance/agents/CONTRACT_agent_teams_lite_v1.md",
    "platform/ops/checks/CHECKLIST_route_d_gate_validation_v1.md"
)
foreach ($artifact in $g2Artifacts) {
    $ok = Test-RepoPath $artifact
    Add-Result -Gate "G2" -Check "artifact '$artifact' present" -Pass $ok -Evidence ($(if ($ok) { "ok" } else { "missing" }))
}

# G3 - Build Complete
$g3Artifacts = @(
    "platform/gentle_ai/runbooks/WINDOWS_bootstrap_gentle_ai.ps1",
    "platform/gentle_ai/runbooks/WINDOWS_verify_gentle_ai_stack.ps1",
    ".gga"
)
foreach ($artifact in $g3Artifacts) {
    $ok = Test-RepoPath $artifact
    Add-Result -Gate "G3" -Check "artifact '$artifact' present" -Pass $ok -Evidence ($(if ($ok) { "ok" } else { "missing" }))
}

# G4 - Validation OK
$gentle = Get-Command gentle-ai -ErrorAction SilentlyContinue
Add-Result -Gate "G4" -Check "gentle-ai command available" -Pass ($null -ne $gentle) -Evidence ($(if ($gentle) { $gentle.Source } else { "not found" }))

$engram = Get-Command engram -ErrorAction SilentlyContinue
Add-Result -Gate "G4" -Check "engram command available" -Pass ($null -ne $engram) -Evidence ($(if ($engram) { $engram.Source } else { "not found" }))

if ($null -ne $engram) {
    try {
        $engramStats = engram stats 2>&1
        Add-Result -Gate "G4" -Check "engram stats command" -Pass ($LASTEXITCODE -eq 0) -Evidence (($engramStats | Select-Object -First 1) -join " ")
    } catch {
        Add-Result -Gate "G4" -Check "engram stats command" -Pass $false -Evidence $_.Exception.Message
    }
} else {
    Add-Result -Gate "G4" -Check "engram stats command" -Pass $false -Evidence "engram command unavailable"
}

if (Test-Path $bashPath) {
    $ggaVersionRaw = & $bashPath -lc "command -v gga >/dev/null 2>&1 && gga version || echo 'gga not found'"
    $ggaVersion = (($ggaVersionRaw | Out-String).Trim())
    Add-Result -Gate "G4" -Check "gga via Git Bash" -Pass ($ggaVersion -match "^gga v") -Evidence $ggaVersion
    $ggaConfigRaw = & $bashPath -lc "cd '$repoUnix' && gga config >/dev/null 2>&1 && echo ok || echo fail"
    $ggaConfig = (($ggaConfigRaw | Out-String).Trim())
    Add-Result -Gate "G4" -Check "gga config on repo" -Pass ($ggaConfig -eq "ok") -Evidence $ggaConfig
} else {
    Add-Result -Gate "G4" -Check "gga via Git Bash" -Pass $false -Evidence "Git Bash missing at $bashPath"
    Add-Result -Gate "G4" -Check "gga config on repo" -Pass $false -Evidence "Git Bash unavailable"
}

if (-not $SkipSweep) {
    try {
        $sweepOutput = python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/reports/local --tag route_d_g4 2>&1
        Add-Result -Gate "G4" -Check "bucket sweep command" -Pass ($LASTEXITCODE -eq 0) -Evidence (($sweepOutput | Select-Object -Last 1) -join " ")
    } catch {
        Add-Result -Gate "G4" -Check "bucket sweep command" -Pass $false -Evidence $_.Exception.Message
    }
} else {
    Add-Result -Gate "G4" -Check "bucket sweep command" -Pass $true -Evidence "skipped by -SkipSweep"
}

# G5 - Release Approved
$g5Artifacts = @(
    "platform/ops/workbenches/WB_route_d_execution_2026-03-24.md"
)
foreach ($artifact in $g5Artifacts) {
    $ok = Test-RepoPath $artifact
    Add-Result -Gate "G5" -Check "artifact '$artifact' present" -Pass $ok -Evidence ($(if ($ok) { "ok" } else { "missing" }))
}

$gateNames = @("G1", "G2", "G3", "G4", "G5")
$summary = foreach ($gate in $gateNames) {
    $gateRows = @($results | Where-Object { $_.gate -eq $gate })
    $gatePass = ($gateRows.Count -gt 0 -and @($gateRows | Where-Object { $_.status -eq "FAIL" }).Count -eq 0)
    [pscustomobject]@{
        gate = $gate
        status = if ($gatePass) { "PASS" } else { "FAIL" }
        checks = $gateRows.Count
    }
}

$reportDir = Join-Path $RepoRoot "platform/ops/checks"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$generatedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$reportLatest = Join-Path $reportDir "REPORT_route_d_gate_status_latest.md"
$reportStamped = Join-Path $reportDir ("REPORT_route_d_gate_status_{0}.md" -f $timestamp)

$lines = @()
$lines += "# Report - Route D Gate Status"
$lines += ""
$lines += ('- generated_at: `' + $generatedAt + '`')
$lines += ('- repo_root: `' + $RepoRoot + '`')
$lines += ""
$lines += "## Gate summary"
$lines += "| Gate | Status | Checks |"
$lines += "| --- | --- | ---: |"
foreach ($row in $summary) {
    $lines += "| $($row.gate) | $($row.status) | $($row.checks) |"
}
$lines += ""
$lines += "## Detailed checks"
$lines += "| Gate | Check | Status | Evidence |"
$lines += "| --- | --- | --- | --- |"
foreach ($row in $results) {
    $safeEvidence = Sanitize-Text $row.evidence
    $lines += "| $($row.gate) | $($row.check) | $($row.status) | $safeEvidence |"
}
$lines += ""

$content = ($lines -join [Environment]::NewLine) + [Environment]::NewLine
Set-Content -Path $reportLatest -Value $content -Encoding UTF8
if ($KeepHistory) {
    Set-Content -Path $reportStamped -Value $content -Encoding UTF8
}

Write-Host ""
Write-Host "Route D gate validation completed."
Write-Host "Report: $reportLatest"
Write-Host ""
$summary | Format-Table -AutoSize

$failedGates = @($summary | Where-Object { $_.status -eq "FAIL" })
if ($failedGates.Count -gt 0) {
    exit 1
}
exit 0
