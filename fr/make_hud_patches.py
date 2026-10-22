"""Patchs BPS « barre du bas seule » : source = une ROM Europe (Ages ou Seasons),
cible = out/hud-<jeu>-<langue>.gbc (jeu d'origine séparé, barre en bas).
Écrit docs/patches/hud/<jeu>-<langue>.bps et docs/patches/hud/manifest.json.

Usage : python fr/make_hud_patches.py [en fr de it es]
"""
import json
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bps  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EU = {
    'ages': 'Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc',
    'seasons': 'Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc',
}
OUT = os.path.join(ROOT, 'docs', 'patches', 'hud')


def crc(data):
    return '%08x' % (zlib.crc32(data) & 0xffffffff)


def main(langs):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'manifest.json')
    manifest = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    manifest.setdefault('patches', {})
    for game, name in EU.items():
        source = open(os.path.join(ROOT, name), 'rb').read()
        manifest.setdefault('source', {})[game] = {'size': len(source), 'crc32': crc(source), 'file': name}
        for lang in langs:
            target = open(os.path.join(ROOT, 'out', 'hud-%s-%s.gbc' % (game, lang)), 'rb').read()
            patch = bps.encode(source, target)
            assert bps.decode(source, patch) == target
            fname = '%s-%s.bps' % (game, lang)
            with open(os.path.join(OUT, fname), 'wb') as f:
                f.write(patch)
            manifest['patches']['%s-%s' % (game, lang)] = {
                'file': 'patches/hud/' + fname, 'size': len(patch), 'targetCrc32': crc(target)}
            print('%s %s : %d Ko' % (game, lang, len(patch) // 1024))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['en', 'fr', 'de', 'it', 'es'])
