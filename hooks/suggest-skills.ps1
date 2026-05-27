param(
    [string]$InputPath,
    [string]$OutputPath = "reports/skill-suggestions.md",
    [switch]$FailOnSuggestions
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ScriptPath = Join-Path $RepoRoot "scripts/suggest_skill_updates.py"

$Arguments = @(
    $ScriptPath,
    "--repo-root", $RepoRoot,
    "--output", $OutputPath
)

if ($InputPath) {
    $Arguments += @("--input", (Resolve-Path $InputPath))
}

if ($FailOnSuggestions) {
    $Arguments += "--fail-on-suggestions"
}

python @Arguments
