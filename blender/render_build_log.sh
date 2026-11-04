#!/usr/bin/env bash
# Render the Duo Display build log with Blender 4.2 LTS: six build stages, a
# 1-to-64-sample convergence ladder, the final shots, the timelapse and the
# making-of video.
#
#   ./blender/render_build_log.sh                 # SUSHIR x STUDIO
#   LEFT=ALPHA RIGHT=BRAVO ./blender/render_build_log.sh
#   BLENDER=/opt/blender/blender ./blender/render_build_log.sh /tmp/out
#
# Needs Blender 4.2 LTS, Python 3 with Pillow, and ffmpeg; setup_unix.sh
# installs all three. Output defaults to blender/renders (git-ignored).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
B="${BLENDER:-blender}"
OUT="${1:-$HERE/renders}"
LEFT="${LEFT:-SUSHIR}"
RIGHT="${RIGHT:-STUDIO}"
MONO="${MONO_FONT:-}"
if [ -z "$MONO" ]; then
	for f in /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf \
		/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf \
		/usr/share/fonts/TTF/DejaVuSansMono.ttf /System/Library/Fonts/Menlo.ttc; do
		if [ -f "$f" ]; then MONO="$f"; break; fi
	done
fi
[ -n "$MONO" ] || { echo "No monospace font found; set MONO_FONT=/path/to/font.ttf"; exit 1; }
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
echo "Making-of video"
python3 "$HERE/make_making_of.py" --stages "$OUT/stages" --final "$OUT/final/duo-display-hero.png" \
	--out "$OUT/making-of/making-of.mp4" --title "$LEFT × $RIGHT" --mono "$MONO"
echo "Done: $OUT"
