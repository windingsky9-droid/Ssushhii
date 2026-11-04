<#
.SYNOPSIS
Render the Duo Display build log with Blender 4.2 LTS: six build stages,
a 1-to-64-sample convergence ladder, the final shots, and the timelapse.

.DESCRIPTION
Output lands in blender\renders (git-ignored). Requires Blender 4.2 LTS,
Python with Pillow (py -m pip install pillow) and ffmpeg on PATH for the
timelapse and GIF.

.EXAMPLE
.\blender\render_build_log.ps1

.EXAMPLE
.\blender\render_build_log.ps1 -Left ALPHA -Right BRAVO -Blender "D:\Blender 4.2\blender.exe"
#>
param(
	[string]$Blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
	[string]$Out = "$PSScriptRoot\renders",
	[string]$Left = "SUSHIR",
	[string]$Right = "STUDIO",
	[string]$MonoFont = "C:\Windows\Fonts\consola.ttf"
)
$ErrorActionPreference = "Stop"
$fonts = @("--font", "$PSScriptRoot\fonts\ChakraPetch-Bold.ttf", "--font-sub", "$PSScriptRoot\fonts\ChakraPetch-SemiBold.ttf")
$names = @("--left", $Left, "--right", $Right)

function Invoke-Render([string[]]$Rest) {
	& $Blender -b --factory-startup -noaudio --python "$PSScriptRoot\duo_display.py" -- @fonts @names @Rest
	if ($LASTEXITCODE -ne 0) { throw "Blender exited with code $LASTEXITCODE" }
}

foreach ($stage in 1..6) {
	Write-Host "Stage $stage of 6"
	Invoke-Render @("--stage", "$stage", "--shots", "hero", "--out", "$Out\stages", "--prefix", "stage$stage",
		"--width", "960", "--height", "540", "--samples", "32")
}
Write-Host "Convergence ladder"
Invoke-Render @("--stage", "6", "--shots", "hero", "--out", "$Out\ladder", "--prefix", "ladder",
	"--width", "960", "--height", "540", "--sample-ladder", "1,2,4,8,16,32,64")
Write-Host "Final shots, 1920x1080"
Invoke-Render @("--stage", "6", "--shots", "hero,left,right", "--out", "$Out\final", "--prefix", "duo-display", "--samples", "64")

py "$PSScriptRoot\assemble_build_log.py" --stages "$Out\stages" --ladder "$Out\ladder" --out "$Out\build-log" `
	--title "$Left x $Right - DUO DISPLAY" --font "$PSScriptRoot\fonts\ChakraPetch-Bold.ttf" `
	--sans "$PSScriptRoot\fonts\ChakraPetch-SemiBold.ttf" --mono $MonoFont
Write-Host "Done: $Out"
