🇫🇷 [Version française](README.md)

# Zelda Oracle of Ages + Seasons "Combined" — French version

The **crossworld** hack from [oracles-disasm](https://github.com/Stewmath/oracles-disasm)
(branch `poc/crossworld1`) merges Oracle of Ages and Oracle of Seasons into a
single 8 MB ROM (internal title "ZELDA CROSS"): items from both games usable
everywhere, travel between the two games. It only exists in English, because
the disassembly can only build US versions.

This repository turns it into a **French version**, reusing Nintendo's official
translation straight from the European ROMs (En, Fr, De, Es, It):

| What | How |
| --- | --- |
| Text (≈ 4,100 entries) | `fr/make_fr_text.py` dumps French (language 1) from the EU ROMs; text IDs match the US ones. The ~60 texts added by the hack are copies of texts from the other game, so their French version already exists. |
| Images containing words | `fr/import_fr_gfx.py`: menus, file select, save, Game Over, secrets, dungeon title cards, "To be continued". In the EU ROMs these images have a 5-language header; the French one is used. |
| Font | `fr/import_fr_font.py`: European font (a few extra accented glyphs). |
| Code | Branch [`fr/crossworld1`](https://github.com/soaresden/oracles-disasm/tree/fr/crossworld1) of the fork: the French text doesn't fit in the US text addressing (2 × 64 KB); a 3rd base is added, as in the European version. |

No ROM is included: bring your own dumps.

## Gameplay additions

- **New game: AGES or SEASONS.** The "new game" menu lets you pick which game
  to start with. The second game is a **linked game** (as if you had entered
  the other game's secret): the real ending (Twinrova, Ganon) is kept.
- **Second game's intro**: the first time you go to the other game (door of
  Vasu's shop), its intro plays normally (the original hack skipped it for
  Seasons).
- **Shortcut to Vasu**: on the map (Select), pressing A on Vasu's shop square
  asks "Aller chez Vasu? Oui / Non" and warps you there. Available once that
  map square has been visited.

- **Combined title screen**: logo, AGES and SEASONS banners on a diagonal,
  over a half orange (Ages) / half blue (Seasons) background; "PRESS / START"
  below AGES. Source: `fr/title_combined.png` (see `fr/title_src/`).

- **Fix for the original hack**: letting the intro play to the end crashed
  the game ("Game Boy Color only" screen).
- The linked game gets the wooden sword and shield when its intro starts,
  as in the original games.

You still change games through the door of Vasu's shop: left one in Seasons,
middle-right one in Ages.

## Required files (at the root)

- `Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc`
- `Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc`
- `Legend of Zelda, The - Oracle of Ages (USA).gbc` (for the font)

## Building (Windows)

Requirements: [MSYS2](https://www.msys2.org/) in `C:\msys64` (with `cmake`,
`make`, `mingw-w64-x86_64-gcc`), Python 3 with `pip install pyyaml pillow`.
From Git Bash:

```bash
./setup.sh
```

```bash
./build.sh
```

`setup.sh` fetches the already translated disassembly (fork, branch
`fr/crossworld1`). To regenerate the French version from the EU ROMs before
building:

```bash
python fr/make_fr_text.py && python fr/import_fr_gfx.py && python fr/patch_newgame_menu.py && python fr/import_fr_font.py && python fr/import_title.py
```

The ROM goes to `out/combined.gbc` (or the name given with `OUT_NAME=...`).
The first build takes about ten minutes.

## Status

- Builds, with French text and images and the EU font.
- Not yet play-tested end to end: check it in an emulator (mGBA, BGB,
  SameBoy…).
- The crossworld hack itself is a proof of concept (see
  `oracles-disasm/crossworld_todo.md`): a few known graphical bugs.
