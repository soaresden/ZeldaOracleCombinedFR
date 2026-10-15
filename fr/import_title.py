"""Écran titre combiné Ages + Seasons : convertit fr/title_combined.png (160x144,
déjà réduit à 8 palettes de 4 couleurs, voir fr/title_src/) en données Game Boy
Color pour la moitié Ages de la ROM (celle qui démarre) :

- gfx/ages/gfx_titlecombo_1.bin / _2.bin : tuiles 2bpp (VRAM banque 0, $8800 puis $9000)
- gfx/ages/map_titlecombo.bin / flg_titlecombo.bin : carte de tuiles et attributs 32x18
- data/ages/paletteData.s : les 8 palettes de fond du titre (paletteData4018)

Usage : python fr/import_title.py
"""
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
PNG = os.path.join(ROOT, 'fr', 'title_combined.png')
GFX_DIR = os.path.join(DISASM, 'gfx', 'ages')
PALETTE_FILE = os.path.join(DISASM, 'data', 'ages', 'paletteData.s')
W, H = 20, 18          # écran en tuiles
MAP_W = 32             # largeur de la carte de fond en VRAM


def main():
    im = Image.open(PNG).convert('RGB')
    tiles = [[im.getpixel((tx * 8 + x, ty * 8 + y)) for y in range(8) for x in range(8)]
             for ty in range(H) for tx in range(W)]

    # Palettes : on regroupe les ensembles de couleurs des tuiles (8 au maximum)
    palettes = []
    for colors in sorted({frozenset(t) for t in tiles}, key=len, reverse=True):
        for pal in palettes:
            if colors <= set(pal) or len(set(pal) | colors) <= 4:
                pal.extend(c for c in sorted(colors) if c not in pal)
                break
        else:
            palettes.append(sorted(colors))
    assert len(palettes) <= 8, '%d palettes (8 maximum)' % len(palettes)
    for pal in palettes:
        while len(pal) < 4:
            pal.append(pal[0])

    # Tuiles 2bpp dédoublonnées, carte et attributs
    tile_data, tile_index = [], {}
    tilemap, attrs = bytearray(MAP_W * H), bytearray(MAP_W * H)
    for i, t in enumerate(tiles):
        p = next(k for k, pal in enumerate(palettes) if set(t) <= set(pal))
        data = bytearray(16)
        for y in range(8):
            for x in range(8):
                c = palettes[p].index(t[y * 8 + x])
                data[y * 2] |= (c & 1) << (7 - x)
                data[y * 2 + 1] |= (c >> 1) << (7 - x)
        key = bytes(data)
        if key not in tile_index:
            tile_index[key] = len(tile_data)
            tile_data.append(key)
        n = tile_index[key]
        tx, ty = i % W, i // W
        # Mode d'adressage $8800 : tuiles $80-$ff en $8800, $00-$7f en $9000
        tilemap[ty * MAP_W + tx] = (n + 0x80) & 0xff
        attrs[ty * MAP_W + tx] = p
    assert len(tile_data) <= 256, '%d tuiles (256 maximum)' % len(tile_data)

    def write(name, data):
        with open(os.path.join(GFX_DIR, name), 'wb') as f:
            f.write(data)
    write('gfx_titlecombo_1.bin', b''.join(tile_data[:128]))
    write('gfx_titlecombo_2.bin', b''.join(tile_data[128:]) or bytes(16))
    write('map_titlecombo.bin', bytes(tilemap))
    write('flg_titlecombo.bin', bytes(attrs))

    # Palettes de fond du titre
    with open(PALETTE_FILE, encoding='utf-8') as f:
        src = f.read()
    lines = []
    for pal in palettes + [palettes[0]] * (8 - len(palettes)):
        for r, g, b in pal:
            lines.append('\tm_RGB16 $%02x $%02x $%02x' % (r >> 3, g >> 3, b >> 3))
        lines.append('')
    block = 'paletteData4018:\n; FR : écran titre combiné (généré par fr/import_title.py)\n' + '\n'.join(lines) + '\n'
    src, n = re.subn(r'paletteData4018:\n.*?(?=paletteData4058:)', lambda m: block, src, flags=re.S)
    assert n == 1
    with open(PALETTE_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src)

    print('titre : %d tuiles, %d palettes' % (len(tile_data), len(palettes)))


main()
