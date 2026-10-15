🇬🇧 [English version](README.en.md)

# Zelda Oracle of Ages + Seasons « Combined » — version française

Le hack **crossworld** de [oracles-disasm](https://github.com/Stewmath/oracles-disasm)
(branche `poc/crossworld1`) réunit Oracle of Ages et Oracle of Seasons dans une
seule ROM de 8 Mo (titre interne « ZELDA CROSS ») : objets des deux jeux
utilisables partout, passage d'un jeu à l'autre. Il n'existe qu'en anglais,
car le désassemblage ne sait construire que les versions US.

Ce dépôt en fait une **VF**, en reprenant la traduction officielle de Nintendo
directement dans les ROMs européennes (En, Fr, De, Es, It) :

| Quoi | Comment |
| --- | --- |
| Textes (≈ 4 100) | `fr/make_fr_text.py` extrait le français (langue 1) des ROMs EU ; les identifiants de texte sont les mêmes qu'en US. Les ~60 textes ajoutés par le hack sont des copies de textes de l'autre jeu : leur VF existe déjà. |
| Images avec du texte | `fr/import_fr_gfx.py` : menus, sélection de fichier, sauvegarde, Game Over, secrets, cartes-titres des donjons, « À suivre… ». Dans les ROMs EU ces images ont un en-tête à 5 langues ; on prend la française. |
| Police | `fr/import_fr_font.py` : police européenne (quelques glyphes accentués en plus). |
| Code | Branche [`fr/crossworld1`](https://github.com/soaresden/oracles-disasm/tree/fr/crossworld1) du fork : la VF ne tient pas dans les 2 × 64 Ko d'adressage du texte US ; ajout d'une 3e base, comme dans la version européenne. |

Aucune ROM n'est incluse : il faut ses propres dumps.

## Ajouts de jouabilité

- **Nouvelle partie : AGES ou SEASONS.** Le menu « Nouveau jeu » propose de
  choisir le jeu par lequel on commence. Le second jeu est une **partie liée**
  (comme avec le code de l'autre jeu) : on garde la vraie fin (Twinrova, Ganon).
- **Intro du second jeu** : la première fois qu'on passe dans l'autre jeu (porte
  de la boutique de Vasu), son intro se joue normalement (le hack d'origine la
  sautait pour Seasons).
- **Raccourci vers Vasu** : sur la carte (Select), appuyer sur A sur la case de
  la boutique de Vasu propose « Aller chez Vasu? Oui / Non » et y téléporte.
  Disponible dès que cette case de la carte a été visitée.

Le jeu se change toujours par la porte de la boutique de Vasu : à gauche dans
Seasons, au milieu-droite dans Ages.

## Fichiers nécessaires (à la racine)

- `Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc`
- `Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc`
- `Legend of Zelda, The - Oracle of Ages (USA).gbc` (pour la police)

## Compiler (Windows)

Prérequis : [MSYS2](https://www.msys2.org/) dans `C:\msys64` (avec `cmake`,
`make`, `mingw-w64-x86_64-gcc`), Python 3 avec `pip install pyyaml pillow`.
Depuis Git Bash :

```bash
./setup.sh
```

```bash
./build.sh
```

`setup.sh` récupère le désassemblage déjà traduit (fork, branche
`fr/crossworld1`). Pour régénérer la VF depuis les ROMs EU avant de compiler :

```bash
python fr/make_fr_text.py && python fr/import_fr_gfx.py && python fr/patch_newgame_menu.py && python fr/import_fr_font.py
```

La ROM sort dans `out/combined.gbc` (ou le nom donné par `OUT_NAME=...`).
La première compilation prend une dizaine de minutes.

## État

- Compile, texte et images FR intégrés, police EU.
- Pas encore testé en jeu de bout en bout : à vérifier dans un émulateur
  (mGBA, BGB, SameBoy…).
- Le hack crossworld lui-même est une preuve de concept (voir
  `oracles-disasm/crossworld_todo.md`) : quelques bugs graphiques connus.
