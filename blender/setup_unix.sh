#!/usr/bin/env bash
# Install everything the Duo Display build log needs on macOS or Linux:
# Blender 4.2 LTS, Python 3 with Pillow, and ffmpeg.
#
#   ./blender/setup_unix.sh
#   BLENDER_VERSION=4.2.23 ./blender/setup_unix.sh
#
# Blender is pinned to a 4.2 LTS release, downloaded from blender.org, checked
# against the published SHA-256, and unpacked into your home folder, so it
# needs no admin rights. Homebrew's blender@lts cask now tracks a newer series,
# which is why the script does not use it. Pillow and ffmpeg come from Homebrew
# on macOS and from the system package manager on Linux (which asks for sudo).
# Safe to run again: anything already installed is skipped.
set -euo pipefail

V="${BLENDER_VERSION:-4.2.23}"
SERIES="${V%.*}"
BASE="https://download.blender.org/release/Blender$SERIES"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

say() { printf '\n==> %s\n' "$*"; }

# Download one release file and check it against blender.org's checksum list.
fetch_verified() {
	curl -fL --progress-bar -o "$TMP/$1" "$BASE/$1"
	curl -fsSL -o "$TMP/sums" "$BASE/blender-$V.sha256"
	local want got
	want="$(awk -v f="$1" '$2 == f { print $1 }' "$TMP/sums")"
	[ -n "$want" ] || { echo "blender.org publishes no checksum for $1"; exit 1; }
	if command -v sha256sum >/dev/null; then
		got="$(sha256sum "$TMP/$1" | cut -d' ' -f1)"
	else
		got="$(shasum -a 256 "$TMP/$1" | cut -d' ' -f1)"
	fi
	[ "$got" = "$want" ] || { echo "Checksum mismatch for $1"; exit 1; }
	echo "Checksum OK: $1"
}

case "$(uname -s)" in
Darwin)
	command -v brew >/dev/null || { echo "Homebrew is required first: https://brew.sh"; exit 1; }
	say "ffmpeg and Pillow (Homebrew)"
	brew install ffmpeg pillow
	APP="$HOME/Applications/Blender $SERIES.app"
	if [ ! -d "$APP" ]; then
		say "Blender $V"
		if [ "$(uname -m)" = arm64 ]; then f="blender-$V-macos-arm64.dmg"; else f="blender-$V-macos-x64.dmg"; fi
		fetch_verified "$f"
		hdiutil attach -nobrowse -quiet -mountpoint "$TMP/mnt" "$TMP/$f"
		mkdir -p "$HOME/Applications"
		cp -R "$TMP/mnt/Blender.app" "$APP"
		hdiutil detach -quiet "$TMP/mnt"
	fi
	B="$APP/Contents/MacOS/Blender"
	;;
Linux)
	[ "$(uname -m)" = x86_64 ] || { echo "Blender publishes Linux builds for x86_64 only."; exit 1; }
	say "ffmpeg, Pillow and fonts (system packages)"
	if command -v apt-get >/dev/null; then
		sudo apt-get update
		sudo apt-get install -y ffmpeg python3-pil fonts-dejavu-core curl xz-utils \
			libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 libgl1
	elif command -v dnf >/dev/null; then
		sudo dnf install -y python3-pillow dejavu-sans-fonts dejavu-sans-mono-fonts curl xz
		sudo dnf install -y ffmpeg ||
			echo "ffmpeg with H.264 needs RPM Fusion on Fedora: https://rpmfusion.org/Configuration"
	elif command -v pacman >/dev/null; then
		sudo pacman -S --needed --noconfirm ffmpeg python-pillow ttf-dejavu curl xz
	elif command -v zypper >/dev/null; then
		sudo zypper install -y ffmpeg python3-Pillow dejavu-fonts curl xz
	else
		echo "Install ffmpeg and Pillow with your package manager, then run this again."
	fi
	DEST="$HOME/.local/opt/blender-$V"
	if [ ! -x "$DEST/blender" ]; then
		say "Blender $V"
		f="blender-$V-linux-x64.tar.xz"
		fetch_verified "$f"
		mkdir -p "$DEST"
		tar -xJf "$TMP/$f" -C "$DEST" --strip-components=1
	fi
	B="$DEST/blender"
	;;
*)
	echo "On Windows, run blender\\setup_windows.ps1 instead."
	exit 1
	;;
esac

say "Check"
"$B" --version | head -n 1
ffmpeg -hide_banner -version | head -n 1
python3 -c "import PIL; print('Pillow', PIL.__version__)"

say "Ready"
echo "Render the build log, or your own two names:"
echo "  BLENDER=\"$B\" ./blender/render_build_log.sh"
echo "  BLENDER=\"$B\" LEFT=ALPHA RIGHT=BRAVO ./blender/render_build_log.sh"
