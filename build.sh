#!/bin/bash
# Compile Ages + Seasons (branche poc/crossworld1) et les fusionne en une ROM 8 Mo.
# À lancer depuis Git Bash ou MSYS2. Pas de vrais liens symboliques sous Windows
# sans le mode développeur : on remplace le lien "build" du Makefile par une
# jonction de répertoire.
set -e
# Python Windows (avec pyyaml), résolu avant de passer devant les outils MSYS2
PYTHON="${PYTHON:-$(command -v python)}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="$ROOT/tools-build/wla-dx-9/build/binaries:/c/msys64/usr/bin:$PATH"
cd "$ROOT/oracles-disasm"

VANILLA=$(grep -q 'BUILD_VANILLA = true' Makefile && echo v || echo e)

build_game() {  # $1 = ages|seasons, $2 = AGES|SEASONS
    local dir="build_$1_$VANILLA"
    { [ -L build ] || [ -e build ]; } && /c/Windows/System32/cmd.exe //c "rmdir build" >/dev/null
    mkdir -p "$dir"
    /c/Windows/System32/cmd.exe //c "mklink /J build $dir" >/dev/null
    echo "===== $1 ====="
    env ROM_$2=1 make --no-print-directory -j8 PYTHON="$PYTHON" "$1.gbc"
}

build_game ages AGES
build_game seasons SEASONS
$PYTHON tools/misc/merge_games.py
mv -f combined.gbc "$ROOT/out/${OUT_NAME:-combined.gbc}"
echo "-> out/${OUT_NAME:-combined.gbc}"
