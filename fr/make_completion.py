"""Données du suivi 100 % (menu Complétion) et des cœurs sur la carte, dans la
langue choisie : écrit oracles-disasm/code/crossworldCompletionData.s.

Les noms (lieux, donjons, essences, bagues, objets d'échange) viennent des
textes du jeu dans cette langue (text/<jeu>/text.yaml, écrits par
make_fr_text.py) ; seuls les titres des lignes sont propres au projet.

Usage : python fr/make_completion.py [--lang=fr]
"""
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lang as langmod
from make_secret_names import encode, center, db

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
OUT = os.path.join(DISASM, 'code', 'crossworldCompletionData.s')

ROW = 16    # caractères d'une ligne du menu
BOX = 11    # caractères visibles d'une ligne du cadre du bas

# Titres des lignes du résumé (10 caractères max), ligne « tout est fait »,
# aide du cadre du bas, noms des époques (cadre du bas, 11 max)
TEXTS = {
    'en': dict(labels=['Heart pcs.', 'Containers', 'Essences', 'Rings', 'Trading', 'Secrets', 'Total'],
               done='All done!', hint=('A = list', ''), eras=('Present', 'Past')),
    'fr': dict(labels=['Quarts', 'Réceptacle', 'Essences', 'Anneaux', 'Echanges', 'Secrets', 'Total'],
               done='Tout est fait!', hint=('A = liste', ''), eras=('Présent', 'Passé')),
    'de': dict(labels=['Herzteile', 'Herzcont.', 'Essenzen', 'Ringe', 'Tausch', 'Geheimn.', 'Gesamt'],
               done='Alles erledigt!', hint=('A = Liste', ''), eras=('Gegenwart', 'Vergangenh.')),
    'it': dict(labels=['Pz. cuore', 'Contenit.', 'Essenze', 'Anelli', 'Scambi', 'Segreti', 'Totale'],
               done='Tutto fatto!', hint=('A = lista', ''), eras=('Presente', 'Passato')),
    'es': dict(labels=['Piezas', 'Contened.', 'Esencias', 'Anillos', 'Trueques', 'Secretos', 'Total'],
               done='Completo!', hint=('A = lista', ''), eras=('Presente', 'Pasado')),
}
SEASONS_MAPS = ('Holodrum', 'Subrosia')

# Noms d'objets sur deux lignes que la règle « mot de liaison en fin de ligne »
# ne détecte pas : (langue, jeu, texte) -> nom
NAME_OVERRIDES = {
    ('fr', 'seasons', 'TX_0905'): 'Chaleur Nutrit.',
}
JOINING_WORDS = ('de', 'du', 'des', 'of', 'the', 'di', 'del', 'della', 'der', 'des', 'y')

# ---- Données des jeux (adresses : voir les symboles ages.sym / seasons.sym)
# Quarts de cœur : (adresse, masque, carte, case[, texte TX_03xx du lieu si la
# case a un nom spécial]) ; carte None = pas de case fixe ('gasha' / 'maple')
HEARTS = {
    'ages': [
        (0xc70d, 0x20, 0, 0x0d),    # Roule-Roche, chant des âges
        (0xc711, 0x20, 0, 0x11),    # Pics Talus, chant des flux
        (0xc78b, 0x20, 0, 0x8b),    # Cimetière Yoll
        (0xc886, 0x20, 1, 0x86),    # Tour Noire (passé), pelle
        (0xc8af, 0x20, 1, 0x43),    # grotte du Mur de la Restauration (3:af)
        (0xcac1, 0x20, 0, 0x18),    # grotte de Roule-Roche, mur à bombes
        (0xcab1, 0x20, 1, 0x91),    # grotte de la forêt Bojo (passé), buisson à brûler
        (0xc906, 0x20, 1, 0x38, 0x32),  # souterrain de Lynna (passé), blocs à pousser
        (0xc8fd, 0x20, 0, 0xba),    # grotte sous-marine (coffre)
        (0xc643, 0x40, 0, 0x68),    # boutique cachée de Lynna, 500 rubis
        (0xc64c, 0x02, None, 'gasha'),
        (0xc644, 0x80, None, 'maple'),
    ],
    'seasons': [
        (0xc7d8, 0x20, 0, 0xd8),    # Village Horon, buisson à brûler
        (0xc7d1, 0x20, 0, 0xd1),    # Cimetière, automne + cape
        (0xc7af, 0x20, 0, 0xaf),    # Bois Hivernaux, lac gelé
        (0xc7b1, 0x20, 0, 0xb1),    # Marais Boueux, printemps
        (0xc72d, 0x20, 0, 0x2d),    # Mt. Cocotte, printemps
        (0xc75b, 0x20, 0, 0x5b, 0x0c),  # Fort Moblin (coffre)
        (0xcab2, 0x20, 0, 0xea),    # grotte de la Banlieue est, hiver
        (0xcac7, 0x20, 0, 0x15),    # grotte des Restes du Temple
        (0xcac0, 0x20, 0, 0xaa),    # grotte du Lac Monocle (coffre)
        (0xc642, 0x02, 1, 0x45),    # Marché subrosien
        (0xc649, 0x02, None, 'gasha'),
        (0xc641, 0x80, None, 'maple'),
    ],
}
# Réceptacles : drapeau « objet pris » de la salle du boss de chaque donjon
CONTAINERS = {
    'ages': [0xc913, 0xc92b, 0xc94a, 0xc96b, 0xc9bf, 0xca36, 0xca62, 0xca78],
    'seasons': [0xc912, 0xc929, 0xc953, 0xc95f, 0xc98c, 0xc9d5, 0xca50, 0xca64],
}
ESSENCES = {'ages': 0xc6bf, 'seasons': 0xc6bb}
RINGS = 0xc616
# Quête d'échange : où on obtient chaque objet (carte, case) ; None = Maple.
# Les bits « fait » sont calculés par le jeu dans wFrCompTrade (voir
# frCompletion_prepare) ; le 13e est l'épée noble.
TRADE = {
    'ages': [(0, 0x7c), (1, 0x57), (1, 0x55), (0, 0xdd), (0, 0x53), (0, 0x66), (1, 0x13),
             (0, 0x56), (1, 0x56), None, (1, 0xa7), (1, 0x5a), (1, 0x23)],
    'seasons': [(0, 0xf9), (0, 0x88), None, (0, 0xa3), (1, 0x22), (0, 0x08), (0, 0x4d),
                (0, 0xb7), (0, 0x1b), (0, 0x5e), (0, 0xd7), (0, 0xda), (0, 0x40)],
}
TRADE_NOBLE_SWORD = 'TX_0924'
HEART_PIECE_TEXT = {'ages': 'TX_0961', 'seasons': 'TX_0952'}


