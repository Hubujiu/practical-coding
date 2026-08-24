param(
    [ValidateSet("skillsbench")]
    [string]$Benchmark = "skillsbench",
    [ValidateSet("smoke", "standard", "full")]
    [string]$Profile = "standard",
    [int]$Runs = 0,
    [int]$Workers = 3,
    [ValidateSet("docker", "daytona", "modal")]
    [string]$Sandbox = "docker",
    [string]$Model = "gpt-5.6-luna",
    [string]$Reasoning = "medium",
    [string]$Output = "",
    [string]$CacheRoot = "",
    [string[]]$Task = @(),
    [switch]$SkipOracle,
    [switch]$RequireStableRanking,
    [switch]$SelfTest
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

if ($Benchmark -ne "skillsbench") {
    Write-Error "Unsupported external benchmark: $Benchmark"
    exit 2
}

$adapter = Join-Path $scriptDir "external/skillsbench_adapter.py"
$arguments = @(
    $adapter,
    "--profile", $Profile,
    "--workers", $Workers,
    "--sandbox", $Sandbox,
    "--model", $Model,
    "--reasoning", $Reasoning
)

if ($Runs -gt 0) { $arguments += @("--runs", $Runs) }
if ($Output) { $arguments += @("--output", $Output) }
if ($CacheRoot) { $arguments += @("--cache-root", $CacheRoot) }
foreach ($item in $Task) { $arguments += @("--task", $item) }
if ($SkipOracle) { $arguments += "--skip-oracle" }
if ($RequireStableRanking) { $arguments += "--require-stable-ranking" }
if ($SelfTest) { $arguments += "--self-test" }

Push-Location $repoRoot
try {
    & python @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
