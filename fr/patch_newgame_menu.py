"""Menu « nouvelle partie » : remplace NOUVEAU JEU / SECRETS par AGES / SEASONS
(on choisit par quel jeu commencer). Les lettres sont découpées dans les mots
déjà présents dans l'image (même police), puis posées sur le bois du bouton.

À lancer après import_fr_gfx.py (il part de l'image française).

Usage : python fr/patch_newgame_menu.py [aperçu.png]
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
sys.path.insert(0, os.path.join(DISASM, 'tools'))
from common import decompressGfxData  # noqa: E402

CMP = os.path.join(DISASM, 'precompressed', 'gfx_compressible', 'common', 'gfx_newfilescreen.cmp')
SIZE = 0x67
BLACK = 3
# Boutons : (première colonne, nombre de colonnes) dans la bande de tuiles 8x16.
# La 1re colonne de chaque bouton est le séparateur « | ».
BUTTONS = {'NOUVEAU JEU': (16, 12), 'SECRETS': (28, 12), 'GAME LINK': (40, 12)}
TEXT_ROWS = range(4, 15)  # lignes des lettres (0-2 : bordure, 3 et 15 : bois)
NEW_LABELS = {'NOUVEAU JEU': 'AGES', 'SECRETS': 'SEASONS'}


def to_pixels(data):
    """Bande de colonnes 8x16 -> pixels[y][x] (valeurs 0-3)."""
    cols = len(data) // 32
    px = [[0] * (cols * 8) for _ in range(16)]
    for c in range(cols):
        for half in range(2):
            t = c * 2 + half
            for y in range(8):
                lo, hi = data[t * 16 + y * 2], data[t * 16 + y * 2 + 1]
                for x in range(8):
                    px[half * 8 + y][c * 8 + x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
    return px


def to_data(px):
    cols = len(px[0]) // 8
    out = bytearray(cols * 32)
    for c in range(cols):
        for half in range(2):
            t = c * 2 + half
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = px[half * 8 + y][c * 8 + x]
                    lo |= (v & 1) << (7 - x)
                    hi |= (v >> 1) << (7 - x)
                out[t * 16 + y * 2], out[t * 16 + y * 2 + 1] = lo, hi
    return out


def letters(px, word, button):
    """Découpe les lettres noires d'un bouton : {lettre: [colonnes de pixels]}."""
    first, ncols = BUTTONS[button]
    x0, x1 = (first + 1) * 8, (first + ncols) * 8
    # colonne de lettre : du noir dans les lignes du texte, mais pas en 3 ni en
    # 15 (sinon c'est le séparateur « | » entre deux boutons)
    black = [any(px[y][x] == BLACK for y in TEXT_ROWS)
             and px[3][x] != BLACK and px[15][x] != BLACK for x in range(x0, x1)]
    runs, start = [], None
    for i, b in enumerate(black + [False]):
        if b and start is None:
            start = i
        elif not b and start is not None:
            runs.append((x0 + start, x0 + i))
            start = None
    chars = [ch for ch in word if ch != ' ']
    assert len(runs) == len(chars), (button, len(runs), chars)
    return {ch: [[px[y][x] == BLACK for y in range(16)] for x in range(a, b)]
            for ch, (a, b) in zip(chars, runs)}


def wood(px, button):
    """Fond du bouton sans texte : on remplace le noir par le bois de la ligne voisine."""
    first, ncols = BUTTONS[button]
    x0, x1 = (first + 1) * 8, (first + ncols) * 8
    out = [row[x0:x1] for row in px]
    for x in range(x1 - x0):
        if px[3][x0 + x] == BLACK:
            continue  # séparateur
        for y in TEXT_ROWS:
            if out[y][x] == BLACK:
                # bois pris 6 pixels plus loin (motif diagonal du bois)
                src = (x + 6) % (x1 - x0)
                k = 0
                while (px[y][x0 + src] == BLACK or px[3][x0 + src] == BLACK) and k < 40:
                    src = (src + 6) % (x1 - x0)
                    k += 1
                out[y][x] = px[y][x0 + src]
    return out


def main():
    with open(CMP, 'rb') as f:
        raw = f.read()
    data = decompressGfxData(raw, 1, SIZE, raw[0])[1]
    px = to_pixels(data)

    glyphs = {}
    for button in BUTTONS:
        glyphs.update({k: v for k, v in letters(px, button, button).items() if k not in glyphs})

    for button, label in NEW_LABELS.items():
        first, ncols = BUTTONS[button]
        x0 = (first + 1) * 8
        bg = wood(px, button)
        width = sum(len(glyphs[ch]) for ch in label) + 2 * (len(label) - 1)
        x = (len(bg[0]) - width) // 2
        for ch in label:
            for col in glyphs[ch]:
                for y in range(16):
                    if col[y]:
                        bg[y][x] = BLACK
                x += 1
            x += 2
        for y in range(16):
            px[y][x0:x0 + len(bg[0])] = bg[y]

    new = bytes(to_data(px))
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, 'in.bin'), os.path.join(tmp, 'out.cmp')
        with open(src, 'wb') as f:
            f.write(new)
        subprocess.run([sys.executable, os.path.join(DISASM, 'tools', 'build', 'compressGfx.py'), src, dst],
                       check=True, stdout=subprocess.DEVNULL)
        with open(dst, 'rb') as f:
            cmp = f.read()
    assert decompressGfxData(cmp, 1, SIZE, cmp[0])[1] == new
    with open(CMP, 'wb') as f:
        f.write(cmp)

    if len(sys.argv) > 1:
        from PIL import Image
        im = Image.new('L', (len(px[0]), 16))
        for y in range(16):
            for x in range(len(px[0])):
                im.putpixel((x, y), (255, 170, 85, 0)[px[y][x]])
        im.resize((im.width * 3, 48), Image.NEAREST).save(sys.argv[1])
    print('menu nouvelle partie : AGES / SEASONS')


main()
