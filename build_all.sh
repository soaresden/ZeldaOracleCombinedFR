#!/bin/bash
# Compile la ROM dans les 5 langues des ROMs Europe, puis fabrique les patchs
# BPS de la page web (docs/). Le désassemblage est remis en français à la fin.
#   ./build_all.sh            -> toutes les langues
#   ./build_all.sh fr de      -> seulement celles-ci
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-$(command -v python)}"
export PYTHONIOENCODING=utf-8
LANGS="${*:-en fr de it es}"

gen() {  # régénère textes et images d'une langue
    "$PYTHON" fr/make_fr_text.py --lang="$1" >/dev/null
    "$PYTHON" fr/import_fr_gfx.py --lang="$1" >/dev/null
    "$PYTHON" fr/patch_newgame_menu.py >/dev/null
    "$PYTHON" fr/make_secret_names.py --lang="$1" >/dev/null
}

for lang in $LANGS; do
    echo "===== langue $lang ====="
    gen "$lang"
    OUT_NAME="zoc-$lang.gbc" bash build.sh > "out/build_$lang.log" 2>&1 || { tail -20 "out/build_$lang.log"; exit 1; }
done

# Remettre le désassemblage dans l'état commité (français)
gen fr

"$PYTHON" fr/make_patches.py $LANGS
"$PYTHON" fr/make_previews.py $LANGS
