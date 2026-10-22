"""Importe les graphismes français (menus, écran de fichier, Game Over, cartes-titres
des donjons, « À suivre… »…) depuis les ROMs Europe.

Dans les ROMs EU, une image qui dépend de la langue a un en-tête spécial :
    00, puis 5 sources de 3 octets (banque|mode<<6, adresse big-endian), une par
    langue dans l'ordre EN FR DE IT ES (voir fr/lang.py), puis destination (2 octets) et taille.
La table des en-têtes EU suit le même ordre que celle du désassemblage : on
parcourt les deux en parallèle pour savoir quelle image remplacer.

- Si l'en-tête EU couvre toute l'image US : on copie les données françaises
  compressées telles quelles dans le .cmp précompressé.
- Sinon (EU a coupé l'image en une partie commune + une partie par langue) :
  on reconstitue l'image complète décompressée et on la recompresse.

Le script ne lit que les ROMs EU et la table d'en-têtes (dans git) : on peut
le relancer autant de fois qu'on veut.

Usage : python fr/import_fr_gfx.py   [--lang=fr|en|de|it|es]   (depuis la racine du dépôt)
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.environ.get('ZOC_DISASM') or os.path.join(ROOT, 'oracles-disasm')
sys.path.insert(0, os.path.join(DISASM, 'tools'))
from common import decompressGfxData  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lang  # noqa: E402

LANG_CODE, LANG = lang.current()
# Dernier commit de master avant la branche crossworld : même ordre d'en-têtes que la ROM US.
BASE_COMMIT = '309a2cff'
GAMES = {
    # rom EU, adresse de la table des en-têtes graphiques
    'ages': ('Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc', 0x5c51e),
    'seasons': ('Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc', 0x58000),
}
HEADER = re.compile(r'\s*m_GfxHeader\w*\s+(\w+)\s+(\S+)\s+\$(\w+)')


def us_groups(game):
    """Liste ordonnée des groupes d'en-têtes US : [(nom, dest, taille)].
    Un label vide est un alias du groupe suivant."""
    src = subprocess.run(['git', 'show', '%s:data/%s/gfxHeaders.s' % (BASE_COMMIT, game)],
                         cwd=DISASM, capture_output=True, text=True, check=True).stdout
    order, groups, pending, current = [], {}, [], None
    for line in src.splitlines():
        m = re.match(r'\s*\.dw (gfxHeader\w+)', line)
        if m:
            order.append(m.group(1))
            continue
        m = re.match(r'(gfxHeader\w+):', line)
        if m:
            pending.append(m.group(1))
            continue
        m = HEADER.match(line)
        if m:
            if pending:
                # Tous les labels en attente partagent la même liste.
                current = []
                for label in pending:
                    groups[label] = current
                pending = []
            dest = m.group(2)
            dest = int(dest[1:], 16) if dest.startswith('$') else None
            current.append((m.group(1), dest, int(m.group(3), 16) & 0x7f))
    return [groups.get(label, []) for label in order]


def eu_group(eu, table_bank, pointer):
    """Enregistrements d'un groupe EU : (dest, taille, [sources]) ; 1 source ou 5 (par langue)."""
    p = table_bank * 0x4000 + pointer - 0x4000
    out = []
    while True:
        if eu[p] == 0:
            srcs = [(eu[p + 1 + i * 3], (eu[p + 2 + i * 3] << 8) | eu[p + 3 + i * 3]) for i in range(5)]
            p += 16
        else:
            srcs = [(eu[p], (eu[p + 1] << 8) | eu[p + 2])]
            p += 3
        dest = (eu[p] << 8) | eu[p + 1]
        size = eu[p + 2]
        out.append((dest, size & 0x7f, srcs))
        p += 3
        if not size & 0x80:
            return out


def offset(src):
    return (src[0] & 0x3f) * 0x4000 + src[1] - 0x4000


def decompress(rom, src, size):
    return decompressGfxData(rom, offset(src), size, src[0] >> 6)


def cmp_path(game, name):
    for sub in ('common', game):
        p = os.path.join(DISASM, 'precompressed', 'gfx_compressible', sub, name + '.cmp')
        if os.path.exists(p):
            return p
    return None


def compress(data):
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = os.path.join(tmp, 'in.bin'), os.path.join(tmp, 'out.cmp')
        with open(src, 'wb') as f:
            f.write(data)
        subprocess.run([sys.executable, os.path.join(DISASM, 'tools', 'build', 'compressGfx.py'), src, dst],
                       check=True, stdout=subprocess.DEVNULL)
        with open(dst, 'rb') as f:
            return f.read()


def french_images(game):
    """{nom de fichier US : données françaises décompressées ou (mode, données compressées)}"""
    rom_name, table = GAMES[game]
    with open(os.path.join(ROOT, rom_name), 'rb') as f:
        eu = f.read()
    table_bank = table // 0x4000
    result = {}
    for i, us in enumerate(us_groups(game)):
        a = table + 2 * i
        records = eu_group(eu, table_bank, eu[a] | (eu[a + 1] << 8))
        if not any(len(srcs) == 5 for _, _, srcs in records):
            continue
        # Groupe propre à la version EU (alias côté US) : rien à remplacer.
        if not us or us[0][1] != records[0][0]:
            continue
        us_keys = {(dest, size) for _, dest, size in us}
        for name, dest, size in us:
            if dest is None or not cmp_path(game, name) or result.get(name, ('',))[0] == 'cmp':
                continue
            exact = [r for r in records if (r[0], r[1]) == (dest, size)]
            if exact:
                parts = exact[:1]
            else:
                # Morceaux EU qui tombent dans la zone de l'image US (sauf ceux
                # qui correspondent exactement à une autre image du groupe).
                start, end = dest & 0xfff0, (dest & 0xfff0) + (size + 1) * 16
                parts = [(d, s, srcs) for d, s, srcs in records
                         if (d & 0xf) == (dest & 0xf) and start <= (d & 0xfff0) < end
                         and (d, s) not in us_keys]
            if not any(len(srcs) == 5 for _, _, srcs in parts):
                continue
            start = dest & 0xfff0
            if len(parts) == 1 and parts[0][1] == size:
                src = parts[0][2][LANG]
                endaddr = decompress(eu, src, size)[0]
                result[name] = ('cmp', bytes([src[0] >> 6]) + eu[offset(src):endaddr])
            else:
                # Image coupée par la version EU : on recolle les morceaux.
                data = bytearray((size + 1) * 16)
                for d, s, srcs in parts:
                    piece = decompress(eu, srcs[LANG if len(srcs) == 5 else 0], s)[1]
                    o = (d & 0xfff0) - start
                    piece = piece[:len(data) - o]
                    data[o:o + len(piece)] = piece
                result[name] = ('bin', bytes(data))
    return result


def main():
    written = {}
    for game in GAMES:
        for name, (kind, data) in sorted(french_images(game).items()):
            path = cmp_path(game, name)
            cmp = data if kind == 'cmp' else compress(data)
            if path in written and written[path] != cmp:
                # Fichier « common » déjà écrit pour Ages : on garde la version Ages.
                print('%-8s %-28s (déjà importé depuis Ages)' % (game, name))
                continue
            with open(path, 'wb') as f:
                f.write(cmp)
            written[path] = cmp
            print('%-8s %-28s %s' % (game, name, 'recollée + recompressée' if kind == 'bin' else 'copiée'))


main()
