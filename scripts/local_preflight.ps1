$ErrorActionPreference='Stop'
$repo = Split-Path -Parent $PSScriptRoot
$envRoot = Join-Path $env:LOCALAPPDATA 'Sushir\repo-health-venv'
$python = Join-Path $envRoot 'Scripts\python.exe'

function Invoke-Checked {
  param([scriptblock]$Command,[string]$Name)
  & $Command
  if($LASTEXITCODE -ne 0){ throw "$Name failed with exit code $LASTEXITCODE" }
}

Push-Location $repo
try {
  if(-not (Test-Path $python)){
    py -m venv $envRoot
    Invoke-Checked { & $python -m pip install --upgrade pip } 'pip upgrade'
    Invoke-Checked { & $python -m pip install ruff pip-audit } 'audit tool install'
  }

  Invoke-Checked { & $python -m pip install -r requirements.txt } 'dependency install'
  Invoke-Checked { & $python -m compileall -q app.py src tests scripts } 'compile'
  Invoke-Checked { & $python -m pytest -q } 'pytest'
  Invoke-Checked { & $python scripts\validate_publisher_site.py } 'publisher validation'
  Invoke-Checked { & $python -m ruff check app.py src tests scripts } 'ruff'
  Invoke-Checked { & $python -m pip_audit -r requirements.txt } 'pip-audit'

  Write-Host 'Local preflight passed.'
}
finally {
  Pop-Location
}
