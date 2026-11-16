"""Seasons d'abord, objets de Seasons, puis Ages (partie liée) :
1. portail du passé sous l'Arbre Mojo une fois l'arbre sauvé (sacoche de Seasons) ;
2. Moosh appelé avec la flûte de Seasons : doit pouvoir être monté ;
3. arbre aux graines mystère après la scène des graines au palais (GLOBALFLAG_0b) :
   pas de garde qui emmène Link.
(Bugs signalés sur romhacking.net en jouant Seasons puis Ages, v1.5.)

Usage : python fr/test_seasons_first.py [rom] [captures.png]
Code de retour 1 s'il y a des anomalies.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:]]
rom = args[0] if args else os.path.join(ROOT, 'out', 'zoc-fr.gbc')
out = args[1] if len(args) > 1 else None
sys.argv = ['x', rom]
sys.path.insert(0, os.path.join(ROOT, 'fr'))
import test_items as T
from PIL import Image

r = T.Runner('seasons')
m = r.pb.memory
subids = T.object_subids(r)
for t in range(1, 0x20):
    if t in T.NOT_IN_GAME['seasons'] or t == 0x0c or not subids.get(t):
        continue
    r.call('giveTreasure', a=t, c=subids[t][0][1])
    r.pb.tick(2, False)
r.call('giveTreasure', a=0x24, c=0x20)   # graines mystère
r.pb.tick(2, False)
m[r.addr('wAnimalCompanion')] = 0x0d     # Moosh, avec sa flûte (comme le jeu la donne)
m[r.addr('wFluteIcon')] = 3
m[r.addr('wMooshState')] |= 0x80
r.swap()
r.run('w30,pa' + ',w30,pa' * 40)
A = lambda n: r.addr(n)
problems = []


def flag(name, n):
    return bool(m[A(name) + (n >> 3)] & (1 << (n & 7)))


def setglobal(n):
    m[A('wGlobalFlags') + (n >> 3)] |= 1 << (n & 7)


print('Ages : liée', m[A('wIsLinkedGame')], 'flûte', m[A('wFluteIcon')], 'compagnon %02x' % m[A('wAnimalCompanion')],
      'wMooshState %02x' % m[A('wMooshState')], 'sacoche', flag('wObtainedTreasureFlags', 0x19),
      'mystère', flag('wObtainedTreasureFlags', 0x24), 'écho', flag('wObtainedTreasureFlags', 0x25))


def warp(group, room, pos=0x55):
    m[0xcc47] = 0x80 | group
    m[0xcc48] = room
    m[0xcc4a] = pos
    m[0xcc49] = 1
    m[0xcc4b] = 3
    r.pb.tick(250, False)


def interactions():
    res = []
    for x in range(16):
        b = 0xd040 + x * 0x100
        if m[b]:
            res.append((m[b + 1], m[b + 2], m[b + 4]))
    return res


shots = []
def shot():
    r.pb.tick(1, True)
    shots.append(r.pb.screen.image.copy().convert('RGB'))


def mount():
    for i in range(10):
        if m[A('wLinkObjectIndex')] == 0xd1:
            break
        dy = m[0xd10b] - m[0xd00b]; dx = m[0xd10d] - m[0xd00d]
        b = ('down' if dy > 0 else 'up') if abs(dy) >= abs(dx) else ('right' if dx > 0 else 'left')
        r.pb.button_press(b); r.pb.tick(20, False); r.pb.button_release(b)
    r.pb.tick(60, False)
    return m[A('wLinkObjectIndex')] == 0xd1


# 1. Portail
setglobal(0x0a)   # intro finie
setglobal(0x12)   # Arbre Mojo sauvé, comme le fait la scène
m[A('wPastRoomFlags') + 0x48] |= 1
m[A('wPresentRoomFlags') + 0x38] &= 0xfe
m[A('wMakuTreeState')] += 1
warp(1, 0x48, 0x57)
shot()
portal = [i for i in interactions() if i[0] == 0xe1]
ok = portal and portal[0][2] == 3
print('1. portail passé -> présent :', portal, 'OUVERT' if ok else 'FERMÉ')
if not ok:
    problems.append('portail fermé')

# 2. Moosh à la flûte
warp(0, 0x48, 0x55)
m[A('wInventoryB')] = 0x0e
r.pb.tick(30, False)
r.pb.button('b', 4)
r.pb.tick(360, False)
shot()
print('2. Moosh arrivé : id %02x état %02x' % (m[0xd101], m[0xd104]))
ok = mount()
shot()
print('   Link sur Moosh :', 'OUI' if ok else 'NON', '(état %02x)' % m[0xd104])
if not ok:
    problems.append('Moosh pas montable')
else:
    # Descendre (A ne fait rien sur Moosh ; on change de salle et on revient à pied)
    r.pb.button('right', 4); r.pb.tick(20, False)
    warp(0, 0x49, 0x55)
    print('   descendu, retenu dans la salle %02x:%02x id %02x' % (
        m[A('wRememberedCompanionGroup')], m[A('wRememberedCompanionRoom')], m[A('wRememberedCompanionId')]))

# 3. Arbre aux graines mystère après la scène du palais
setglobal(0x0b)
warp(1, 0x81, 0x55)
shot()
soldier = [i for i in interactions() if i[0] == 0x40 and i[1] == 0x0a]
print('3. arbre aux graines mystère, garde qui emmène Link :', 'OUI' if soldier else 'non')
if soldier:
    problems.append('garde de l\'arbre aux graines mystère')

if out:
    s = Image.new('RGB', (160 * len(shots), 144))
    for i, im in enumerate(shots):
        s.paste(im, (160 * i, 0))
    s.resize((s.width * 2, 288), Image.NEAREST).save(out)
print('\n%d anomalie(s)' % len(problems))
for p in problems:
    print(p)
r.pb.stop(save=False)
sys.exit(1 if problems else 0)
