param(
    [string]$Agents = "claude-code,vscode-copilot",
    [string]$Components = "context7,engram,sdd,skills,persona,permissions,gga,theme",
    [string]$Persona = "gentleman",
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
Write-Host "[gentle-ai] Components: $Components"
Write-Host "[gentle-ai] Persona: $Persona"

if (-not (Get-Command gentle-ai -ErrorAction SilentlyContinue)) {
    Write-Host "[gentle-ai] CLI not found. Installing from upstream script..."
    irm https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.ps1 | iex
}

$args = @(
    "install",
    "--agent", $Agents,
    "--component", $Components,
    "--persona", $Persona
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

    $ggaHealth = (& $bashPath -lc "command -v gga >/dev/null 2>&1 && gga version || echo 'gga missing'").Trim()
    Write-Host "[gentle-ai] GGA health: $ggaHealth"
}

Write-Host ""
Write-Host "[done] gentle-ai ecosystem configured."
