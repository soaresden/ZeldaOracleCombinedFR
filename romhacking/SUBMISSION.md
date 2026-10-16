# Soumission romhacking.net — fiche champ par champ

Formulaire : https://www.romhacking.net/hacks/addentrypage/ (Submissions → Submit Files).
Les textes à coller sont en anglais (le site est anglophone). Fichiers prêts :

- zip : `out/release/ZeldaOraclesCombined-v1.0.zip` (5 patchs BPS, `readme.txt`,
  `join_roms.bat`, `join_roms.sh`), refait par `python fr/make_release.py 1.0`
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
| Version | `1.0` |
| Release Date | la date d'envoi |
| Download Link | lien du zip (voir plus bas : release GitHub) |

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
| Image2 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/5-secrets-tracker.png` |
| Image3 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/4-vasu-doors-to-each-game.png` |
| Image4 | `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/3-status-bar-at-the-bottom.png` |

Autres captures disponibles : `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/6-reward-markers-on-the-map.png`, `https://soaresden.github.io/ZeldaOracleCombinedFR/screenshots/7-advance-shop.png`.

## Description

```
Oracle of Ages and Oracle of Seasons in a single Game Boy Color ROM, in English, French, German, Italian or Spanish (Nintendo's official European translations).

When starting a new game you pick AGES or SEASONS: the other game becomes the linked game (real ending included), and its intro plays the first time you go there. You travel between the two games through Vasu's shop, with a single shared inventory.

Based on the "crossworld" hack of the oracles-disasm disassembly (Stewmath and contributors), which only existed in English. The game code is the American one, with the texts and images of the European ROMs put back: each ROM holds one language, with no language menu at startup.

Easiest way: the web page https://soaresden.github.io/ZeldaOracleCombinedFR/ builds the ROM in your browser from your two European ROMs, with the language and the options you tick (nothing is uploaded).

Options (default in brackets):
- Combined Ages + Seasons title screen [on]
- Map shortcut to Vasu [on]
- Icons above Vasu's doors (hourglass = Ages, sun = Seasons) [on]
- Current game icon in the status bar [on]
- Warning before entering the linked game too early [on]
- Automatic secrets between the games: no more copying secrets [on]
- Rewards to collect marked on the map [on]
- Secrets tracker in the Start menu [on]
- Advance shop (GBA bonus) without the GBA's brightened colors [off]
- Status bar at the bottom of the screen, like Link's Awakening [off]

Also fixed from the original crossworld hack: crash at the end of the intro, used key items coming back after two changes of game.

The BPS patches apply to BOTH European ROMs joined end to end (Ages first): see readme.txt (join_roms.bat / join_roms.sh included). A ROM made from the patches has the default options; use the web page to change them.

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
GitHub `v1.0` du dépôt avec le zip en pièce jointe :
`https://github.com/soaresden/ZeldaOracleCombinedFR/releases/download/v1.0/ZeldaOraclesCombined-v1.0.zip`
