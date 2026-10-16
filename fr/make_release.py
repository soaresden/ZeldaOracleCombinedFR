"""Paquet de publication (romhacking.net) : captures d'écran en taille réelle
(docs/screenshots/, en ligne sur GitHub Pages) et zip avec les patchs BPS, le lisez-moi et les
scripts qui collent les deux ROMs (out/release/).

Les captures sont faites dans la version anglaise (out/zoc-en.gbc, compilée
par build_all.sh), avec PyBoy comme fr/make_previews.py.

Usage : python fr/make_release.py [version]
"""
import json
import os
import sys
import zipfile

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join(ROOT, 'romhacking')
SHOTS = os.path.join(ROOT, 'docs', 'screenshots')
OUT = os.path.join(ROOT, 'out', 'release')
VERSION = sys.argv[1] if len(sys.argv) > 1 else '1.0'
OPTIONS = {o['id']: int(o['offset'], 16) for o in
           json.load(open(os.path.join(ROOT, 'fr', 'options.json'), encoding='utf-8'))['options']}

# Séquences (voir fr/make_previews.py)
BOOT = 'w1300,pstart,w150'
NEW_AGES = BOOT + ',pstart,w150,pa,w60,pa,w60,pa,w20,pa,w20,pstart,w30,pa,w90,pa,w60,pa,w200' + ',pa,w50' * 30
TO_VASU = 'oc6d1=04,oc758=10,mcbca=00,mcc02=00,w30,pselect,w120,mcbb6=58,w10,pa,w90,pa,w40,pa,w300'
EQUIP = 'mc684=01,mc685=05,mc6af=01,mc6b2=01,oc69a=22,mcbe9=ff,w30'
TO_TRACKER = ('oc6d1=04,oc6d2=10,m4000=00,oa676=70,oa677=40,m4000=01,oc6dd=c0,'
              'mcbca=00,mcc02=00,w10,pstart,w60,pselect,w60,pselect,w60,pright,w10,pa,w90,pdown,w20,pdown,w40')
MAP_REWARD = 'oc6d1=04,oc6d2=10,m4000=00,oa676=40,m4000=01,mcbca=00,mcc02=00,w30,pselect,w90'
TO_GBA_SHOP = ('oc6d1=04,oc758=10,mcbca=00,mcc02=00,w30,pselect,w120,mcbb6=58,w10,pa,w90,pa,w40,pa,'
               'w3,mcc47=81,mcc48=58,mcc4a=45,w300,hup:40,w150')


class Game:
    def __init__(self, opts):
        rom = bytearray(open(os.path.join(ROOT, 'out', 'zoc-en.gbc'), 'rb').read())
        for opt, on in opts.items():
            rom[OPTIONS[opt]] = 1 if on else 0
        tmp = os.path.join(ROOT, 'out', 'release_tmp.gbc')
        open(tmp, 'wb').write(rom)
        self.pb = PyBoy(tmp, window='null', cgb=True, sound_emulated=True, sound_volume=0)
        self.pb.set_emulation_speed(0)

    def run(self, steps):
        pb = self.pb
        for step in steps.split(','):
            if not step:
                continue
            if step[0] == 'w':
                pb.tick(int(step[1:]), False)
            elif step[0] == 'p':
                pb.button(step[1:], 4)
                pb.tick(12, False)
            elif step[0] == 'h':
                b, n = step[1:].split(':')
                pb.button_press(b)
                pb.tick(int(n), False)
                pb.button_release(b)
                pb.tick(2, False)
            elif step[0] in 'mo':
                a, v = step[1:].split('=')
                a, v = int(a, 16), int(v, 16)
                pb.memory[a] = v if step[0] == 'm' else pb.memory[a] | v
        return self

    def wait_press_start(self):
        for _ in range(64):
            self.pb.tick(1, False)
            if not self.pb.memory[0xcbb3] & 0x20:
                break
        return self

    def shot(self, name):
        self.pb.tick(1, True)
        self.pb.screen.image.convert('RGB').save(os.path.join(SHOTS, name + '.png'), optimize=True)
        print(name)
        self.pb.stop(save=False)


def screenshots():
    os.makedirs(SHOTS, exist_ok=True)
    Game({}).run(BOOT).wait_press_start().shot('1-title')
    Game({}).run(BOOT + ',pstart,w150,pa,w60').shot('2-new-game-ages-or-seasons')
    Game({'hud_bottom': True}).run(NEW_AGES + ',' + EQUIP).shot('3-status-bar-at-the-bottom')
    Game({}).run(NEW_AGES + ',' + TO_VASU).shot('4-vasu-doors-to-each-game')
    Game({}).run(NEW_AGES + ',' + TO_TRACKER).shot('5-secrets-tracker')
    Game({}).run(NEW_AGES + ',' + MAP_REWARD).shot('6-reward-markers-on-the-map')
    Game({'gba_shop': True}).run(NEW_AGES + ',' + TO_GBA_SHOP).shot('7-advance-shop')
    os.remove(os.path.join(ROOT, 'out', 'release_tmp.gbc'))


def package():
    os.makedirs(OUT, exist_ok=True)
    name = os.path.join(OUT, 'ZeldaOraclesCombined-v%s.zip' % VERSION)
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
        for lang in ('en', 'fr', 'de', 'it', 'es'):
            z.write(os.path.join(ROOT, 'docs', 'patches', lang + '.bps'),
                    'Zelda Oracles Combined (%s).bps' % lang.upper())
        for f in ('readme.txt', 'join_roms.bat', 'join_roms.sh'):
            z.write(os.path.join(REL, f), f)
    print(name, os.path.getsize(name))


if '--no-shots' not in sys.argv:
    screenshots()
package()
