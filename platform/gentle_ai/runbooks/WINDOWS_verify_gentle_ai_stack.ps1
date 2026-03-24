param(
    [string]$RepoRoot = ""
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

$checks = @()

function Add-Check {
    param(
        [string]$Name,
        [bool]$Pass,
        [string]$Evidence
    )
    $script:checks += [pscustomobject]@{
        check = $Name
        status = if ($Pass) { "PASS" } else { "FAIL" }
        evidence = $Evidence
    }
}

Set-Location $RepoRoot

$gentle = Get-Command gentle-ai -ErrorAction SilentlyContinue
Add-Check -Name "gentle-ai command" -Pass ($null -ne $gentle) -Evidence ($(if ($gentle) { $gentle.Source } else { "not found" }))

$engram = Get-Command engram -ErrorAction SilentlyContinue
Add-Check -Name "engram command" -Pass ($null -ne $engram) -Evidence ($(if ($engram) { $engram.Source } else { "not found" }))

if (Test-Path $bashPath) {
    $ggaVersionRaw = & $bashPath -lc "command -v gga >/dev/null 2>&1 && gga version || echo 'gga not found'"
    $ggaVersion = (($ggaVersionRaw | Out-String).Trim())
    Add-Check -Name "gga via Git Bash" -Pass ($ggaVersion -match "^gga v") -Evidence $ggaVersion
} else {
    Add-Check -Name "gga via Git Bash" -Pass $false -Evidence "Git Bash missing at $bashPath"
}

try {
    $engramStats = engram stats 2>&1
    Add-Check -Name "engram stats" -Pass ($LASTEXITCODE -eq 0) -Evidence (($engramStats | Select-Object -First 1) -join " ")
} catch {
    Add-Check -Name "engram stats" -Pass $false -Evidence $_.Exception.Message
}

if (Test-Path $bashPath) {
    $ggaConfigRaw = & $bashPath -lc "cd '$repoUnix' && gga config >/dev/null 2>&1 && echo ok || echo fail"
    $ggaConfig = (($ggaConfigRaw | Out-String).Trim())
    Add-Check -Name "gga config on repo" -Pass ($ggaConfig -eq "ok") -Evidence $ggaConfig
} else {
    Add-Check -Name "gga config on repo" -Pass $false -Evidence "Git Bash unavailable"
}

Write-Host ""
Write-Host "Gentle AI Stack Verification"
Write-Host "Repo: $RepoRoot"
Write-Host ""

$checks | Format-Table -AutoSize

$failed = @($checks | Where-Object { $_.status -eq "FAIL" })
if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Stack verification failed. Review FAIL rows."
    exit 1
}

Write-Host ""
Write-Host "Stack verification passed."
exit 0
