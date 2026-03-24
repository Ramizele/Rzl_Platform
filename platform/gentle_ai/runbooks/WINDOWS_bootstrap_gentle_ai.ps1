param(
    [string]$Agents = "claude-code,vscode-copilot",
    [switch]$DryRun,
    [switch]$Apply,
    [switch]$EnableGga
)

$ErrorActionPreference = "Stop"

if ($DryRun -and $Apply) {
    throw "Use either -DryRun or -Apply, not both."
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\\..\\..")

$useDryRun = $true
if ($Apply) {
    $useDryRun = $false
}
if ($DryRun) {
    $useDryRun = $true
}

$mode = if ($Apply) { "apply" } else { "dry-run" }
Write-Host "[gentle-ai] Mode: $mode"
Write-Host "[gentle-ai] Agents: $Agents"
Write-Host "[gentle-ai] Components: context7,engram,sdd,skills"

if (-not (Get-Command gentle-ai -ErrorAction SilentlyContinue)) {
    Write-Host "[gentle-ai] CLI not found. Installing from upstream script..."
    irm https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.ps1 | iex
}

$args = @(
    "install",
    "--agent", $Agents,
    "--component", "context7,engram,sdd,skills",
    "--persona", "gentleman"
)

if ($useDryRun) {
    $args += "--dry-run"
}

Write-Host "[gentle-ai] Running: gentle-ai $($args -join ' ')"
& gentle-ai @args

if (-not $useDryRun -and $EnableGga) {
    $bashPath = "C:\\Program Files\\Git\\bin\\bash.exe"
    if (-not (Test-Path $bashPath)) {
        throw "Git Bash not found at '$bashPath'. Install Git for Windows to enable GGA."
    }
    $repoUnix = $repoRoot.Path -replace "\\", "/"
    if ($repoUnix -match "^([A-Za-z]):") {
        $drive = $Matches[1].ToLower()
        $repoUnix = "/$drive" + $repoUnix.Substring(2)
    }
    Write-Host "[gentle-ai] Enabling GGA in this repository via Git Bash..."
    & $bashPath -lc "cd '$repoUnix' && bash platform/gentle_ai/runbooks/GIT_BASH_enable_gga.sh"
}

Write-Host ""
Write-Host "[done] gentle-ai ecosystem configured."