# ---- Textes du jeu
def load_texts(game):
    path = os.path.join(DISASM, 'text', game, 'text.yaml')
    doc = yaml.safe_load(open(path, encoding='utf-8'))
    out = {}
    for group in doc['groups']:
        for e in group['data']:
            for n in (e['name'] if isinstance(e['name'], list) else [e['name']]):
                out[n] = e['text']
    return out


def decode(text):
    """Texte du yaml -> lignes d'octets (police du jeu), commandes retirées"""
    lines = []
    for line in text.split('\n'):
        out = []
        i = 0
        while i < len(line):
            if line[i] == '\\':
                m = re.match(r'\\x([0-9a-fA-F]{2})', line[i:])
                if m:
                    out.append(int(m.group(1), 16))
                    i += 4
                    continue
                m = re.match(r'\\[a-z]+(\([^)]*\))?', line[i:])
                i += len(m.group(0)) if m else 1
                continue
            out.append(ord(line[i]))
            i += 1
        lines.append(bytes(out).strip())
    return [l for l in lines if l]


def join(lines):
    out = b''
    for l in lines:
        if out and not out.endswith(b'-'):
            out += b' '
        out += l
    return out


def fit(name, width=ROW):
    if len(name) <= width:
        return name
    return name[:width - 1].rstrip() + b'.'


def item_name(code, game, texts, tx):
    if (code, game, tx) in NAME_OVERRIDES:
        return bytes(encode(NAME_OVERRIDES[(code, game, tx)]))
    lines = decode(texts[tx])
    name = lines[0]
    if name.split(b' ')[-1].decode('latin-1').lower() in JOINING_WORDS and len(lines) > 1:
        name = name + b' ' + lines[1]
    return fit(name)


def map_tables(game):
    """{0: [indices], 1: [indices]}, largeur de chaque table"""
    src = open(os.path.join(DISASM, 'data', game, 'mapTextAndPopups.s'), encoding='utf-8').read()
    tables = {}
    for m, label in ((0, 'presentMapTextIndices'), (1, 'pastMapTextIndices')):
        part = src.split(label + ':', 1)[1]
        rows = []
        for line in part.split('\n')[1:]:
            line = line.strip()
            if not line.startswith('.db'):
                if rows:
                    break
                continue
            rows.append([int(v[1:], 16) for v in line[3:].split()])
        tables[m] = rows
    return tables


def place_name(texts, tables, m, square):
    rows = tables[m]
    r, c = square >> 4, square & 15
    idx = rows[r][c]
    if idx & 0x80:   # case spéciale (donjon, arbre Maku...) : nom des cases voisines
        near = []
        for dr, dc in ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < len(rows) and 0 <= cc < len(rows[rr]) and not rows[rr][cc] & 0x80:
                near.append(rows[rr][cc])
        idx = max(set(near), key=near.count)
    return fit(join(decode(texts['TX_03%02x' % idx])))


def square_box(game, t, m, square):
    coord = '%s:%d' % (chr(ord('A') + (square & 15)), (square >> 4) + 1)
    era = (t['eras'] if game == 'ages' else SEASONS_MAPS)[m]
    return center(encode(coord)) + center(encode(era))


def line_box(line1, line2=b''):
    assert len(line1) <= BOX and len(line2) <= BOX, (line1, line2)
    return center(list(line1)) + center(list(line2))


