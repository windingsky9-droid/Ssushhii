param(
    [ValidateSet('All', 'Python', 'JavaScript')]
    [string]$Mode = 'All'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
$previous = Get-Location

function Invoke-Checked {
    param(
        [string]$Label,
        [string]$Executable,
        [string[]]$Arguments
    )
    Write-Host ""
    Write-Host "[RUN] $Label" -ForegroundColor Cyan
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
    Write-Host "[PASS] $Label" -ForegroundColor Green
}

try {
    Set-Location $root
    Write-Host "OMEN verification - $root" -ForegroundColor Cyan
    if ($Mode -in @('All', 'Python')) {
        $venv = Join-Path $root '.venv\Scripts\python.exe'
        if (-not (Test-Path $venv) -and (Get-Command git -ErrorAction SilentlyContinue)) {
            $commonDir = & git -C $root rev-parse --path-format=absolute --git-common-dir
            if ($LASTEXITCODE -eq 0 -and $commonDir) {
                $sharedVenv = Join-Path (Split-Path -Parent $commonDir.Trim()) '.venv\Scripts\python.exe'
                if (Test-Path $sharedVenv) { $venv = $sharedVenv }
            }
        }
        if (Test-Path $venv) {
            $python = $venv
            $prefix = @()
        } elseif (Get-Command py -ErrorAction SilentlyContinue) {
            $python = (Get-Command py).Source
            $prefix = @('-3')
        } elseif (Get-Command python -ErrorAction SilentlyContinue) {
            $python = (Get-Command python).Source
            $prefix = @()
        } else {
            throw 'Python not found. Install Python or create .venv in this repository.'
        }
        Invoke-Checked 'Python tests' $python ($prefix + @('-m', 'pytest', '-q'))
        Invoke-Checked 'Python syntax' $python ($prefix + @('-m', 'compileall', '-q', 'app.py', 'src', 'scripts'))
    }
    if ($Mode -in @('All', 'JavaScript')) {
        $node = Get-Command node -ErrorAction SilentlyContinue
        if (-not $node) {
            throw 'Node.js not found. Install Node.js to validate browser JavaScript.'
        }
        Invoke-Checked 'Dashboard JavaScript syntax' $node.Source @('--check', 'static/app.js')
        Invoke-Checked 'Public demo JavaScript syntax' $node.Source @('--check', 'public-demo/app.js')
    }
    Write-Host ""
    Write-Host "[SUCCESS] Requested checks passed." -ForegroundColor Green
} catch {
    [Console]::Error.WriteLine("[FAIL] $($_.Exception.Message)")
    exit 1
} finally {
    Set-Location $previous
}
