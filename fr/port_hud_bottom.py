"""Porte la barre d'état en bas (OPT_HUD_BOTTOM du combined) dans les jeux
d'origine séparés (dossier oracles-hud, branche hack/hud-bottom, désassemblage
de 2020 avec les textes européens).

Les routines viennent de oracles-disasm/code/bank0.s (branche fr/crossworld1).
La banque 0 d'origine n'a que 264 octets libres : elle garde les points
d'accroche, le chemin rapide de l'interruption LCD (ondulation, une par ligne),
les petites routines appelées partout et deux tremplins ; le reste va en banque
$40 (libre, la ROM fait 2 Mo) et les deux routines des icônes A/B, appelées
seulement par la banque 2, vont en banque 2. La barre est toujours en bas.

Usage : python fr/port_hud_bottom.py   (une seule fois ; refuse si déjà fait)
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROSS = os.path.join(ROOT, 'oracles-disasm')
HUD = os.path.join(ROOT, 'oracles-hud')


def read(base, p):
    return io.open(os.path.join(base, p), encoding='utf-8').read()


def write(p, s):
    io.open(os.path.join(HUD, p), 'w', encoding='utf-8', newline='\n').write(s)


def rep(s, a, b, what):
    assert s.count(a) == 1, 'introuvable ou en double : ' + what
    return s.replace(a, b)


def functions():
    """Les routines de la barre du combined, par nom (avec leur commentaire)."""
    src = read(CROSS, 'code/bank0.s')
    start = src.rindex(';;', 0, src.index('\nfrHudBottomVblank:'))
    end = src.index('.ENDS', src.index('\nfrLdiYAddHudOffset:'))
    chunks = re.split(r'\n(?=;;\n)', src[start:end].strip('\n'))
    out = {}
    for c in chunks:
        name = re.search(r'^(\w+):', c, re.M).group(1)
        out[name] = c.rstrip() + '\n'
    return out


BANK0_EXTRA = """
;;
; FR: status bar at the bottom of the screen, like Link's Awakening (ported from
; ZeldaOracleCombinedFR). Most of it is in bank $40 (code/hudBottom40.s); bank 0
; keeps the hooks, the wave effect (one interrupt per line) and small helpers.
.define FRHUD_PHASE_GAME		1
.define FRHUD_PHASE_LCDC_A7		2
.define FRHUD_PHASE_RING_TEXT		3
.define FRHUD_PHASE_RING_END		4
.define FRHUD_PHASE_WAVE		5
.define FRHUD_PHASE_STATUS		6

;;
; Called by vblankInterrupt (keeps hl and bc).
frHudBottomVblank:
	ld a,:frHudBottomVblank_body
	ld ($2222),a
	call frHudBottomVblank_body

;;
; Back to the bank in use, like the end of vblankInterrupt.
frHudRestoreBank:
	push hl
	ld hl,hFFB7
	ldh a,(<hRomBank)
	bit 0,(hl)
	jr z,+
	ldh a,(<hSoundDataBaseBank2)
+
	ld ($2222),a
	pop hl
	ret

;;
; LCD interrupt with the status bar at the bottom (see frHudBottomVblank_body).
frHudBottomLcd:
	push bc
	ld a,($ff00+R_LY)
	inc a
	ld b,a
	ld a,(wFrHudPhase)
	cp FRHUD_PHASE_WAVE
	jr nz,@wait

	; Wave effect: SCX for line b-1 (which was line b+$0f), then the next line
	ld a,b
	cp $7f
	ld a,FRHUD_PHASE_WAVE
	jr nc,@far
	ld a,b
	add $0f
	ld l,a
	ld h,>wBigBuffer
	ld a,(hl)
	ld ($ff00+R_SCX),a
	ld a,b
	ld ($ff00+R_LYC),a
	jp _lcdInterruptEnd

@wait:
	; Wait for hblank, like lcdInterrupt
	ld c,a
-
	ld a,($ff00+R_STAT)
	and $03
	jr nz,-
	ld a,c
@far:
	ld c,a
	ld a,:frHudRunPhase
	ld ($2222),a
	ld a,c
	call frHudRunPhase
	call frHudRestoreBank
	jp _lcdInterruptEnd

