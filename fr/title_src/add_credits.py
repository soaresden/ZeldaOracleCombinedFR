"""Crédits en petit en bas de l'écran titre : title_base.png (le titre sans
crédits, sortie de choosepal.py) -> fr/title_combined.png.

Rangée 16 : « ORIGINAL MOD BY DANIEL JIANORAN » (le hack crossworld d'origine)
Rangée 17 : « FOLLOW-UP BY SOARESDEN » et « (C)2001 NINTENDO »
Police de 5 pixels de haut, environ deux lettres par tuile 8x8 : l'image est déjà presque à la
limite de 256 tuiles différentes.

Usage : python fr/title_src/add_credits.py [sortie.png]
Ensuite : python fr/import_title.py
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(HERE, 'title_base.png')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'fr', 'title_combined.png')

TEXT = (224, 240, 248)    # blanc du titre
SHADOW = (112, 96, 32)    # ombre (couleur du © d'origine)
YELLOW = (208, 176, 0)    # jaune du bandeau SEASONS

FONT = {
    'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'],
    'C': ['011', '100', '100', '100', '011'], 'D': ['110', '101', '101', '101', '110'],
    'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
    'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'],
    'I': ['111', '010', '010', '010', '111'], 'J': ['001', '001', '001', '101', '010'],
    'L': ['100', '100', '100', '100', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
    'N': ['110', '101', '101', '101', '101'], 'O': ['010', '101', '101', '101', '010'],
    'P': ['110', '101', '110', '100', '100'], 'R': ['110', '101', '110', '101', '101'],
    'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'],
    'U': ['101', '101', '101', '101', '111'], 'W': ['10001', '10001', '10101', '11011', '10001'],
    'Y': ['101', '101', '010', '010', '010'], '0': ['111', '101', '101', '101', '111'],
    '1': ['010', '110', '010', '010', '111'], '2': ['110', '001', '010', '100', '111'],
    '-': ['000', '000', '111', '000', '000'], ' ': ['00'] * 5,
    '(': ['01', '10', '10', '10', '01'], ')': ['10', '01', '01', '01', '10'],
}


def text_width(s):
    return sum(len(FONT[ch][0]) + 1 for ch in s) - 1


def draw(im, s, x, y, color=TEXT):
    """Lettres de 5 pixels de haut (M et W plus larges), ombre en dessous.
    Renvoie la position après le texte."""
    for ch in s:
        g = FONT[ch]
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit == '1':
                    px, py = x + gx, y + gy
                    for sx, sy, c in ((0, 1, SHADOW), (0, 0, color)):
                        if im.getpixel((px + sx, py + sy)) not in (TEXT, YELLOW):
                            im.putpixel((px + sx, py + sy), c)
        x += len(g[0]) + 1
    return x


def palettes(im):
    """Les 8 palettes de l'image (même regroupement que fr/import_title.py)."""
    tiles = [[im.getpixel((tx * 8 + x, ty * 8 + y)) for y in range(8) for x in range(8)]
             for ty in range(18) for tx in range(20)]
    pals = []
    for colors in sorted({frozenset(t) for t in tiles}, key=len, reverse=True):
        for pal in pals:
            if colors <= set(pal) or len(set(pal) | colors) <= 4:
                pal.extend(c for c in sorted(colors) if c not in pal)
                break
        else:
            pals.append(sorted(colors))
    return pals


def fit_rows(im, pals, rows):
    """Chaque tuile de ces rangées prend la palette existante qui l'abîme le
    moins (texte blanc, ombre et jaune compris) : pas de palette en plus."""
    def dist(a, b):
        return sum((p - q) ** 2 for p, q in zip(a, b))
    for ty in rows:
        for tx in range(20):
            px = [(tx * 8 + x, ty * 8 + y) for y in range(8) for x in range(8)]
            cols = [im.getpixel(p) for p in px]
            # Le texte doit garder ses couleurs exactes : palettes qui les ont
            need = {c for c in cols if c in (TEXT, YELLOW, SHADOW)}
            cand = [p for p in pals if need <= set(p)] or pals
            best = min(cand, key=lambda p: sum(min(dist(c, q) for q in p) for c in cols))
            for p, c in zip(px, cols):
                im.putpixel(p, min(best, key=lambda q: dist(q, c)))


def main():
    im = Image.open(BASE).convert('RGB')
    # Pas de bandeau : le texte est posé sur le décor. Sous l'ancien gros
    # « ©2001 Nintendo » (rangée 17), le décor de la rangée 16 est prolongé.
    for y in range(136, 144):
        for x in range(160):
            im.putpixel((x, y), im.getpixel((x, 135)))
    # Côté orange, orange uni sous le texte (la seule palette orange qui a le
    # blanc et l'ombre n'a pas les orangés clairs) ; à droite, le tourbillon
    # clair n'a pas l'ombre : bleu uni.
    for y in range(128, 144):
        for x in range(160):
            c = im.getpixel((x, y))
            if x < 48 and c[0] > c[2]:
                im.putpixel((x, y), (240, 104, 0))
            elif x >= 152:
                im.putpixel((x, y), (80, 144, 248))
    pals = palettes(Image.open(BASE).convert('RGB'))
    line1 = 'ORIGINAL MOD BY DANIEL JIANORAN'
    draw(im, line1, (160 - text_width(line1)) // 2, 129)
    x = draw(im, 'FOLLOW-UP BY ', 3, 137)
    end = draw(im, 'SOARESDEN', x, 137, YELLOW)
    copy = '(C)2001 NINTENDO'
    start = 160 - 3 - text_width(copy) - 1
    assert start - end >= 4, 'rangée 17 trop longue (%d, %d)' % (end, start)
    draw(im, copy, start, 137)
    fit_rows(im, pals, (16, 17))
    im.save(OUT)
    print(OUT)


main()
