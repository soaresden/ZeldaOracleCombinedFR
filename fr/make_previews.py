"""Captures d'aperçu de la page web : pour chaque option, l'écran du jeu avec
l'option activée et désactivée (docs/previews/<option>_<on|off>[_<langue>].png).
Les écrans avec du texte sont faits dans chaque langue.

Joue les ROMs out/zoc-<langue>.gbc dans PyBoy (pip install pyboy), en forçant
l'octet de l'option à 1 ou 0. Il faut le son émulé, sinon le jeu boucle sur un
registre audio après le logo Capcom.

Usage : python fr/make_previews.py [en fr de it es]
"""
import json
import os
import re
import sys

from PIL import Image
from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'previews')
OPTIONS = {o['id']: int(o['offset'], 16) for o in
           json.load(open(os.path.join(ROOT, 'fr', 'options.json'), encoding='utf-8'))['options']}
SYMS = {}
for line in open(os.path.join(ROOT, 'oracles-disasm', 'ages.sym')):
    m = re.match(r'([0-9a-f]{2}):([0-9a-f]{4}) (\S+)', line)
    if m:
        SYMS[m.group(3)] = int(m.group(2), 16)

# Séquences de boutons (voir les tests de la session) : wN = attendre N images,
# pX = appuyer sur X, hX:N = maintenir X pendant N images, mADDR=V / oADDR=V = poke.
BOOT = 'w1300,pstart,w150'
NEW_AGES = BOOT + ',pstart,w150,pa,w60,pa,w60,pa,w20,pa,w20,pstart,w30,pa,w90,pa,w60,pa,w200' + ',pa,w50' * 30
TO_VASU = ('oc6d1=04,oc758=10,mcbca=00,mcc02=00,w30,pselect,w120,mcbb6=58,w10,pa,w90,pa,w40,pa,w300')
MAP_ON_VASU = 'oc6d1=04,oc758=10,mcbca=00,mcc02=00,w30,pselect,w120,mcbb6=58,w10,pa,w200'
# Ages fini (FINISHEDGAME) et code de Troy commencé dans la sauvegarde Seasons
# (SRAM banque 0) : un marqueur sur la case de Troy (0:1d)
MAP_REWARD = 'oc6d1=04,oc6d2=10,m4000=00,oa676=40,m4000=01,mcbca=00,mcc02=00,w30,pselect,w90'


class Game:
    def __init__(self, rom_path, opts):
        rom = bytearray(open(rom_path, 'rb').read())
        for opt, on in opts.items():
            rom[OPTIONS[opt]] = 1 if on else 0
        tmp = os.path.join(ROOT, 'out', 'preview_tmp.gbc')
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

    def shot(self, name):
        self.pb.tick(1, True)
        im = self.pb.screen.image.convert('RGB').resize((320, 288), Image.NEAREST)
        im.save(os.path.join(OUT, name + '.png'), optimize=True)
        print(name)
        return self

    def wait_title_press_start(self):
        # « PRESS START » clignote : attendre qu'il soit affiché
        for _ in range(64):
            self.pb.tick(1, False)
            if not self.pb.memory[0xcbb3] & 0x20:
                break
        return self

    def open_secret_menu(self):
        """Ouvre l'écran de saisie d'un code (comme un personnage qui en demande un)."""
        pb, state = self.pb, {'armed': True}
        sentinel = 0x3fe8

        def inject(_):
            if not state['armed']:
                return
            state['armed'] = False
            r = pb.register_file
            state['saved'] = (r.SP, r.PC, r.A, r.F)
            r.SP -= 2
            pb.memory[r.SP] = sentinel & 0xff
            pb.memory[r.SP + 1] = sentinel >> 8
            r.A = 0x85
            r.PC = SYMS['openSecretInputMenu']

        def back(_):
            r = pb.register_file
            r.SP, r.PC, r.A, r.F = state['saved']

        pb.hook_register(0, SYMS['_mainLoop_nextThread'], inject, None)
        pb.hook_register(0, sentinel, back, None)
        pb.tick(5, False)
        pb.hook_deregister(0, SYMS['_mainLoop_nextThread'])
        pb.hook_deregister(0, sentinel)
        return self

    def stop(self):
        self.pb.stop(save=False)


def rom(lang):
    return os.path.join(ROOT, 'out', 'zoc-%s.gbc' % lang)


def main(langs):
    os.makedirs(OUT, exist_ok=True)
    base = 'fr' if 'fr' in langs else langs[0]

    # Écrans sans texte : une seule langue
    for on in (True, False):
        suffix = 'on' if on else 'off'
        g = Game(rom(base), {'title_combined': on}).run(BOOT).wait_title_press_start()
        g.shot('title_combined_' + suffix).stop()
        g = Game(rom(base), {'hud_game_icon': on}).run(NEW_AGES).shot('hud_game_icon_' + suffix)
        g.stop()
        g = Game(rom(base), {'door_icons': on}).run(NEW_AGES + ',' + TO_VASU).shot('door_icons_' + suffix)
        g.stop()
        g = Game(rom(base), {'reward_markers': on}).run(NEW_AGES + ',' + MAP_REWARD).shot('reward_markers_' + suffix)
        g.stop()

    # Écrans avec du texte : dans chaque langue
    for lang in langs:
        for on in (True, False):
            suffix = ('on' if on else 'off') + '_' + lang
            g = Game(rom(lang), {'vasu_shortcut': on}).run(NEW_AGES + ',' + MAP_ON_VASU)
            g.shot('vasu_shortcut_' + suffix).stop()
        # Avertissement : dernière page de la question (une page de plus en DE/IT/ES)
        extra = ',pa,w300' if lang in ('de', 'it', 'es') else ''
        g = Game(rom(lang), {'linked_warning': True}).run(
            NEW_AGES + ',' + TO_VASU + ',hright:22,hdown:60,w250,pa,w250,pa,w300' + extra)
        g.shot('linked_warning_on_' + lang).stop()
        # Écran de saisie d'un code (ce qu'on évite avec les codes automatiques)
        g = Game(rom(lang), {}).run(NEW_AGES).open_secret_menu().run('w120')
        g.shot('auto_secrets_off_' + lang).stop()
    # Sans avertissement : on arrive directement dans l'intro de la partie liée
    g = Game(rom(base), {'linked_warning': False}).run(
        NEW_AGES + ',' + TO_VASU + ',hright:22,hdown:60,w600,pa,w60,pa,w60')
    g.shot('linked_warning_off').stop()
    os.remove(os.path.join(ROOT, 'out', 'preview_tmp.gbc'))


main(sys.argv[1:] or ['en', 'fr', 'de', 'it', 'es'])
