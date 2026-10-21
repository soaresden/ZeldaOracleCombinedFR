"""Icônes des jeux : sablier = Ages, soleil = Seasons. Couleurs (palette de la
barre) : 0 = blanc, 1 = rouge, 2 = fond, 3 = noir.

- gfx/ages|seasons/gfx_fr_hud_icon.bin : l'icône du jeu en cours, dans la barre
  d'état (option « icône de jeu »), tuile $3f.
- gfx/common/gfx_fr_map_heart.bin : cœur 8x16 (palette 5 de la carte, rouge) qui
  marque sur la carte les quarts de cœur pas encore pris (tuiles $6c-$6d).
- gfx/common/gfx_fr_door_icons.bin : sablier puis soleil, chacun centré sur
  deux tuiles (16x8), au-dessus des portes de la boutique de Vasu (option
  « icônes des portes »), tuiles $3a-$3d. Porte de gauche = Ages, droite = Seasons
  dans les deux jeux.

Usage : python fr/make_hud_icons.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ICONS = {
    'ages': [          # sablier
        '33333333',
        '23000032',
        '22311322',
        '22231222',
        '22230222',
        '22300322',
        '23111132',
        '33333333',
    ],
    'seasons': [       # soleil
        '22212222',
        '21212122',
        '22111222',
        '11101112',
        '22111222',
        '21212122',
        '22212222',
        '22222222',
    ],
}


def to_2bpp(rows):
    out = bytearray()
    for row in rows:
        lo = hi = 0
        for x, c in enumerate(row):
            v = int(c)
            lo |= (v & 1) << (7 - x)
            hi |= (v >> 1) << (7 - x)
        out += bytes([lo, hi])
    return bytes(out)


def write(path, data):
    path = os.path.join(ROOT, 'oracles-disasm', 'gfx', *path)
    with open(path, 'wb') as f:
        f.write(data)
    print(path)


for game, rows in ICONS.items():
    write((game, 'gfx_fr_hud_icon.bin'), to_2bpp(rows))

door = b''
for game in ('ages', 'seasons'):
    wide = ['2222' + row + '2222' for row in ICONS[game]]   # icône centrée sur 16 px
    door += to_2bpp([r[:8] for r in wide]) + to_2bpp([r[8:] for r in wide])
write(('common', 'gfx_fr_door_icons.bin'), door)

# Cœur de la carte : 8x16 (deux tuiles l'une sous l'autre), centré. 1 = rouge,
# 2 = rouge foncé, 3 = noir (palette de sprites 5 de la carte), 0 = transparent.
MAP_HEART = [
    '00000000',
    '00000000',
    '00000000',
    '00000000',
    '03303300',
    '31131130',
    '31111130',
    '31111130',
    '03121300',
    '00313000',
    '00030000',
    '00000000',
    '00000000',
    '00000000',
    '00000000',
    '00000000',
]
write(('common', 'gfx_fr_map_heart.bin'), to_2bpp(MAP_HEART[:8]) + to_2bpp(MAP_HEART[8:]))
