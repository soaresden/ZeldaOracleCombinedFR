"""Patchs BPS de la page web : source = ROM Ages Europe + ROM Seasons Europe mises
bout à bout, cible = out/zoc-<langue>.gbc. Écrit docs/patches/<langue>.bps,
docs/patches/manifest.json et copie fr/options.json dans docs/.

Usage : python fr/make_patches.py [en fr de it es]
"""
import json
import os
import shutil
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bps  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EU = {
    'ages': 'Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc',
    'seasons': 'Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc',
}
DOCS = os.path.join(ROOT, 'docs')


def crc(data):
    return '%08x' % (zlib.crc32(data) & 0xffffffff)


def main(langs):
    roms = {g: open(os.path.join(ROOT, n), 'rb').read() for g, n in EU.items()}
    source = roms['ages'] + roms['seasons']
    os.makedirs(os.path.join(DOCS, 'patches'), exist_ok=True)
    manifest_path = os.path.join(DOCS, 'patches', 'manifest.json')
    manifest = json.load(open(manifest_path, encoding='utf-8')) if os.path.exists(manifest_path) else {}
    manifest['source'] = {g: {'size': len(r), 'crc32': crc(r), 'file': EU[g]} for g, r in roms.items()}
    manifest.setdefault('patches', {})
    for lang in langs:
        target = open(os.path.join(ROOT, 'out', 'zoc-%s.gbc' % lang), 'rb').read()
        patch = bps.encode(source, target)
        assert bps.decode(source, patch) == target
        with open(os.path.join(DOCS, 'patches', '%s.bps' % lang), 'wb') as f:
            f.write(patch)
        manifest['patches'][lang] = {'file': 'patches/%s.bps' % lang, 'size': len(patch),
                                     'targetCrc32': crc(target)}
        print('%s : %d Ko' % (lang, len(patch) // 1024))
    with open(manifest_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    shutil.copyfile(os.path.join(ROOT, 'fr', 'options.json'), os.path.join(DOCS, 'options.json'))


main(sys.argv[1:] or ['en', 'fr', 'de', 'it', 'es'])
