param(
    [ValidateSet("smoke", "standard", "full")]
    [string]$Profile = "standard",
    [ValidateSet("delivery", "router", "decision", "debug", "behavior")]
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
    [switch]$ComboMatrix,
    [switch]$NoBuilds,
    [switch]$SelfTest,
    [switch]$FailOnCellFailure,
    [switch]$RequireStableRanking,
    [switch]$ProgressiveSelfTest,
    [switch]$TreeSelfTest,
    [string]$Rescore = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

if ($SelfTest) {
    Push-Location $repoRoot
    try {
        & python -m unittest benchmarks.test_benchmarks benchmarks.test_stability benchmarks.test_catalog
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

if ($ProgressiveSelfTest) {
    Push-Location $repoRoot
    try {
        & python benchmarks/progressive_validation.py --self-test
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & python -m unittest benchmarks.test_progressive_validation
        exit $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}

if ($TreeSelfTest) {
    Push-Location $repoRoot
    try {
        & python benchmarks/tree_validation.py --self-test
        exit $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}

$effectiveRuns = if ($Runs -gt 0) {
    $Runs
}
elseif ($Profile -eq "smoke") {
    1
}
else {
    3
}

if ($RequireStableRanking -and $Rescore) {
    Write-Error "-RequireStableRanking cannot be combined with -Rescore; gate the rescored run directly with benchmarks/check_stability.py."
    exit 2
}
if ($RequireStableRanking -and $effectiveRuns -lt 3) {
    Write-Error "Stable ranking requires at least 3 runs per cell; effective runs=$effectiveRuns."
    exit 2
}
if ($RequireStableRanking -and $NoBuilds -and (($Suite.Count -eq 0) -or ($Suite -contains "delivery"))) {
    Write-Error "Stable Delivery ranking requires production build evidence; remove -NoBuilds."
    exit 2
}
if ($RequireStableRanking -and -not $Output) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Output = Join-Path $repoRoot "benchmark-results/stable-$stamp"
}

$arguments = @(
    (Join-Path $scriptDir "run_catalog.py"),
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
if ($ComboMatrix) { $arguments += "--combo-matrix" }
if ($NoBuilds) { $arguments += "--no-builds" }
if ($SelfTest) { $arguments += "--self-test" }
if ($FailOnCellFailure) { $arguments += "--fail-on-cell-failure" }
if ($Rescore) { $arguments += @("--rescore", $Rescore) }

& python @arguments
$benchmarkExit = $LASTEXITCODE
if ($benchmarkExit -ne 0) { exit $benchmarkExit }

if ($RequireStableRanking) {
    $gateArguments = @(
        (Join-Path $scriptDir "check_stability.py"),
        $Output,
        "--min-runs", "3"
    )
    foreach ($item in $Suite) { $gateArguments += @("--suite", $item) }
    & python @gateArguments
    exit $LASTEXITCODE
}

exit 0
