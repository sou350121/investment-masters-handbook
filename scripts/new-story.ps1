param(
  [Parameter(Mandatory=$true)][string]$Id,
  [Parameter(Mandatory=$true)][string]$Title
)

$scriptPath = Join-Path $PSScriptRoot "new-story.py"
python $scriptPath --id $Id --title $Title
exit $LASTEXITCODE
