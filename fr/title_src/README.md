# Fabrication de `fr/title_combined.png`

Image de l'écran titre combiné (maquette 2 : deux bandeaux décalés, fond en
diagonale), réduite aux contraintes Game Boy Color : 4 couleurs par tuile 8×8,
8 palettes de fond.

1. `bgshot.py <rom> <nom>` : capture le titre d'une ROM US sans les sprites
   (PyBoy, son activé) → `ages_bg.png` avec la ROM Ages US, `seas_bg.png` avec Seasons US.
2. `compose4.py` : montage (logo d'Ages, bandeaux recalés sur la grille 8×8,
   fond uni autour des dessins, © descendu d'une rangée) → `title_v4.png`.
3. `fixpal.py title_v4.png title_v4f.png` : ramène à 4 couleurs les rares tuiles qui débordent.
4. `choosepal.py title_v4f.png title_combined.png` : choisit les 8 palettes qui
   abîment le moins l'image.

Ensuite `python fr/import_title.py` convertit l'image pour le jeu.
