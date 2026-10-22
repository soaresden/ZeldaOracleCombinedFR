"""Test automatique du suivi 100 % (menu Complétion) et des cœurs sur la carte,
dans les deux jeux (PyBoy).

Dans une nouvelle partie, le test met des drapeaux connus (quarts de cœur,
réceptacles, essences, bagues, quête d'échange), puis :
1. ouvre le menu (Start, 3e page, A sur les quarts de cœur) et vérifie le
   total fait (wFrCompDone) ;
2. ouvre la liste de chaque catégorie et vérifie le nombre de choses qui
   manquent et les lignes affichées (wFrCompRowEntries), pages comprises ;
3. ouvre la carte et compte les cœurs (sprites $6c) : un par quart pas pris
   sur cette carte.
Des captures sont enregistrées dans out/test_completion/.

Usage : python fr/test_completion.py [rom]   (par défaut out/zoc-fr.gbc)
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_items as ti
from make_completion import HEARTS, CONTAINERS, ESSENCES, RINGS, TRADE

OUT = os.path.join(ti.ROOT, 'out', 'test_completion')
TO_MENU = 'w10,pstart,w60,pselect,w60,pselect,w60,pright,w10,pdown,w20,pa,w150'
ROWS = 11
HEART_TILE = 0x6c

# Drapeaux mis par le test : indices dans les tables de make_completion
SET_HEARTS = (0, 3, 10)        # deux quarts fixes + la noix Gasha
SET_CONTAINERS = (0, 2, 5)
SET_ESSENCES = (0, 1)
SET_RINGS = (0, 1, 9, 40, 63)
TRADE_HELD = 3                 # objet d'échange 3 en main : objets 0 à 3 obtenus


def flag_entries(game):
    """Par catégorie : liste de (adresse, masque)"""
    hearts = [(a, msk) for a, msk, *_ in HEARTS[game]]
    containers = [(a, 0x20) for a in CONTAINERS[game]]
    essences = [(ESSENCES[game], 1 << k) for k in range(8)]
    rings = [(RINGS + (i >> 3), 1 << (i & 7)) for i in range(64)]
    return hearts, containers, essences, rings


def setup(r):
    m = r.pb.memory
    for name in ('wMenuDisabled', 'wDisabledObjects', 'wDisableLinkCollisionsAndMenu'):
        if name in r.syms:
            m[r.addr(name)] = 0
    m[r.addr('wGlobalFlags') + 1] |= 0x04   # GLOBALFLAG_INTRO_DONE ($0a) : Start et Select utilisables
    hearts, containers, essences, rings = flag_entries(r.game)
    for table, chosen in ((hearts, SET_HEARTS), (containers, SET_CONTAINERS),
                          (essences, SET_ESSENCES), (rings, SET_RINGS)):
        for i in chosen:
            a, msk = table[i]
            m[a] |= msk
    m[r.addr('wTradeItem')] = TRADE_HELD
    m[r.addr('wObtainedTreasureFlags') + 8] |= 0x02   # TREASURE_TRADEITEM ($41)


def open_completion(r):
    r.run(TO_MENU)   # le vrai chemin : Start, 3e page, A sur les quarts de cœur


def open_map(r):
    r.run('pselect,w150')


def far_call(r, func, a=0):
    """Appelle une routine d'une autre banque entre deux images (la banque est
    choisie à la main : interBankCall écraserait A) ; renvoie (a, b, c)."""
    pb, st = r.pb, {'armed': True, 'done': False}
    bank, addr = r.syms[func]

    def inject(_):
        if not st['armed']:
            return
        st['armed'] = False
        g = pb.register_file
        st['saved'] = (g.SP, g.PC, g.A, g.F, g.B, g.C, g.D, g.E, g.HL)
        g.SP -= 2
        pb.memory[g.SP] = ti.SENTINEL & 0xff
        pb.memory[g.SP + 1] = ti.SENTINEL >> 8
        st['bank'] = pb.memory[0xff97]
        pb.memory[0xff97] = bank
        pb.memory[0x2222] = bank
        g.A = a
        g.PC = addr

    def back(_):
        g = pb.register_file
        st['out'] = (g.A, g.B, g.C)
        pb.memory[0xff97] = st['bank']
        pb.memory[0x2222] = st['bank']
        g.SP, g.PC, g.A, g.F, g.B, g.C, g.D, g.E, g.HL = st['saved']
        st['done'] = True

    pb.hook_register(0, r.addr('_mainLoop_nextThread'), inject, None)
    pb.hook_register(0, ti.SENTINEL, back, None)
    for _ in range(60):
        pb.tick(1, False)
        if st['done']:
            break
    pb.hook_deregister(0, r.addr('_mainLoop_nextThread'))
    pb.hook_deregister(0, ti.SENTINEL)
    assert st['done'], func
    return st['out']


def test_routines(r, problems, expected_done):
    """Seasons : l'intro de la partie liée bloque les menus dans PyBoy ; on appelle
    les routines du menu (mêmes que dans Ages, testées par l'écran) pour vérifier
    les données et les adresses propres à Seasons."""
    game = r.game
    far_call(r, 'frCompletion_prepare')
    names = ['quarts', 'receptacles', 'essences', 'bagues', 'echange']
    sizes = [len(HEARTS[game]), len(CONTAINERS[game]), 8, 64, len(TRADE[game])]
    for k in range(5):
        _, total, done = far_call(r, 'frComp_countCategory', a=k)
        check(problems, (total, done) == (sizes[k], expected_done[k]),
              '%s : %s %d/%d (attendu %d/%d)' % (game, names[k], done, total, expected_done[k], sizes[k]))


def state(r):
    m = r.pb.memory
    return dict(mode=m[0xcbb4], num=m[0xcbb5], cursor=m[0xcbb6], done=m[0xc5a2], page=m[0xc582],
                rows=[m[0xc583 + i] for i in range(ROWS)])


def shot(r, name):
    r.pb.tick(1, True)
    os.makedirs(OUT, exist_ok=True)
    r.pb.screen.image.convert('RGB').resize((320, 288), Image.NEAREST).save(
        os.path.join(OUT, '%s_%s.png' % (r.game, name)))


def check(problems, ok, label):
    print('%-60s %s' % (label, 'ok' if ok else '<-- ANOMALIE'), flush=True)
    if not ok:
        problems.append(label)


def test_game(game, problems):
    print('\n=== %s ===' % game, flush=True)
    if game == 'ages':
        r = ti.Runner(game)
    else:
        # L'intro de Seasons reste bloquée dans PyBoy : on passe par la porte de Vasu
        r = ti.Runner('ages')
        r.pb.memory[r.addr('wGlobalFlags') + 1] |= 0x04
        r.swap()
        r.run('w300')
    setup(r)
    trade_done = TRADE_HELD + 1
    if game == 'seasons':
        test_routines(r, problems, [len(SET_HEARTS), len(SET_CONTAINERS), len(SET_ESSENCES),
                                    len(SET_RINGS), trade_done])
        r.pb.stop(save=False)
        return
    open_completion(r)
    st = state(r)
    shot(r, 'resume')
    expected = len(SET_HEARTS) + len(SET_CONTAINERS) + len(SET_ESSENCES) + len(SET_RINGS) + trade_done
    check(problems, st['mode'] == 0 and st['num'] == 7, '%s : résumé ouvert (7 lignes)' % game)
    check(problems, st['done'] == expected, '%s : total fait %d (attendu %d)' % (game, st['done'], expected))

    sizes = [len(HEARTS[game]), len(CONTAINERS[game]), 8, 64, len(TRADE[game])]
    chosen = [SET_HEARTS, SET_CONTAINERS, SET_ESSENCES, SET_RINGS, range(trade_done)]
    names = ['quarts', 'receptacles', 'essences', 'bagues', 'echange']
    for k in range(5):
        missing = [i for i in range(sizes[k]) if i not in chosen[k]]
        # Aller sur la ligne k et ouvrir la liste
        r.run('pdown,w20,' * k + 'pa,w150')
        pages = []
        while True:
            st = state(r)
            pages += [x for x in st['rows'] if x != 0xff]
            shot(r, '%s_page%d' % (names[k], st['page'] // ROWS + 1))
            if st['page'] + ROWS >= len(missing):
                break
            r.run('pright,w150')
        check(problems, st['mode'] == k + 1, '%s : liste %s ouverte' % (game, names[k]))
        check(problems, st['done'] == len(missing),
              '%s : %s, %d manquants (attendu %d)' % (game, names[k], st['done'], len(missing)))
        check(problems, pages == missing, '%s : %s, lignes = ce qui manque, dans l\'ordre' % (game, names[k]))
        r.run('pb,w150')
        st = state(r)
        check(problems, st['mode'] == 0, '%s : B revient au résumé' % game)

    # Carte : un cœur par quart fixe pas pris sur cette carte (mode 0)
    r.run('pb,w150')
    open_map(r)
    m = r.pb.memory
    most = 0
    for _ in range(40):
        r.pb.tick(1, False)
        n = sum(1 for i in range(40) if m[0xfe00 + 4 * i + 2] == HEART_TILE and 16 < m[0xfe00 + 4 * i] < 160)
        most = max(most, n)
    shot(r, 'carte')
    expected_hearts = sum(1 for i, (a, msk, mp, *_) in enumerate(HEARTS[game])
                          if mp == m[0xcbb3] and i not in SET_HEARTS)
    check(problems, most == expected_hearts,
          '%s : %d cœurs sur la carte (attendu %d)' % (game, most, expected_hearts))
    r.pb.stop(save=False)


def main():
    problems = []
    for game in ('ages', 'seasons'):
        test_game(game, problems)
    print('\n%d anomalie(s)' % len(problems))
    for p in problems:
        print(p)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
