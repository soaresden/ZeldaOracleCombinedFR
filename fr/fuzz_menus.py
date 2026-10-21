"""Fuzz des menus : appuie au hasard sur les boutons (menu Start, carte, Select,
raccourci Vasu, suivi des codes, boîte à bagues...) et s'arrête dès qu'un objet
qui n'était pas là apparaît dans l'inventaire (équiper ne fait qu'échanger les
objets entre eux). Affiche alors les dernières actions pour les rejouer.

Usage : python fr/fuzz_menus.py [graine] [nombre d'actions] [rom] [--vasu]
  --vasu : départ dans la boutique de Vasu, avec des bagues à faire estimer
           (dont la n°$17, même numéro que la plume) et la boîte à bagues.
"""
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
STEPS = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
VASU = '--vasu' in sys.argv
sys.argv = [a for a in sys.argv if a != '--vasu']
ROM = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'out', 'zoc-fr.gbc')

sys.argv = ['test_items', ROM]
_src = open(os.path.join(ROOT, 'fr', 'test_items.py'), encoding='utf-8').read().replace('\nmain()\n', '\n')
ns = {'__file__': os.path.join(ROOT, 'fr', 'test_items.py'), '__name__': 'test_items'}
exec(compile(_src, 'test_items.py', 'exec'), ns)

BUTTONS = ['a', 'b', 'start', 'select', 'up', 'down', 'left', 'right']


def main():
    rng = random.Random(SEED)
    r = ns['Runner']('ages')
    m = r.pb.memory
    m[r.addr('wGlobalFlags') + 1] |= 0x04           # menus utilisables
    m[r.addr('wGlobalFlags') + 1] |= 0x01           # boîte à bagues
    r.reset_inventory()
    for t, c in ((0x05, 1), (0x19, 1), (0x16, 1), (0x15, 0), (0x2c, 1), (0x03, 0x10)):
        r.call('giveTreasure', a=t, c=c)
        r.pb.tick(20, False)
    m[r.addr('wNumEmberSeeds')] = 0x17
    m[0xc758] |= 0x10                                 # case de Vasu visitée (raccourci)
    if VASU:
        # Bagues à estimer (bit 6 = pas encore estimée) et boîte à bagues
        for i, ring in enumerate((0x17, 0x05, 0x10, 0x28, 0x17, 0x2a)):
            m[r.addr('wUnappraisedRings') + i] = ring | 0x40
        m[r.addr('wNumUnappraisedRingsBcd')] = 0x06
        m[r.addr('wObtainedRingBox')] = 1
        m[r.addr('wRingBoxLevel')] = 1
        r.run('w10,pselect,w120')
        m[0xcbb6] = 0x58
        r.run('w10,pa,w90,pa,w40,pa,w300')
    inv = r.addr('wInventoryB')
    start = sorted(m[inv + i] for i in range(22))
    print('inventaire de départ', ' '.join('%02x' % x for x in start if x), flush=True)
    history = []
    for n in range(STEPS):
        b = rng.choice(BUTTONS)
        # Menu SAUVER : toujours « Continuer » (sinon retour au titre, faux positif)
        if m[r.addr('wOpenedMenuType')] == 0x03:
            # « Continuer » ou « Sauv. & Continuer », jamais « Sauv. & Quitter »
            if m[0xcbb5] > 1:
                m[0xcbb5] = rng.choice((0, 1))
            if b in ('up', 'down'):
                b = 'a'
        wait = rng.choice((2, 5, 10, 20, 40, 90))
        r.pb.button(b, 3)
        r.pb.tick(wait, False)
        history.append('p%s,w%d' % (b, wait))
        game = 'seasons' if m[0xc4bd] == 1 else 'ages'
        if game != r.game:
            r.set_game(game)
            inv = r.addr('wInventoryB')
            history.append('[%s]' % game)
        now = sorted(m[inv + i] for i in range(22))
        if now != start:
            print('!! inventaire modifié après %d actions' % (n + 1))
            print('   avant :', ' '.join('%02x' % x for x in start if x))
            print('   après :', ' '.join('%02x' % x for x in now if x))
            print('   menu %02x état %02x/%02x sous-état %02x  cbb6=%02x' % (
                m[r.addr('wOpenedMenuType')], m[r.addr('wMenuLoadState')], m[r.addr('wMenuActiveState')],
                m[r.addr('wSubmenuState')], m[0xcbb6]))
            print('   dernières actions :', ','.join(history[-40:]))
            sys.exit(1)
    print('rien après %d actions (graine %d)' % (STEPS, SEED))


main()
