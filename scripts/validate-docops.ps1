param(
  [string]$StoriesDir = "stories",
  [string]$PromptsDir = "prompts",
  [string]$SessionsDir = "sessions",
  [string]$FeaturesDir = "docs/features"
)

$scriptPath = Join-Path $PSScriptRoot "validate-docops.py"
python $scriptPath
exit $LASTEXITCODE
