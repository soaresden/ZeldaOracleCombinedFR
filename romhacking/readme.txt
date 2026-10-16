Zelda Oracles Combined (Ages + Seasons) - 5 languages
=====================================================
by soaresden
https://github.com/soaresden/ZeldaOracleCombinedFR

Oracle of Ages and Oracle of Seasons in a single Game Boy Color ROM, in
English, French, German, Italian or Spanish (Nintendo's official European
translations). You choose AGES or SEASONS when starting a new game; the other
game becomes the linked game, and you travel between the two through Vasu's
shop, with a single shared inventory.

Based on the "crossworld" hack of the oracles-disasm disassembly (Stewmath and
contributors). The game code is the American one (the disassembly), with the
texts and images of the European ROMs put back: each ROM holds one language,
with no language menu at startup.


EASIEST WAY: THE WEB PAGE
-------------------------
https://soaresden.github.io/ZeldaOracleCombinedFR/
Drop your two European ROMs, pick the language and tick the options: the page
builds the ROM in your browser (nothing is uploaded).


PATCHING BY HAND (BPS)
----------------------
The patches apply to BOTH European ROMs joined end to end (Ages first):

  Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc
    2,097,152 bytes  CRC32 5933E3FA
    SHA-1 9F2DFF3C46406839F839A8D535353DFC1E3E8670
  Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc
    2,097,152 bytes  CRC32 DBAC1357
    SHA-1 360B9408E569BA826212EAC1EBEA1B09573CB48C

1. Put both ROMs next to join_roms.bat (Windows) or join_roms.sh (Linux/Mac)
   and run it. It creates "Oracles (Ages+Seasons).gbc":
     4,194,304 bytes  CRC32 E7CCFA2F
     SHA-1 B353C8B7EE2A597B4DAC207B02DCABC6BFB8C7C6
   (by hand: copy /b Ages.gbc + Seasons.gbc joined.gbc, or cat Ages.gbc
   Seasons.gbc > joined.gbc)
2. Apply the BPS patch of your language to that file (Floating IPS, beat, or
   any BPS patcher). The result is an 8 MB .gbc ROM.

A ROM made from the BPS files has the default options (see below). To change
them, use the web page.


ALWAYS INCLUDED
---------------
- New game: AGES or SEASONS; the second game is a linked game (real ending).
- The second game's intro plays normally; the linked game starts with the
  wooden sword, as in the original games.
- Shared inventory: Link keeps everything when changing games.
- Fixes to the original crossworld hack: crash at the end of the intro, used
  key items coming back after two changes of game.


OPTIONS (web page checkboxes, default in brackets)
--------------------------------------------------
- Combined Ages + Seasons title screen [on]
- Map shortcut to Vasu: A on Vasu's square warps to his shop [on]
- Icons above Vasu's doors: hourglass = Ages, sun = Seasons [on]
- Current game icon in the status bar [on]
- Warning before entering the linked game too early [on]
- Automatic secrets between the games: no more copying secrets [on]
- Rewards to collect marked on the map [on]
- Secrets tracker in the Start menu (3rd page, A on the hourglass / season
  emblem) [on]
- Advance shop (GBA bonus) without the GBA's brightened colors [off]
- Status bar at the bottom of the screen, like Link's Awakening [off]


KNOWN ISSUES
------------
The crossworld hack itself is a proof of concept: a few graphical glitches are
known (see crossworld_todo.md in the disassembly).


CREDITS
-------
- oracles-disasm and its crossworld hack: Stewmath and contributors
  https://github.com/Stewmath/oracles-disasm
- Translations: Nintendo (European ROMs)
- Secret exchanges reference: zoragen-wpf by kabili207
  https://github.com/kabili207/zoragen-wpf
- Advance shop option: idea from the "Force GBA Enhanced Mode" patch
  https://www.romhacking.net/hacks/3580/
- Combined version in 5 languages, options and fixes: soaresden


-------------------------------------------------------------------------------
FRANCAIS
-------------------------------------------------------------------------------
Oracle of Ages et Oracle of Seasons dans une seule ROM Game Boy Color, en
anglais, francais, allemand, italien ou espagnol (traductions officielles
europeennes). Le plus simple : la page web ci-dessus (options a cocher).

A la main : coller les deux ROMs europeennes (Ages puis Seasons) avec
join_roms.bat / join_roms.sh, puis appliquer le patch BPS de sa langue.
Le jeu est construit sur la version americaine (desassemblage oracles-disasm)
avec les textes et images europeens : une seule langue par ROM.
