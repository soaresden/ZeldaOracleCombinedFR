🇫🇷 [Version française](README.md)

# Zelda Oracle of Ages + Seasons "Combined" — in 5 languages

The **crossworld** hack from [oracles-disasm](https://github.com/Stewmath/oracles-disasm)
(branch `poc/crossworld1`) merges Oracle of Ages and Oracle of Seasons into a
single 8 MB ROM: items from both games usable everywhere, travel between the
two games through Vasu's shop. It only existed in English (US).

This repository translates it into **English, French, German, Italian and
Spanish** using Nintendo's official translation from the European ROMs, and
adds quality-of-life improvements you pick when generating the ROM.

> **American base.** The game is still built on the **American version**: the
> code is the one of the oracles-disasm disassembly (made from the US ROMs),
> into which the texts and images of the European ROMs are put back. The
> generated ROM therefore contains **a single language**, chosen on the page,
> with no language menu at startup like in the European versions.

## 👉 Make your ROM: [the web page](https://soaresden.github.io/ZeldaOracleCombinedFR/)

Drop your two **European** ROMs (Oracle of Ages and Oracle of Seasons,
En,Fr,De,Es,It), pick the language and the options, and the page builds the
ROM in your browser (nothing is uploaded). No ROM is distributed here.

## Always included

- **New game: AGES or SEASONS.** You pick the game you start with. The second
  game is a **linked game** (as if you had entered the other game's secret):
  the real ending (Twinrova, Ganon) is kept.
- **Second game's intro**: the first time you go to the other game, its intro
  plays normally (the original hack skipped it for Seasons). As in the original
  games, the linked game starts with the wooden sword (no shield: Impa gives it
  in Ages, it's bought in Seasons).
- **Shared inventory** (the crossworld hack's principle): at each change of
  game, Link keeps everything he has (items, hearts, rupees, seeds, rings,
  levels, key items). What you get in one game is there in the other.
- **Fixes for the original hack**: letting the intro play to the end crashed
  the game ("Game Boy Color only" screen); used key items (drunk potion, Tuni
  nut, ores, Book of Seals, Ricky's gloves…) came back after two changes of
  game; a level item (feather, boomerang…) whose level was 0 showed up as another
  item (the feather as a slingshot): it is shown at level 1 and its level is
  repaired.

You change games through Vasu's shop: the left door leads to Ages, the right
one to Seasons (in each game, one of them leads back to town).

## Options (page checkboxes)

| Option | Effect |
| --- | --- |
| Combined title screen | Logo, AGES and SEASONS banners on a diagonal over an orange / blue background. Otherwise, the Ages title. |
| Map shortcut to Vasu | On the map (Select), A on Vasu's square offers to warp to his shop. |
| Icons above Vasu's doors | Hourglass above the door to Ages, sun above the door to Seasons. |
| Game icon in the status bar | Hourglass in Ages, sun in Seasons, next to the rupees. |
| Linked game warning | The first time you leave for the other game before finishing the current adventure, the game asks for confirmation. |
| Automatic secrets | No more copying secrets: when a character asks for the secret given in the other adventure, it is passed on automatically (Farore too). |
| Rewards on the map | Once the first adventure is finished, a circle blinks on the map where a character waits to give an item. In the linked game: Farore, when a return secret is ready. |
| Secrets tracker | Start menu, 3rd page: A on the hourglass (Ages) or the seasons emblem (Seasons). Lists the 10 exchanges between the games: no secret yet, reward to collect, see Farore, complete. In adventure 1, available once it is finished. |
| Advance shop | Opens the shop reserved for the Game Boy Advance (Lynna in the past, Horon in Seasons), without brightening the colors like the real GBA mode. Idea taken from the [Force GBA Enhanced Mode](https://www.romhacking.net/hacks/3580/) patch. |
| Status bar at the bottom | Like Link's Awakening (top by default): the bar is at the bottom wherever it shows (game, Start menu, ring appraisal, time travel ripples) and the rest moves up. |

Options are ROM bytes (table at `$3FF0`, signature `ZOCFROPT` at `$3FE0`, see
`fr/options.json`): the page writes them according to the checkboxes, the game
reads them. One ROM, one patch per language.

## How it's made

| What | How |
| --- | --- |
| Text (≈ 4,100) | `fr/make_fr_text.py --lang=xx` dumps the chosen language from the EU ROMs (actual order: EN FR DE IT ES, see `fr/lang.py`). The ~60 texts added by the hack are copies of texts from the other game. Project-specific texts: `fr/extra_text.yaml`, in 5 languages. |
| Images containing words | `fr/import_fr_gfx.py --lang=xx`: menus, file select, save, Game Over, secrets, dungeon title cards, "To be continued" (5-language headers of the EU ROMs). |
| Secret list | `fr/make_secret_names.py --lang=xx`: names in Farore's list (translated in the EU ROMs) and the secrets tracker texts. |
| AGES / SEASONS menu | `fr/patch_newgame_menu.py`: menu letters drawn on the buttons, for all 5 languages. |
| Font | `fr/import_fr_font.py`: European font (extra accented glyphs). |
| Title, icons | `fr/import_title.py` (`fr/title_combined.png`, see `fr/title_src/`), `fr/make_hud_icons.py`. |
| Code | Branch [`fr/crossworld1`](https://github.com/soaresden/oracles-disasm/tree/fr/crossworld1) of the fork: 3rd text base (the translations don't fit in the US text addressing), options, menus, icons, warning, automatic secrets, markers, secrets tracker (Farore's list moved out of bank 2), fixes. |
| Tests | `fr/test_items.py` (PyBoy): in both games, every item given the way the game does, with a level of 0, then after a round trip between the games; checks the inventory and the menu display. |
| Release | `fr/make_release.py`: 160×144 screenshots and zip (patches, readme, ROM joining scripts); romhacking.net form in `romhacking/SUBMISSION.md` (French). |
| Patches | `fr/bps.py`, `fr/make_patches.py`: one BPS patch per language, from "Ages EU ROM + Seasons EU ROM" to the final ROM (`docs/patches/`). |

## Building it yourself (Windows)

Requirements: [MSYS2](https://www.msys2.org/) in `C:\msys64` (with `cmake`,
`make`, `mingw-w64-x86_64-gcc`), Python 3 with `pip install pyyaml pillow`, and
at the root the two European ROMs + `Legend of Zelda, The - Oracle of Ages (USA).gbc`
(for the font). From Git Bash:

```bash
./setup.sh
```

```bash
./build.sh
```

The (French) ROM goes to `out/combined.gbc` (or `OUT_NAME=...`). To build all
5 languages and remake the page's patches:

```bash
./build_all.sh
```

For a single language (here German), regenerate then build:
`python fr/make_fr_text.py --lang=de && python fr/import_fr_gfx.py --lang=de && python fr/patch_newgame_menu.py`, then `./build.sh`.

## Credits

- [oracles-disasm](https://github.com/Stewmath/oracles-disasm) and its crossworld hack (Stewmath and contributors).
- Nintendo's official translations, taken from the European ROMs.
- [zoragen-wpf](https://github.com/kabili207/zoragen-wpf) (kabili207): list of the secret exchanges between the games.
- [Force GBA Enhanced Mode](https://www.romhacking.net/hacks/3580/) patch: idea for the Advance shop option.

## Status

- Tested in an emulator: full intro, title, new game in both orders, travel
  between games, shortcut, icons, warning, automatic secrets, reward markers,
  secrets tracker, bottom status bar.
- The crossworld hack itself is still a proof of concept (see
  `oracles-disasm/crossworld_todo.md`): a few known graphical bugs.
- Status bar at the bottom: tested outdoors, indoors, with text boxes, during
  screen scrolling, in the Start menu, the ring appraisal and a wave effect, in
  both games.
