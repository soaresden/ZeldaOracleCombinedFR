"""Remplace la police du jeu par celle de la ROM Europe (quelques glyphes accentués
en plus : Ô, °, Í, Ó, Ú, ß, ¡, ¿…).

La police est en 1bpp, 16 octets par caractère (8x16), 256 caractères, dans
gfx/common/gfx_font.png (16 caractères par ligne). Un bit à 1 dans la ROM
correspond à un pixel de la couleur de fond de l'image.

Usage : python fr/import_fr_font.py   (depuis la racine ZeldaOracleCombinedFR)
"""
import io
import os
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, 'oracles-disasm', 'gfx', 'common', 'gfx_font.png')
EU_ROM = 'Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc'
US_ROM = 'Legend of Zelda, The - Oracle of Ages (USA).gbc'
GLYPH_A = bytes.fromhex('ffffffffffffe7dbdbdbbdbd81bdbdff')  # « A », caractère 0x41


def read_font(rom_name):
    with open(os.path.join(ROOT, rom_name), 'rb') as f:
        rom = f.read()
    start = rom.find(GLYPH_A) - 0x41 * 16
    return rom[start:start + 0x1000]


def main():
    font, us_font = (read_font(r) for r in (EU_ROM, US_ROM))

    # Police anglaise d'origine relue dans git : on peut relancer le script.
    png = subprocess.run(['git', 'show', '37a4eef3:gfx/common/gfx_font.png'],
                         cwd=os.path.dirname(os.path.dirname(os.path.dirname(PNG))),
                         capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png))
    im.load()
    px = im.load()
    bg = px[0, 0]
    fg = next(px[x, y] for y in range(im.height) for x in range(im.width) if px[x, y] != bg)
    # Seuls les glyphes qui diffèrent entre US et EU sont redessinés (les
    # premiers caractères de l'image utilisent d'autres couleurs).
    for c in (c for c in range(256) if font[c * 16:c * 16 + 16] != us_font[c * 16:c * 16 + 16]):
        for y in range(16):
            b = font[c * 16 + y]
            for x in range(8):
                px[(c % 16) * 8 + x, (c // 16) * 16 + y] = bg if b & (0x80 >> x) else fg
    im.save(PNG)
    print('police EU importée')


main()
