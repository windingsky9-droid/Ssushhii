<#
.SYNOPSIS
Render the Duo Display build log with Blender 4.2 LTS: six build stages,
a 1-to-64-sample convergence ladder, the final shots, the timelapse and the
making-of video.

.DESCRIPTION
Output lands in blender\renders (git-ignored). Requires Blender 4.2 LTS,
Python with Pillow and ffmpeg on PATH; setup_windows.ps1 installs all three.

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
if ($LASTEXITCODE -ne 0) { throw "assemble_build_log.py exited with code $LASTEXITCODE" }

Write-Host "Making-of video"
py "$PSScriptRoot\make_making_of.py" --stages "$Out\stages" --final "$Out\final\duo-display-hero.png" `
	--out "$Out\making-of\making-of.mp4" --title "$Left x $Right" --mono $MonoFont
if ($LASTEXITCODE -ne 0) { throw "make_making_of.py exited with code $LASTEXITCODE" }
Write-Host "Done: $Out"