"""


def main():
    f = functions()
    for n in ('frHudBottomVblank', 'frHudWriteShiftedRegs', 'frHudAfterGameRegs', 'frHudSchedule',
              'frHudScheduleStatus', 'frHudBottomLcd', 'frHudRunPhase', 'frHudWaveLine',
              'frMoveStatusBarItemsDown', 'frMenuSpriteYOffset', 'frGetStatusBarItemsY',
              'frFixStatusBarItemsY', 'frGetSpriteCameraY', 'frLdiYAddHudOffset'):
        assert n in f, n

    bank0 = read(HUD, 'code/bank0.s')
    assert 'frHudBottomVblank' not in bank0, 'déjà porté'
    hooks = [
        ("\tld ($ff00+R_LYC),a\n\n\t; increment wVBlankChecker",
         "\tld ($ff00+R_LYC),a\n\tcall frHudBottomVblank\n\n\t; increment wVBlankChecker", 'vblankInterrupt'),
        ("lcdInterrupt:\n\tldh a,(<hLcdInterruptBehaviour)",
         "lcdInterrupt:\n\tld a,(wFrHudBottom)\n\tor a\n\tjp nz,frHudBottomLcd\n\tldh a,(<hLcdInterruptBehaviour)",
         'lcdInterrupt'),
        ("addSpritesToOam_withOffset:\n\tldh a,(<hOamTail)",
         "addSpritesToOam_withOffset:\n\tcall frMenuSpriteYOffset\n\tldh a,(<hOamTail)", 'addSpritesToOam_withOffset'),
        ("_getObjectPositionOnScreen:\n\tldh a,(<hCameraX)\n\tld c,a\n\tldh a,(<hCameraY)\n\tld b,a",
         "_getObjectPositionOnScreen:\n\tldh a,(<hCameraX)\n\tld c,a\n\tcall frGetSpriteCameraY",
         '_getObjectPositionOnScreen'),
        ("_label_00_152:\n\tldh a,(<hCameraX)\n\tld c,a\n\tldh a,(<hCameraY)\n\tld b,a",
         "_label_00_152:\n\tldh a,(<hCameraX)\n\tld c,a\n\tcall frGetSpriteCameraY", '_label_00_152'),
        ("\t; Read Object.yh\n\tld d,$00\n\tldi a,(hl)\n\tadd $10",
         "\t; Read Object.yh\n\tld d,$00\n\tcall frLdiYAddHudOffset", 'duringScreenTransition'),
    ]
    for a, b, what in hooks:
        bank0 = rep(bank0, a, b, what)
    extra = BANK0_EXTRA + f['frMenuSpriteYOffset'] + '\n' + f['frGetSpriteCameraY'] + '\n' + f['frLdiYAddHudOffset']
    i = bank0.rindex('.ENDS')
    bank0 = bank0[:i] + extra + '\n' + bank0[i:]
    write('code/bank0.s', bank0)

    # Banque $40 : le reste
    vblank = f['frHudBottomVblank'].replace('\nfrHudBottomVblank:', '\nfrHudBottomVblank_body:', 1)
    vblank = rep(vblank, 'ld a,(OPT_HUD_BOTTOM)', 'ld a,(frHudBottomEnabled)', 'option')
    bank40 = ('; FR: status bar at the bottom of the screen (ported from ZeldaOracleCombinedFR,\n'
              '; see frHudBottomVblank in bank 0). Always on.\n\n'
              'frHudBottomEnabled:\n\t.db $01\n\n' + vblank)
    for n in ('frHudWriteShiftedRegs', 'frHudAfterGameRegs', 'frHudSchedule', 'frHudScheduleStatus',
              'frHudRunPhase', 'frHudWaveLine', 'frMoveStatusBarItemsDown'):
        bank40 += '\n' + f[n]
    write('code/hudBottom40.s', bank40)
    for game in ('ages', 'seasons'):
        s = read(HUD, game + '.s')
        s = rep(s, "\n\n; Text moved to bank $43", """

.BANK $40 SLOT 1
.ORG 0

.SECTION "FR_HudBottom"
	.include "code/hudBottom40.s"
.ENDS

; Text moved to bank $43""", game + '.s')
        write(game + '.s', s)

    # Banque 2 : icônes A/B
    bank2 = read(HUD, 'code/bank2.s')
    bank2 = rep(bank2, "\tld e,$10\n\tld bc,$1038",
                "\tld e,$10\n\tld c,$38\n\tcall frGetStatusBarItemsY ; FR: $10, or $90 with the status bar at the bottom",
                '_updateStatusBar (Y des objets)')
    bank2 = rep(bank2, "\tld b,$10\n\tjp copyMemoryReverse\n\n@oamData:",
                "\tld b,$10\n\tcall copyMemoryReverse\n\tjp frFixStatusBarItemsY\n\n@oamData:",
                '_updateStatusBar (épée de Biggoron)')
    # Avant le bloc propre à Ages de la fin du fichier (sinon Seasons ne les a pas)
    i = bank2.rindex('\n.ifdef ROM_AGES\n')
    bank2 = bank2[:i] + '\n\n' + f['frGetStatusBarItemsY'] + '\n' + f['frFixStatusBarItemsY'] + bank2[i:]
    write('code/bank2.s', bank2)

    wram = read(HUD, 'include/wram.s')
    wram = rep(wram, "\tdsb $40\n\n; $c540-$c5af unused?\n", """	dsb $40
wObjectsToDrawEnd: ; $c540
; FR: the priority lists actually go up to $c57f (see objectQueueDraw)
	dsb $40

wFrHudBottom: ; $c580
; FR: 1 while the status bar is drawn at the bottom of the screen this frame
; (see frHudBottomVblank): 1 in gameplay, 2 in a menu
	db

wFrHudPhase: ; $c581
; FR: next LCD interrupt event with the status bar at the bottom (FRHUD_PHASE_*)
	db

; $c582-$c5af unused?
""", 'wram')
    write('include/wram.s', wram)
    print('barre du bas portée (banque 0, $40, 2)')


if __name__ == '__main__':
    main()
