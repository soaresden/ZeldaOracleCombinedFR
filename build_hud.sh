#!/bin/bash
# Compile Ages et Seasons d'origine (US) avec seulement la barre d'état en bas
# (branche hack/hud-bottom, dossier oracles-hud), puis fait les patchs BPS de
# la page (docs/patches/hud-ages.bps, hud-seasons.bps) depuis les ROMs US.
set -e
PYTHON="${PYTHON:-$(command -v python)}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="$ROOT/tools-build/wla-dx-9/build/binaries:/c/msys64/usr/bin:$PATH"
cd "$ROOT/oracles-hud"

build_game() {  # $1 = ages|seasons, $2 = AGES|SEASONS
    local dir="build_$1"
    { [ -L build ] || [ -e build ]; } && /c/Windows/System32/cmd.exe //c "rmdir build" >/dev/null
    mkdir -p "$dir"
    /c/Windows/System32/cmd.exe //c "mklink /J build $dir" >/dev/null
    echo "===== $1 ====="
    env ROM_$2=1 make --no-print-directory -j8 PYTHON="$PYTHON" "$1.gbc"
}

build_game ages AGES
build_game seasons SEASONS
cp ages.gbc "$ROOT/out/hud-ages.gbc"
cp seasons.gbc "$ROOT/out/hud-seasons.gbc"
echo "-> out/hud-ages.gbc out/hud-seasons.gbc"
