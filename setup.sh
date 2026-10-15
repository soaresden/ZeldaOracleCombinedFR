#!/bin/bash
# Prépare l'environnement de compilation (une seule fois) :
# - le désassemblage oracles-disasm, branche fr/crossworld1 du fork
#   soaresden/oracles-disasm (crossworld + VF déjà générée + 3e base de texte)
# - WLA-DX v9.11 (la branche crossworld date de 2020 : WLA-DX v10 change la
#   priorité des opérateurs et ne l'assemble plus)
# Requiert MSYS2 (C:\msys64) avec cmake, make et gcc (mingw64), et Python 3
# avec pyyaml et pillow (pip install pyyaml pillow).
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"

if [ ! -d "$ROOT/oracles-disasm" ]; then
    git clone -b fr/crossworld1 https://github.com/soaresden/oracles-disasm.git "$ROOT/oracles-disasm" || true
    cd "$ROOT/oracles-disasm"
    # tools/aux : nom réservé sous Windows, inutile pour compiler
    git sparse-checkout set --no-cone '/*' '!/tools/aux/'
    # Les liens symboliques common.py deviennent des fichiers texte sous Windows
    for f in tools/build/common.py tools/dump/common.py tools/misc/common.py; do
        cp tools/common.py "$f"
        git update-index --assume-unchanged "$f"
    done
fi

WLA="$ROOT/tools-build/wla-dx-9"
if [ ! -x "$WLA/build/binaries/wla-gb.exe" ]; then
    mkdir -p "$ROOT/tools-build"
    [ -d "$WLA" ] || git clone --depth 1 -b v9.11-fix-fix-fix https://github.com/vhelin/wla-dx.git "$WLA"
    cmake -S "$WLA" -B "$WLA/build" -G "MSYS Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
    cmake --build "$WLA/build" --target wla-gb wlalink -j8
fi
echo "Prêt : ./build.sh compile la VF. Pour régénérer la VF depuis les ROMs EU :"
echo "  python fr/make_fr_text.py && python fr/import_fr_gfx.py && python fr/import_fr_font.py"
