"""Test automatique des objets, dans les deux jeux de la ROM combinée (PyBoy).

1. Obtention : pour chaque objet d'inventaire ($01-$1f) et chaque variante
   (subid) que le jeu peut donner (data/<jeu>/treasureObjectData.s : coffres,
   scripts, boutiques), le test part d'un inventaire vide, appelle la vraie
   fonction giveTreasure avec le même paramètre que le jeu, puis vérifie que
   l'objet est dans l'inventaire et que le menu l'affiche avec sa propre ligne
   (loadTreasureDisplayData) : sinon le menu montre un autre objet, comme la
   plume affichée en lance-pierres quand son niveau vaut 0.
2. Niveau 0 : chaque objet à niveaux (épée, bouclier, bracelet, plume,
   boomerang, grappin) est donné puis son niveau remis à 0 ; le menu doit
   toujours le montrer (c'était la plume affichée en lance-pierres).
3. Aller-retour : tous les objets d'un jeu sont donnés, puis le jeu change
   d'aventure comme par la porte de Vasu (wSwapGame) ; les objets doivent être
   là et bien affichés dans l'autre jeu, puis de nouveau dans le premier.

Usage : python fr/test_items.py [rom]   (par défaut out/zoc-fr.gbc)
Code de retour 1 s'il y a des anomalies.
"""
import os
import re
import sys

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIS = os.path.join(ROOT, 'oracles-disasm')
ROM = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'zoc-fr.gbc')

BOOT = 'w1300,pstart,w150,pstart,w150'
NEW_GAME = {
    'ages': BOOT + ',pa,w60,pa,w60,pa,w20,pa,w20,pstart,w30,pa,w90,pa,w60,pa,w200' + ',pa,w50' * 30,
    'seasons': BOOT + ',pa,w60,pdown,w20,pa,w60,pa,w20,pa,w20,pstart,w30,pa,w90,pa,w60,pa,w200' + ',pa,w50' * 40,
}
OTHER = {'ages': 'seasons', 'seasons': 'ages'}
SWAP_VALUE = {'ages': 0x03, 'seasons': 0x02}   # wSwapGame : SRAMBANK_SEASONS / SRAMBANK_AGES
BANK_BASE = {'ages': 0, 'seasons': 0x100}      # Seasons : banques $100-$1ff de la ROM combinée
SENTINEL = 0x3fe8                               # retour factice (zone d'options, jamais exécutée)
# Objets qui n'existent pas dans un jeu (leurs données y sont des restes)
NOT_IN_GAME = {'ages': {0x07, 0x08, 0x13, 0x1e}, 'seasons': {0x04, 0x0a, 0x0f, 0x11}}

# Variables remises à zéro avant chaque objet (niveaux, munitions, choix)
RESET_VARS = (r'^w(Sword|Shield|Bracelet|Feather|Boomerang|Slingshot|SwitchHook|SeedSatchel)Level$|'
              r'^wMagnetGlovePolarity$|^wFluteIcon$|^wSelectedHarpSong$|^w(Satchel|Shooter|Slingshot)SelectedSeeds$|'
              r'^wNumBombs$|^wMaxBombs$|^wNumBombchus$|^wTuniNutState$')

TREASURE_NAMES = {}
for _line in open(os.path.join(DIS, 'constants', 'treasure.s')):
    _m = re.match(r'\s*TREASURE_(\w+)\s+db\s*;\s*\$([0-9a-f]{2})', _line)
    if _m and int(_m.group(2), 16) < 0x20:
        TREASURE_NAMES[int(_m.group(2), 16)] = _m.group(1).lower()


def load_syms(game):
    syms = {}
    for line in open(os.path.join(DIS, game + '.sym')):
        m = re.match(r'([0-9a-f]{2}):([0-9a-f]{4}) (\S+)', line)
        if m:
            # Même nom dans plusieurs banques (ex. loadTreasureDisplayData) : la banque 0 d'abord
            name, bank = m.group(3), int(m.group(1), 16)
            if name not in syms or bank == 0:
                syms[name] = (bank, int(m.group(2), 16))
    return syms


