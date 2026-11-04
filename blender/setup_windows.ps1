<#
.SYNOPSIS
Install everything the Duo Display build log needs on Windows: Blender 4.2 LTS,
Python 3 with Pillow, and ffmpeg.

.DESCRIPTION
Uses winget, which ships with Windows 10 (1809 or later) and Windows 11. Each
package is skipped if it is already installed, so the script is safe to run
again. When it finishes, open a new terminal so the updated PATH applies.

.EXAMPLE
.\blender\setup_windows.ps1

.EXAMPLE
.\blender\setup_windows.ps1 -SkipBlender
#>
param(
	[switch]$SkipBlender,
	[switch]$SkipPython,
	[switch]$SkipFfmpeg
)
$ErrorActionPreference = "Stop"

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
	throw "winget is missing. Install 'App Installer' from the Microsoft Store, then run this script again."
}

function Install-Package([string]$Id, [string]$Label) {
	Write-Host "`n==> $Label" -ForegroundColor Cyan
	winget list --id $Id --exact --accept-source-agreements *> $null
	if ($LASTEXITCODE -eq 0) {
		Write-Host "    already installed"
		return
	}
	winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements
	if ($LASTEXITCODE -ne 0) { throw "winget could not install $Id (exit code $LASTEXITCODE)" }
}

if (-not $SkipBlender) { Install-Package "BlenderFoundation.Blender.LTS.4.2" "Blender 4.2 LTS" }
if (-not $SkipPython) { Install-Package "Python.Python.3.13" "Python 3.13" }
if (-not $SkipFfmpeg) { Install-Package "Gyan.FFmpeg" "ffmpeg" }

# Pick up PATH changes from the installers without opening a new terminal.
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
	[Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "`n==> Pillow" -ForegroundColor Cyan
py -m pip install --upgrade --quiet pillow
if ($LASTEXITCODE -ne 0) { throw "pip could not install Pillow" }

Write-Host "`n==> Check" -ForegroundColor Cyan
$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
if (Test-Path $blender) {
	& $blender --version | Select-Object -First 1
} else {
	Write-Warning "Blender 4.2 is not at $blender. Pass its path to render_build_log.ps1 with -Blender."
}
py -c "import PIL; print('Pillow', PIL.__version__)"
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
	ffmpeg -hide_banner -version | Select-Object -First 1
} else {
	Write-Warning "ffmpeg is installed but not on PATH yet. Open a new terminal."
}

Write-Host "`nReady. Render the build log, or your own two names:" -ForegroundColor Green
Write-Host "  .\blender\render_build_log.ps1"
Write-Host "  .\blender\render_build_log.ps1 -Left ALPHA -Right BRAVO"
