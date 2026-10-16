#!/bin/sh
# Joins the two European ROMs (Ages first) into the file the BPS patches apply to.
AGES="Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc"
SEASONS="Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc"
for f in "$AGES" "$SEASONS"; do
    [ -f "$f" ] || { echo "Missing: $f"; exit 1; }
done
cat "$AGES" "$SEASONS" > "Oracles (Ages+Seasons).gbc"
echo 'Created "Oracles (Ages+Seasons).gbc" - now apply the BPS patch of your language to it.'
