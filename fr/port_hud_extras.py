"""Porte les cœurs sur la carte et le suivi 100 % (menu Complétion) dans les jeux
séparés (dossier oracles-hud, branche hack/hud-bottom), comme dans le combined.

- Banque $38 (vide dans les deux jeux d'origine) : image du cœur, cœurs sur la
  carte (code/hudMapHearts.s), moteur de la liste de Farore et menu Complétion
  (copies de code/crossworldSecretList.s et code/crossworldCompletion.s du
  combined, assemblées avec FR_COMP_NO_SECRETS : pas de suivi des codes), noms
  et données générés (make_secret_names.py, make_completion.py).
- Banque 2 : liste de Farore -> banque $38, A sur les quarts de cœur (inventaire,
  3e page) -> menu Complétion, carte -> cœurs.
- Les fichiers partagés sont recopiés depuis oracles-disasm par build_hud_all.sh.

Usage : python fr/port_hud_extras.py   (une seule fois ; refuse si déjà fait)
"""
import io
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROSS = os.path.join(ROOT, 'oracles-disasm')
HUD = os.path.join(ROOT, 'oracles-hud')
SHARED = ['code/crossworldSecretList.s', 'code/crossworldCompletion.s', 'gfx/common/gfx_fr_map_heart.bin']


def read(base, p):
    return io.open(os.path.join(base, p), encoding='utf-8').read()


def write(p, s):
    io.open(os.path.join(HUD, p), 'w', encoding='utf-8', newline='\n').write(s)


def rep(s, a, b, what):
    assert s.count(a) == 1, 'introuvable ou en double : ' + what
    return s.replace(a, b)


def copy_shared():
    for p in SHARED:
        shutil.copyfile(os.path.join(CROSS, p), os.path.join(HUD, p))


def map_hearts_code():
    src = read(CROSS, 'code/crossworldMapMarkers.s')
    sprite = src[src.rindex(';;', 0, src.index('\nfrDrawMapSprite:')):src.index('; Square of the character')]
    hearts = src[src.rindex(';;', 0, src.index('\nfrDrawMapHearts:')):]
    return ('; FR: blinking hearts on the overworld map (OPT_MAP_HEARTS), from\n'
            '; code/crossworldMapMarkers.s of the combined Ages + Seasons.\n\n'
            + hearts.rstrip() + '\n\n' + sprite.rstrip() + '\n')


def main():
    bank2 = read(HUD, 'code/bank2.s')
    assert 'frRunSecretListMenu' not in bank2, 'déjà porté'
    copy_shared()
    write('code/hudMapHearts.s', map_hearts_code())

    # Constantes
    c = read(HUD, 'constants/hudOptions.s')
    c += ("\n; wSubmenuState value marking Farore's secret list (menu $0a) as the completion\n"
          "; menu opened from the heart pieces (openMenu clears it otherwise)\n"
          ".define FR_COMPLETION_MARK\t\t$fe\n"
          "; Completion menu without the secret exchanges between the games\n"
          ".define FR_COMP_NO_SECRETS\n")
    write('constants/hudOptions.s', c)

    # WRAM (mêmes adresses que dans le combined)
    wram = read(HUD, 'include/wram.s')
    wram = rep(wram, "\n; $c582-$c5af unused?\n", """
; FR: completion menu (OPT_COMPLETION, code/crossworldCompletion.s)
wFrCompPage: ; $c582
; In a list of missing things: index of the first one shown
	db
wFrCompRowEntries: ; $c583
; In a list of missing things: entry shown on each row ($ff = none)
	dsb 11
wFrCompTrade: ; $c58e
; Trading sequence steps done (bit i = item i obtained, bit 12 = noble sword)
	dsb 2
wFrCompSecrets: ; $c590
; (unused in the separate games)
	dsb 2
wFrCompRowBuffer: ; $c592
; Characters of the row being built
	dsb 16
wFrCompDone: ; $c5a2
; Total of things done (completion percentage)
	db

; $c5a3-$c5af unused?
""", 'wram')
    write('include/wram.s', wram)

    # En-têtes graphiques de la carte : le cœur après les icônes
    for game in ('ages', 'seasons'):
        p = 'data/%s/gfxHeaders.s' % game
        s = read(HUD, p)
        n = 0
        out = []
        for line in s.split('\n'):
            out.append(line)
            if re.match(r'\s*m_GfxHeader\s+gfx_minimap_tiles_dungeon\s+\$8800\s', line) and n < 2:
                out.append('\tm_GfxHeader gfx_fr_map_heart $86c0 $01|$80 ; FR: map heart (heart pieces)')
                n += 1
        assert n == 2, p
        write(p, '\n'.join(out))

    # Banque $38
    for game in ('ages', 'seasons'):
        s = read(HUD, game + '.s')
        s = rep(s, "\n\n.BANK $40 SLOT 1", """

.BANK $38 SLOT 1
.ORG 0

.SECTION "FR_HudExtras"
	m_GfxDataSimple gfx_fr_map_heart
	.include "code/hudMapHearts.s"
	.include "code/crossworldSecretList.s"
	.include "code/crossworldSecretNames.s"
	.include "code/crossworldCompletion.s"
	.include "code/crossworldCompletionData.s"
.ENDS

.BANK $40 SLOT 1""", game + '.s')
        write(game + '.s', s)

    # Banque 2
    bank2 = rep(bank2, """	ld a,(wInventory.submenu2CursorPos2)
	cp $02
	jr nz,+

	; Save button selected
	inc a""", """	ld a,(wInventory.submenu2CursorPos2)
	cp $02
	jr z,@saveButton

	; FR: A on the heart pieces opens Farore's secret list as the completion
	; menu (OPT_COMPLETION, code/crossworldCompletion.s)
	dec a
	jr nz,+
	ld a,(OPT_COMPLETION)
	or a
	jr z,+
	ld a,FR_COMPLETION_MARK
	ld (wSubmenuState),a
	ld a,$0a-1

@saveButton:
	; Save button selected
	inc a""", 'inventaire, 3e page')
    bank2 = rep(bank2, """_runSecretListMenu:
	call clearOam""", """_runSecretListMenu:
	; FR: moved to bank $38 with the completion menu (code/crossworldSecretList.s)
	jpab frRunSecretListMenu
	call clearOam""", '_runSecretListMenu')
    bank2 = rep(bank2, """	ld a,(wMapMenu.drawWarpDestinations)
	or a
	jp nz,_mapMenu_drawWarpSites
""", """	ld a,(wMapMenu.drawWarpDestinations)
	or a
	jp nz,_mapMenu_drawWarpSites

	; FR: heart pieces still waiting (code/hudMapHearts.s)
	callab frDrawMapHearts
""", 'carte')
    write('code/bank2.s', bank2)
    print('cœurs sur la carte et menu Complétion portés (banque $38)')


if __name__ == '__main__':
    main()