def game_data(game, code, t):
    texts = load_texts(game)
    tables = map_tables(game)
    maple_name = texts['TX_0700'].split('\\col(3)')[1].split('\\')[0].encode('latin-1')
    gasha = item_name(code, game, texts, 'TX_0916')
    dungeon_levels = []
    dungeon_names = []
    for k in range(1, 9):
        lines = decode(texts['TX_02%02x' % k])
        dungeon_levels.append(lines[0])
        dungeon_names.append(fit(join(lines[1:])))

    cats = []
    # 0 quarts de cœur
    entries = []
    for addr, mask, m, square, *tx in HEARTS[game]:
        if m is None:
            entries.append((addr, mask, gasha if square == 'gasha' else maple_name, None))
        else:
            name = fit(join(decode(texts['TX_03%02x' % tx[0]]))) if tx else place_name(texts, tables, m, square)
            entries.append((addr, mask, name, square_box(game, t, m, square)))
    cats.append(entries)
    # 1 réceptacles (nom du donjon, niveau dans le cadre)
    cats.append([(addr, 0x20, dungeon_names[k], line_box(dungeon_levels[k]))
                 for k, addr in enumerate(CONTAINERS[game])])
    # 2 essences
    cats.append([(ESSENCES[game], 1 << k, item_name(code, game, texts, 'TX_09%02x' % (k + 1)),
                  line_box(dungeon_levels[k])) for k in range(8)])
    # 3 bagues
    cats.append([(RINGS + (i >> 3), 1 << (i & 7), fit(join(decode(texts['TX_30%02x' % (0x40 + i)]))), None)
                 for i in range(64)])
    # 4 échange (bits calculés dans wFrCompTrade)
    entries = []
    for i, where in enumerate(TRADE[game]):
        tx = TRADE_NOBLE_SWORD if i == 12 else 'TX_09%02x' % (0x09 + i)
        box = square_box(game, t, *where) if where else line_box(maple_name)
        entries.append(('wFrCompTrade+%d' % (i >> 3), 1 << (i & 7), item_name(code, game, texts, tx), box))
    cats.append(entries)
    # 5 secrets : pas de liste (A ouvre le suivi des codes), bits dans wFrCompSecrets
    cats.append([('wFrCompSecrets+%d' % (i >> 3), 1 << (i & 7), None, None) for i in range(10)])
    return cats


def emit(game, cats, lines, strings):
    def ref(data):
        data = bytes(data)
        if data not in strings:
            strings[data] = 'frCompStr%03x' % len(strings)
        return strings[data]

    lines.append('frCompCategories:')
    for k, entries in enumerate(cats):
        lines.append('\t.dw frCompEntries%d' % k)
        lines.append('\t.db $%02x' % len(entries))
    for k, entries in enumerate(cats):
        lines.append('frCompEntries%d:' % k)
        for addr, mask, name, box in entries:
            a = addr if isinstance(addr, str) else '$%04x' % addr
            n = ref(list(name) + [0]) if name is not None else '$0000'
            b = ref(box) if box is not None else '$0000'
            lines.append('\t.dw %s\n\t.db $%02x\n\t.dw %s, %s' % (a, mask, n, b))


def main():
    code, _ = langmod.current()
    t = TEXTS[code]
    lines = ['; Generated by fr/make_completion.py (language: %s), do not edit.' % code,
             '; Completion menu (OPT_COMPLETION) and map hearts (OPT_MAP_HEARTS).',
             ';', '; frCompCategories: per category, .dw entries, .db count',
             '; Entry: .dw flag address, .db mask (set = done), .dw row text (0-terminated,',
             '; 16 characters max) or 0, .dw bottom box text (2 x 12 characters) or 0.', '']
    strings = {}
    for game in ('ages', 'seasons'):
        cats = game_data(game, code, t)
        lines.append('.ifdef ROM_%s' % game.upper())
        emit(game, cats, lines, strings)
        # Cœurs de la carte : .db carte, case ; .dw adresse ; .db masque
        lines.append('frMapHearts:')
        for addr, mask, m, square, *_ in HEARTS[game]:
            if m is not None:
                lines.append('\t.db $%02x $%02x\n\t.dw $%04x\n\t.db $%02x' % (m, square, addr, mask))
        lines.append('\t.db $ff')
        lines.append('.endif')
        lines.append('')
    labels = t['labels']
    for i, l in enumerate(labels):
        assert len(encode(l)) <= 10, l
    lines.append('frCompLabels:')
    lines += ['\t.dw @label%d' % i for i in range(len(labels))]
    for i, l in enumerate(labels):
        lines.append('@label%d:' % i)
        lines.append(db(encode(l) + [0]))
    lines.append('frCompAllDoneRow:')
    assert len(encode(t['done'])) <= ROW
    lines.append(db(encode(t['done']) + [0]))
    lines.append('frCompHintBox:')
    lines.append(db(line_box(bytes(encode(t['hint'][0])), bytes(encode(t['hint'][1])))))
    lines.append('')
    lines.append('frCompStrings:')
    for data, label in strings.items():
        lines.append(label + ':')
        lines.append(db(data))
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print(OUT, code, len(strings), 'textes')


if __name__ == '__main__':
    main()
