#!/bin/bash
# Jeux d'origine séparés avec seulement la barre d'état en bas, dans les 5 langues
# des ROMs Europe : compile oracles-hud (branche hack/hud-bottom) pour chaque
# langue, puis fait les patchs BPS de la page (docs/patches/hud/).
#   ./build_hud_all.sh            -> toutes les langues
#   ./build_hud_all.sh fr de      -> seulement celles-ci
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-$(command -v python)}"
export PYTHONIOENCODING=utf-8
export ZOC_DISASM="$ROOT/oracles-hud" ZOC_TEXT_BASE=309a2cff
LANGS="${*:-en fr de it es}"

gen() {  # textes et images d'une langue dans oracles-hud
    "$PYTHON" fr/make_fr_text.py --lang="$1" >/dev/null
    "$PYTHON" fr/import_fr_gfx.py --lang="$1" >/dev/null
}

for lang in $LANGS; do
    echo "===== langue $lang ====="
    gen "$lang"
    bash build_hud.sh > "out/build_hud_$lang.log" 2>&1 || { tail -20 "out/build_hud_$lang.log"; exit 1; }
    mv -f out/hud-ages.gbc "out/hud-ages-$lang.gbc"
    mv -f out/hud-seasons.gbc "out/hud-seasons-$lang.gbc"
done

# Remettre oracles-hud dans l'état commité (français)
gen fr

"$PYTHON" fr/make_hud_patches.py $LANGS
