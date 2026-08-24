param(
    [ValidateSet("smoke", "standard", "full")]
    [string]$Profile = "standard",
    [ValidateSet("delivery", "router", "decision", "debug")]
    [string[]]$Suite = @(),
    [string[]]$Case = @(),
    [string[]]$Arm = @(),
    [int]$Runs = 0,
    [int]$Workers = 3,
    [string]$Output = "",
    [string]$SourcesRoot = "",
    [string]$BaselineSkill = "",
    [string]$BaselineRef = "",
    [switch]$IncludeBaseline,
    [switch]$NoBuilds,
    [switch]$SelfTest,
    [switch]$FailOnCellFailure,
    [string]$Rescore = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

if ($SelfTest) {
    Push-Location $repoRoot
    try {
        & python -m unittest benchmarks.test_benchmarks
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

$arguments = @(
    (Join-Path $scriptDir "run_benchmarks.py"),
    "--profile", $Profile,
    "--workers", $Workers
)

if ($Runs -gt 0) { $arguments += @("--runs", $Runs) }
foreach ($item in $Suite) { $arguments += @("--suite", $item) }
foreach ($item in $Case) { $arguments += @("--case", $item) }
foreach ($item in $Arm) { $arguments += @("--arm", $item) }
if ($Output) { $arguments += @("--output", $Output) }
if ($SourcesRoot) { $arguments += @("--sources-root", $SourcesRoot) }
if ($BaselineSkill) { $arguments += @("--baseline-skill", $BaselineSkill) }
if ($BaselineRef) { $arguments += @("--baseline-ref", $BaselineRef) }
if ($IncludeBaseline) { $arguments += "--include-baseline" }
if ($NoBuilds) { $arguments += "--no-builds" }
if ($SelfTest) { $arguments += "--self-test" }
if ($FailOnCellFailure) { $arguments += "--fail-on-cell-failure" }
if ($Rescore) { $arguments += @("--rescore", $Rescore) }

& python @arguments
exit $LASTEXITCODE
