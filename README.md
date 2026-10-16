🇬🇧 [English version](README.en.md)

# Zelda Oracle of Ages + Seasons « Combined » — en 5 langues

Le hack **crossworld** de [oracles-disasm](https://github.com/Stewmath/oracles-disasm)
(branche `poc/crossworld1`) réunit Oracle of Ages et Oracle of Seasons dans une
seule ROM de 8 Mo : objets des deux jeux utilisables partout, passage d'un jeu
à l'autre par la boutique de Vasu. Il n'existait qu'en anglais (US).

Ce dépôt le traduit en **anglais, français, allemand, italien et espagnol** en
reprenant la traduction officielle de Nintendo dans les ROMs européennes, et
ajoute des améliorations de confort qu'on choisit à la génération.

> **Base américaine.** Le jeu reste construit sur la **version américaine** : le
> code est celui du désassemblage oracles-disasm (fait à partir des ROMs US),
> dans lequel on remet les textes et les images des ROMs européennes. La ROM
> générée contient donc **une seule langue**, choisie sur la page, sans menu de
> langue au démarrage comme dans les versions européennes.

## 👉 Fabriquer sa ROM : [la page web](https://soaresden.github.io/ZeldaOracleCombinedFR/)

On y dépose ses deux ROMs **Europe** (Oracle of Ages et Oracle of Seasons,
En,Fr,De,Es,It), on choisit la langue et les options, et la page fabrique la
ROM dans le navigateur (rien n'est envoyé). Aucune ROM n'est distribuée ici.

## Ce qui est toujours inclus

- **Nouvelle partie : AGES ou SEASONS.** On choisit le jeu par lequel on
  commence. Le second jeu est une **partie liée** (comme avec le code de l'autre
  jeu) : on garde la vraie fin (Twinrova, Ganon).
- **Intro du second jeu** : la première fois qu'on passe dans l'autre jeu, son
  intro se joue normalement (le hack d'origine la sautait pour Seasons). Comme
  dans les jeux d'origine, la partie liée commence avec l'épée en bois (pas de
  bouclier : Impa le donne dans Ages, il s'achète dans Seasons).
- **Inventaire commun** (principe du hack crossworld) : à chaque changement de
  jeu, Link garde tout ce qu'il a (objets, cœurs, rubis, graines, bagues,
  niveaux, objets clés). Ce qu'on obtient dans un jeu se retrouve dans l'autre.
- **Corrections du hack d'origine** : laisser l'intro aller jusqu'au bout
  faisait planter le jeu (écran « Game Boy Color only ») ; les objets clés
  utilisés (potion bue, noix Tuni, minerais, Livre des Sceaux, gants de Ricky…)
  revenaient après deux changements de jeu.

On change de jeu par la boutique de Vasu : la porte de gauche mène à Ages, celle
de droite à Seasons (dans un des deux jeux, l'une des deux ramène en ville).

## Options (cases à cocher de la page)

| Option | Effet |
| --- | --- |
| Écran titre combiné | Logo, bandeaux AGES et SEASONS en diagonale sur fond orange / bleu. Sinon, titre d'Ages. |
| Raccourci carte vers Vasu | Sur la carte (Select), A sur la case de Vasu propose d'aller dans sa boutique. |
| Icônes des portes de Vasu | Sablier au-dessus de la porte vers Ages, soleil au-dessus de celle vers Seasons. |
| Icône du jeu dans la barre | Sablier dans Ages, soleil dans Seasons, à côté des rubis. |
| Avertissement partie liée | La 1re fois qu'on part dans l'autre jeu sans avoir fini l'aventure, le jeu demande confirmation. |
| Codes automatiques | Plus besoin de recopier les codes : quand un personnage demande le code donné dans l'autre aventure, il est transmis tout seul (Farore aussi). |
| Récompenses sur la carte | Une fois la 1re aventure finie, un cercle clignote sur la carte là où un personnage attend pour donner un objet. Dans la partie liée : Farore, quand un code de retour est prêt. |
| Suivi des codes | Menu Start, 3e page : A sur le sablier (Ages) ou l'emblème des saisons (Seasons). Liste les 10 échanges entre les jeux : code pas encore reçu, récompense à récupérer, Farore à voir, terminé. Dans l'aventure 1, disponible une fois celle-ci finie. |
| Boutique Advance | Ouvre la boutique réservée à la Game Boy Advance (Lynna dans le passé, Horon dans Seasons), sans éclaircir les couleurs comme le vrai mode GBA. Idée reprise du patch [Force GBA Enhanced Mode](https://www.romhacking.net/hacks/3580/). |
| Barre d'état en bas | Comme dans Link's Awakening (en haut par défaut) : la barre est en bas partout où elle s'affiche (jeu, menu Start, évaluation des bagues, ondulations des voyages dans le temps) et le reste remonte. |

Les options sont des octets de la ROM (table à `$3FF0`, signature
`ZOCFROPT` à `$3FE0`, voir `fr/options.json`) : la page les écrit selon les
cases cochées, le jeu les lit. Une seule ROM, un patch par langue.

## Comment c'est fait

| Quoi | Comment |
| --- | --- |
| Textes (≈ 4 100) | `fr/make_fr_text.py --lang=xx` extrait la langue choisie des ROMs EU (ordre réel : EN FR DE IT ES, voir `fr/lang.py`). Les ~60 textes ajoutés par le hack sont des copies de textes de l'autre jeu. Textes propres au projet : `fr/extra_text.yaml`, en 5 langues. |
| Images avec du texte | `fr/import_fr_gfx.py --lang=xx` : menus, sélection de fichier, sauvegarde, Game Over, secrets, cartes-titres des donjons, « À suivre… » (en-têtes à 5 langues des ROMs EU). |
| Liste des secrets | `fr/make_secret_names.py --lang=xx` : noms de la liste de Farore (traduits dans les ROMs EU) et textes du suivi des codes. |
| Menu AGES / SEASONS | `fr/patch_newgame_menu.py` : lettres du menu posées sur les boutons, pour les 5 langues. |
| Police | `fr/import_fr_font.py` : police européenne (glyphes accentués en plus). |
| Titre, icônes | `fr/import_title.py` (`fr/title_combined.png`, voir `fr/title_src/`), `fr/make_hud_icons.py`. |
| Code | Branche [`fr/crossworld1`](https://github.com/soaresden/oracles-disasm/tree/fr/crossworld1) du fork : 3e base de texte (la VF ne tient pas dans l'adressage US), options, menus, icônes, avertissement, codes automatiques, marqueurs, suivi des codes (liste de Farore déplacée hors de la banque 2), corrections. |
| Patchs | `fr/bps.py`, `fr/make_patches.py` : patch BPS par langue, de « ROM Ages EU + ROM Seasons EU » vers la ROM finale (`docs/patches/`). |

## Compiler soi-même (Windows)

Prérequis : [MSYS2](https://www.msys2.org/) dans `C:\msys64` (avec `cmake`,
`make`, `mingw-w64-x86_64-gcc`), Python 3 avec `pip install pyyaml pillow`, et
à la racine les deux ROMs Europe + `Legend of Zelda, The - Oracle of Ages (USA).gbc`
(pour la police). Depuis Git Bash :

```bash
./setup.sh
```

```bash
./build.sh
```

La ROM (française) sort dans `out/combined.gbc` (ou `OUT_NAME=...`). Pour
compiler les 5 langues et refaire les patchs de la page :

```bash
./build_all.sh
```

Pour une seule langue (ici l'allemand), régénérer puis compiler :
`python fr/make_fr_text.py --lang=de && python fr/import_fr_gfx.py --lang=de && python fr/patch_newgame_menu.py`, puis `./build.sh`.

## Crédits

- [oracles-disasm](https://github.com/Stewmath/oracles-disasm) et son hack crossworld (Stewmath et contributeurs).
- Traductions officielles de Nintendo, reprises des ROMs européennes.
- [zoragen-wpf](https://github.com/kabili207/zoragen-wpf) (kabili207) : liste des échanges de codes entre les jeux.
- Patch [Force GBA Enhanced Mode](https://www.romhacking.net/hacks/3580/) : idée de l'option Boutique Advance.

## État

- Testé dans un émulateur : intro complète, titre, nouvelle partie dans les
  deux ordres, passage entre les jeux, raccourci, icônes, avertissement,
  codes automatiques, marqueurs de récompense, suivi des codes, barre en bas.
- Le hack crossworld lui-même reste une preuve de concept (voir
  `oracles-disasm/crossworld_todo.md`) : quelques bugs graphiques connus.
- Barre d'état en bas : testée en extérieur, en intérieur, avec les boîtes de
  texte, pendant les défilements d'écran, dans le menu Start, l'évaluation des
  bagues et un effet d'ondulation, dans les deux jeux.