class Runner:
    """Une partie dans PyBoy ; self.game change avec l'aventure en cours."""

    def __init__(self, game):
        self.rom = open(ROM, 'rb').read()
        self.all_syms = {g: load_syms(g) for g in ('ages', 'seasons')}
        self.set_game(game)
        self.pb = PyBoy(ROM, window='null', cgb=True, sound_emulated=True, sound_volume=0)
        self.pb.set_emulation_speed(0)
        self.run(NEW_GAME[game])

    def set_game(self, game):
        self.game, self.syms = game, self.all_syms[game]

    def addr(self, name):
        return self.syms[name][1]

    def rom_read(self, name, n):
        bank, a = self.syms[name]
        if bank:
            bank += BANK_BASE[self.game]
        off = bank * 0x4000 + (a - 0x4000 if a >= 0x4000 else a)
        return self.rom[off:off + n]

    def rom_at(self, bank, a, n):
        off = (bank + BANK_BASE[self.game]) * 0x4000 + a - 0x4000
        return self.rom[off:off + n]

    def run(self, steps):
        for step in steps.split(','):
            if step[0] == 'w':
                self.pb.tick(int(step[1:]), False)
            elif step[0] == 'p':
                self.pb.button(step[1:], 4)
                self.pb.tick(12, False)

    def call(self, func, a=0, c=0):
        """Appelle une fonction de la banque 0 entre deux images, comme le jeu."""
        pb, st = self.pb, {'armed': True, 'done': False}

        def inject(_):
            if not st['armed']:
                return
            st['armed'] = False
            r = pb.register_file
            st['saved'] = (r.SP, r.PC, r.A, r.F, r.B, r.C, r.D, r.E, r.HL)
            r.SP -= 2
            pb.memory[r.SP] = SENTINEL & 0xff
            pb.memory[r.SP + 1] = SENTINEL >> 8
            r.A, r.C = a, c
            r.PC = self.addr(func)

        def back(_):
            r = pb.register_file
            st['out'] = (r.A, r.C, r.HL)
            r.SP, r.PC, r.A, r.F, r.B, r.C, r.D, r.E, r.HL = st['saved']
            st['done'] = True

        pb.hook_register(0, self.addr('_mainLoop_nextThread'), inject, None)
        pb.hook_register(0, SENTINEL, back, None)
        for _ in range(60):
            pb.tick(1, False)
            if st['done']:
                break
        pb.hook_deregister(0, self.addr('_mainLoop_nextThread'))
        pb.hook_deregister(0, SENTINEL)
        assert st['done'], func
        return st['out']

    def reset_inventory(self):
        m = self.pb.memory
        for i in range(18):
            m[self.addr('wInventoryB') + i] = 0
        for i in range(4):   # drapeaux des objets $00-$1f
            m[self.addr('wObtainedTreasureFlags') + i] = 0
        for name in self.syms:
            if re.match(RESET_VARS, name):
                m[self.addr(name)] = 0

    def inventory(self):
        return [self.pb.memory[self.addr('wInventoryB') + i] for i in range(18)]

    def display(self, t):
        """Les 7 octets que le menu affiche pour l'objet t."""
        hl = self.call('loadTreasureDisplayData', a=t)[2]
        return bytes(self.pb.memory[hl + i] for i in range(7))

    def swap(self):
        """Change d'aventure comme la porte de Vasu, puis attend que l'autre jeu tourne."""
        other = OTHER[self.game]
        self.pb.memory[self.addr('wSwapGame')] = SWAP_VALUE[self.game]
        for _ in range(40):
            self.run('w30,pa')
        self.set_game(other)
        cur = self.pb.memory[self.addr('wCurrentGame')]
        assert cur == (0 if other == 'ages' else 1), 'changement de jeu raté'


# ---- Tables du jeu en cours (lues dans la ROM)

def object_subids(r):
    """{trésor: [(subid, paramètre)]} lu dans treasureObjectData."""
    bank, base = r.syms['treasureObjectData']
    raw = r.rom_at(bank, base, 0x80 * 4)
    ptrs = {}
    targets = set()
    for t in range(0x80):
        e = raw[t * 4:t * 4 + 4]
        if e[0] & 0x80:
            ptrs[t] = e[1] | e[2] << 8
            targets.add(ptrs[t])
    targets = sorted(targets)
    out = {}
    for t in range(1, 0x20):
        if t in ptrs:
            p = ptrs[t]
            n = (min([x for x in targets if x > p] + [p + 0x40]) - p) // 4
            out[t] = [(i, r.rom_at(bank, p + i * 4 + 1, 1)[0]) for i in range(n)]
        else:
            e = raw[t * 4:t * 4 + 4]
            out[t] = [(0, e[1])] if (e[0] or e[3]) else []
    return out


def sub_tables(r):
    """[(nom, adresse, fin)] des sous-tables de treasureDisplayData2."""
    labels = sorted((a, n.split('@', 1)[1]) for n, (b, a) in r.syms.items()
                    if n.startswith('treasureDisplayData2@'))
    bank, start = r.syms['treasureDisplayData2']
    size = int([l for l in open(os.path.join(DIS, r.game + '.sym'))
                if l.strip().endswith(' _sizeof_treasureDisplayData2')][0].split()[0], 16)
    return [(n, a, labels[i + 1][0] if i + 1 < len(labels) else start + size)
            for i, (a, n) in enumerate(labels)]


def expected_tables(r, t):
    """Sous-tables où l'objet t a le droit d'être affiché."""
    raw = r.rom_read('treasureDisplayData1', 0x40)
    ptrs = r.rom_read('treasureDisplayData2', 0x20)
    by_addr = {a: n for n, a, _ in sub_tables(r)}
    want = set()
    for i in range(0, 0x40, 3):
        if raw[i] == 0:
            break
        if raw[i] == t:
            e = raw[i + 2]
            p = ptrs[e * 2] | ptrs[e * 2 + 1] << 8
            # Les pointeurs « - 7 » (niveau 1 = première ligne) visent 7 octets avant
            want.add(by_addr.get(p) or by_addr.get(p + 7) or '?')
    return want or {'standardData'}


