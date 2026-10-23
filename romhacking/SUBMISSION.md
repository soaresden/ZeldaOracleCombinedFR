# Soumission romhacking.net — fiche champ par champ

Formulaire : https://www.romhacking.net/hacks/addentrypage/ (Submissions → Submit Files).
Les textes à coller sont en anglais (le site est anglophone). Fichiers prêts :

- zip : `out/release/ZeldaOraclesCombined-v1.5.zip` (5 patchs BPS, `readme.txt`,
  `join_roms.bat`, `join_roms.sh`), refait par `python fr/make_release.py 1.5 --no-shots`
- captures 160×144 : `docs/screenshots/`, en ligne sur GitHub Pages (URLs ci-dessous,
  à coller directement : la Scratchpad n'est pas nécessaire)

## General Information

| Champ | À mettre |
| --- | --- |
| Title | `Zelda Oracles Combined (Ages + Seasons)` |
| Category | `Improvement` |
| Platform | `Game Boy` (la GBC est rangée sous Game Boy sur le site) |
| Game | `Legend of Zelda, The: Oracle of Ages` (une seule fiche jeu possible ; Seasons est cité dans la description) |
| Author | `soaresden` |
| Version | `1.5` |
| Release Date | la date d'envoi |
| Download Link | `https://github.com/soaresden/ZeldaOracleCombinedFR/releases/download/v1.5/ZeldaOraclesCombined-v1.5.zip` |

## Media

Le site n'accepte que la taille réelle (160×144 pour la Game Boy) : ne pas utiliser
les aperçus de la page (`previews/`, agrandis en 320×288). Les captures de
`docs/screenshots/` sont en ligne :
`https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/<fichier>`

| Champ | Fichier |
| --- | --- |
| YouTube Share URL | (vide) |
| Title Image | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/1-title.png` (titre combiné, différent de l'original) |
| Image1 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/2-new-game-ages-or-seasons.png` |
| Image2 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/8-100-percent-tracker.png` |
| Image3 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/4-vasu-doors-to-each-game.png` |
| Image4 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/3-status-bar-at-the-bottom.png` |

Autres captures disponibles : `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/9-heart-pieces-on-the-map.png`, `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/5-secrets-tracker.png`, `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/6-reward-markers-on-the-map.png`, `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/7-advance-shop.png`.

## Description

```
Oracle of Ages and Oracle of Seasons in a single Game Boy Color ROM, in English, French, German, Italian or Spanish (Nintendo's official European translations).

When starting a new game you pick AGES or SEASONS: the other game becomes the linked game (real ending included), and its intro plays the first time you go there. You travel between the two games through Vasu's shop, with a single shared inventory.

Based on the "crossworld" hack of the oracles-disasm disassembly (Stewmath and contributors), which only existed in English. The game code is the American one, with the texts and images of the European ROMs put back: each ROM holds one language, with no language menu at startup.

Easiest way: the web page https://soaresden.github.io/ZeldaOracleCombinedFR/ builds the ROM in your browser from your two European ROMs, with the language and the options you tick (nothing is uploaded).

The page can also keep the games separate: from one European ROM (Ages and/or Seasons), it makes the original game in the chosen language with only the options that make sense without merging (status bar at the bottom, Advance shop, heart pieces on the map, 100% tracker).

Options (default in brackets):
- Combined Ages + Seasons title screen [on]
- Map shortcut to Vasu [on]
- Icons above Vasu's doors (hourglass = Ages, sun = Seasons) [on]
- Current game icon in the status bar [on]
- Warning before entering the linked game too early [on]
- Automatic secrets between the games: no more copying secrets [on]
- Rewards to collect marked on the map [on]
- Secrets tracker in the Start menu [on]
- Heart pieces still to collect on the map [on]
- 100% tracker in the Start menu: what is missing, with its map square [on]
- Advance shop (GBA bonus) without the GBA's brightened colors [off]
- Status bar at the bottom of the screen, like Link's Awakening [off]

Also fixed from the original crossworld hack: crash at the end of the intro, used key items coming back after two changes of game, rings partly lost when changing games, seed trees in Ages drawn with status bar digits, kid's name/character and game ID not carried over, rupees and counters half copied.

The BPS patches apply to BOTH European ROMs joined end to end (Ages first): see readme.txt (join_roms.bat / join_roms.sh included). A ROM made from the patches has the default options; use the web page to change them.

Version history:
1.5 - When changing games, the kid's name and character and the game ID (what the original games' link secret carried) now come along; they are only copied when set in the game left, so a game where the kid isn't named yet doesn't erase his name. Rupees, play time and the death, enemy and rupee counters were only half copied (199 rupees became 99): fixed. Existing saves keep working.
1.4 - In Ages, the seed trees showed status bar digits instead of the tree: bug of the original crossworld hack (it loaded 16 status bar tiles too many, over the trees' graphics), fixed. Existing saves keep working.
1.3 - New options: heart pieces still to collect blink on the map; 100% tracker in the Start menu (heart pieces, heart containers, essences, rings, trading sequence, secrets, with the list of what is missing and its map square, and where to go next in the trading sequence). When changing games, all obtained rings, the whole ring box and the rings waiting to be appraised now come along (only part of them did). The game icon in the status bar and the icons above Vasu's doors could be replaced by shop graphics: fixed.
1.2 - In Ages, picking up a dungeon map didn't record it and changed the first inventory item (the shovel turned into a feather in dungeon 1): bug of the original crossworld hack, fixed. The automatic test now also checks maps, compasses and keys in all 8 dungeons of both games.
1.1 - A level item (feather, boomerang...) whose level was 0 showed up in the menu as another item (the feather as a slingshot): it is now shown at level 1 and its level is repaired. New automatic test of every item of both games (obtaining, level 0, round trip between the games).
1.0 - First release.

Sources: https://github.com/soaresden/ZeldaOracleCombinedFR
Credits: Stewmath and contributors (oracles-disasm, crossworld), Nintendo (translations), kabili207 (zoragen-wpf, secret exchanges reference), "Force GBA Enhanced Mode" patch (Advance shop idea).
```

## Scan Your ROM / ROM / ISO Information

Le scan du site ne prend qu'une ROM : on peut scanner la ROM Ages, puis remplacer
le texte par celui-ci (les deux ROMs et le fichier collé) :

```
Patches apply to both ROMs joined end to end (Ages first):

Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc
File Size: 2,097,152 bytes
CRC32: 5933E3FA
MD5: 825DE040EA4DFF66661693F8712B1BDB
SHA-1: 9F2DFF3C46406839F839A8D535353DFC1E3E8670

Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc
File Size: 2,097,152 bytes
CRC32: DBAC1357
MD5: 4CA44CBDD4E05C9B3C22DA96D3DE6338
SHA-1: 360B9408E569BA826212EAC1EBEA1B09573CB48C

Joined file (Ages + Seasons):
File Size: 4,194,304 bytes
CRC32: E7CCFA2F
SHA-1: B353C8B7EE2A597B4DAC207B02DCABC6BFB8C7C6
```

## Lien de téléchargement

Le formulaire demande un lien, pas un fichier. Le plus propre : une release
GitHub `v1.5` du dépôt avec le zip en pièce jointe :
`https://github.com/soaresden/ZeldaOracleCombinedFR/releases/download/v1.5/ZeldaOraclesCombined-v1.5.zip`
