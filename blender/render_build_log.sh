#!/usr/bin/env bash
# Render the Duo Display build log with Blender 4.2 LTS: six build stages, a
# 1-to-64-sample convergence ladder, the final shots, and the timelapse.
#
#   ./blender/render_build_log.sh                 # SUSHIR x STUDIO
#   LEFT=ALPHA RIGHT=BRAVO ./blender/render_build_log.sh
#   BLENDER=/opt/blender/blender ./blender/render_build_log.sh /tmp/out
#
# Needs Blender 4.2 LTS, Python 3 with Pillow, and ffmpeg. Output defaults to
# blender/renders (git-ignored).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
B="${BLENDER:-blender}"
OUT="${1:-$HERE/renders}"
LEFT="${LEFT:-SUSHIR}"
RIGHT="${RIGHT:-STUDIO}"
MONO="${MONO_FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf}"
FONTS=(--font "$HERE/fonts/ChakraPetch-Bold.ttf" --font-sub "$HERE/fonts/ChakraPetch-SemiBold.ttf")

render() {
	"$B" -b --factory-startup -noaudio --python "$HERE/duo_display.py" -- \
		"${FONTS[@]}" --left "$LEFT" --right "$RIGHT" "$@"
}

for stage in 1 2 3 4 5 6; do
	echo "Stage $stage of 6"
	render --stage "$stage" --shots hero --out "$OUT/stages" --prefix "stage$stage" \
		--width 960 --height 540 --samples 32
done
echo "Convergence ladder"
render --stage 6 --shots hero --out "$OUT/ladder" --prefix ladder \
	--width 960 --height 540 --sample-ladder 1,2,4,8,16,32,64
echo "Final shots, 1920x1080"
render --stage 6 --shots hero,left,right --out "$OUT/final" --prefix duo-display --samples 64

python3 "$HERE/assemble_build_log.py" --stages "$OUT/stages" --ladder "$OUT/ladder" \
	--out "$OUT/build-log" --title "$LEFT × $RIGHT · DUO DISPLAY" \
	--font "$HERE/fonts/ChakraPetch-Bold.ttf" --sans "$HERE/fonts/ChakraPetch-SemiBold.ttf" --mono "$MONO"
echo "Done: $OUT"