def find_rows(r, data):
    bank = r.syms['treasureDisplayData2'][0]
    found = []
    for name, a, b in sub_tables(r):
        blob = r.rom_at(bank, a, b - a)
        for k in range(0, len(blob) - 6, 7):
            if blob[k:k + 7] == data:
                found.append((name, k // 7))
    return found


def check(r, t, data):
    """'' si l'affichage de t est bon, sinon la raison."""
    rows = find_rows(r, data)
    want = expected_tables(r, t)
    ok = any(n in want for n, _ in rows)
    if ok and want == {'standardData'}:
        ok = data[0] in (t, 0)
    if ok:
        return ''
    return 'affiche %s au lieu de %s' % (
        ', '.join('%s[%d]' % x for x in rows) or 'une ligne inconnue', '/'.join(sorted(want)))


def describe(r, t, data):
    rows = find_rows(r, data)
    return '%s (sprite %02x, texte %02x)' % (
        ', '.join('%s[%d]' % x for x in rows) or '?', data[1], data[6])


def where(inv, t):
    return 'B' if inv[0] == t else 'A' if inv[1] == t else ('case %d' % (inv.index(t) - 2)) if t in inv else 'absent'


# ---- Tests

def test_obtain(game, problems):
    print('== %s : obtention de chaque objet' % game, flush=True)
    r = Runner(game)
    subids = object_subids(r)
    for t in range(1, 0x20):
        if t in NOT_IN_GAME[game]:
            continue
        for subid, param in subids.get(t, []):
            r.reset_inventory()
            r.call('giveTreasure', a=t, c=param)
            r.pb.tick(2, False)
            w = where(r.inventory(), t)
            data = r.display(t)
            line = '%-7s %-16s %02x/%d param %02x  %-7s %s' % (
                game, TREASURE_NAMES.get(t, '?'), t, subid, param, w, describe(r, t, data))
            print(line, flush=True)
            why = check(r, t, data)
            if w == 'absent':
                why = (why + ' ; ' if why else '') + 'pas dans l\'inventaire'
            if why:
                problems.append('%s  <-- %s' % (line, why))
    r.pb.stop(save=False)


LEVEL_ITEMS = (0x01, 0x05, 0x06, 0x0a, 0x16, 0x17)   # bouclier, épée, boomerang, grappin, bracelet, plume


def test_level_zero(game, problems):
    print('== %s : objets à niveaux avec un niveau 0' % game, flush=True)
    r = Runner(game)
    subids = object_subids(r)
    table1 = r.rom_read('treasureDisplayData1', 0x40)
    for t in LEVEL_ITEMS:
        if t in NOT_IN_GAME[game] or not subids.get(t):
            continue
        r.reset_inventory()
        r.call('giveTreasure', a=t, c=subids[t][0][1])
        r.pb.tick(2, False)
        for i in range(0, 0x40, 3):
            if table1[i] == t:
                r.pb.memory[0xc600 + table1[i + 1]] = 0
                break
        data = r.display(t)
        line = '%-7s %-16s %02x niveau 0  %s' % (game, TREASURE_NAMES.get(t, '?'), t, describe(r, t, data))
        print(line, flush=True)
        why = check(r, t, data)
        if why:
            problems.append('%s  <-- %s' % (line, why))
    r.pb.stop(save=False)


def test_round_trip(first, problems):
    print('== aller-retour : objets de %s' % first, flush=True)
    r = Runner(first)
    subids = object_subids(r)
    r.reset_inventory()
    given = []
    for t in range(1, 0x20):
        if t in NOT_IN_GAME[first] or t == 0x0c or not subids.get(t):
            continue
        r.call('giveTreasure', a=t, c=subids[t][0][1])
        r.pb.tick(2, False)
        given.append(t)
    for step in (first, OTHER[first], first):
        if step != r.game:
            r.swap()
        inv = r.inventory()
        for t in given:
            w = where(inv, t)
            if t in NOT_IN_GAME[r.game]:
                line = '%-7s %-16s %02x  %-7s (objet de l\'autre jeu)' % (r.game, TREASURE_NAMES.get(t, '?'), t, w)
                print(line, flush=True)
                continue
            data = r.display(t)
            line = '%-7s %-16s %02x  %-7s %s' % (r.game, TREASURE_NAMES.get(t, '?'), t, w, describe(r, t, data))
            print(line, flush=True)
            why = check(r, t, data)
            if w == 'absent':
                why = (why + ' ; ' if why else '') + 'perdu'
            if why:
                problems.append('aller-retour depuis %s : %s  <-- %s' % (first, line, why))
    r.pb.stop(save=False)


def main():
    problems = []
    for game in ('ages', 'seasons'):
        test_obtain(game, problems)
    for game in ('ages', 'seasons'):
        test_level_zero(game, problems)
    for game in ('ages', 'seasons'):
        test_round_trip(game, problems)
    print('\n%d anomalie(s)' % len(problems))
    for p in problems:
        print(p)
    sys.exit(1 if problems else 0)


main()
