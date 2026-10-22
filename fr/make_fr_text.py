"""Remplace le texte anglais du hack crossworld par la VF officielle des ROMs Europe.

1. Extrait le texte de la langue choisie (fr/lang.py) des deux ROMs EU avec dumpText.py.
2. Chaque texte du hack qui existe dans la ROM EU (même identifiant TX_xxxx)
   prend sa version française.
3. Les textes ajoutés par le hack sont presque tous des copies de textes de
   l'autre jeu (« Vous obtenez la Clé du Dragon ! » dans Seasons, etc.) : on
   retrouve le texte anglais identique dans l'autre jeu et on prend sa VF.
4. Ce qui reste est pris dans fr/manual.yaml (traductions faites à la main).

Usage : python fr/make_fr_text.py   [--lang=fr|en|de|it|es]   (depuis la racine du dépôt)
"""
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lang  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ZOC_DISASM : autre désassemblage (oracles-hud : jeux d'origine séparés, barre du bas seule)
DISASM = os.environ.get('ZOC_DISASM') or os.path.join(ROOT, 'oracles-disasm')
EU_ROMS = {
    'ages': 'Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc',
    'seasons': 'Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc',
}
LANG_CODE, LANG = lang.current()
# Dernier commit de la branche poc/crossworld1 (version anglaise du hack)
# (ZOC_TEXT_BASE : autre commit, ex. 309a2cff pour les jeux d'origine)
CROSSWORLD_COMMIT = os.environ.get('ZOC_TEXT_BASE', '37a4eef3')
GAMES = ('ages', 'seasons')


def dump_french(work):
    """Lance dumpText.py dans un dossier jetable (il écrit dans text/ et precompressed/)."""
    shutil.copytree(os.path.join(DISASM, 'tools'), os.path.join(work, 'tools'))
    for game in GAMES:
        os.makedirs(os.path.join(work, 'text', game))
        os.makedirs(os.path.join(work, 'precompressed', 'text', game))
    for game in GAMES:
        subprocess.run([sys.executable, 'tools/dump/dumpText.py',
                        os.path.join(ROOT, EU_ROMS[game]), str(LANG)],
                       cwd=work, check=True, stdout=subprocess.DEVNULL)


def git_show(path):
    return subprocess.run(['git', 'show', '%s:%s' % (CROSSWORLD_COMMIT, path)], cwd=DISASM,
                          capture_output=True, text=True, encoding='utf-8', check=True).stdout


def load(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def entries(doc):
    for group in doc['groups']:
        for entry in group['data']:
            yield entry


def names(entry):
    n = entry['name']
    return n if isinstance(n, list) else [n]


def by_name(doc):
    return {n: e['text'] for e in entries(doc) for n in names(e)}


def dump(doc, path):
    class Dumper(yaml.SafeDumper):
        pass

    def str_repr(dumper, s):
        style = '|' if '\n' in s else None
        return dumper.represent_scalar('tag:yaml.org,2002:str', s, style=style)

    def int_repr(dumper, i):
        return dumper.represent_scalar('tag:yaml.org,2002:int', '0x%02x' % i)

    Dumper.add_representer(str, str_repr)
    Dumper.add_representer(int, int_repr)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# See "text/info.txt" for documentation about this file.\n')
        f.write('# Textes de la ROM Europe (langue %s), voir fr/make_fr_text.py.\n\n' % LANG_CODE)
        yaml.dump(doc, f, Dumper=Dumper, sort_keys=False, allow_unicode=True,
                  width=1000)


def main():
    with tempfile.TemporaryDirectory() as work:
        dump_french(work)
        fr = {g: by_name(load(os.path.join(work, 'text', g, 'text.yaml'))) for g in GAMES}

    us_path = {g: os.path.join(DISASM, 'text', g, 'text.yaml') for g in GAMES}
    # Le texte anglais d'origine est relu dans git : on peut relancer le script.
    us = {g: yaml.safe_load(git_show('text/%s/text.yaml' % g)) for g in GAMES}
    manual_path = os.path.join(ROOT, 'fr', 'manual.yaml')
    manual = load(manual_path) if os.path.exists(manual_path) else {}
    manual = manual or {}

    # texte anglais -> sa VF, calculé avant de toucher aux textes
    en_to_fr = {g: {} for g in GAMES}
    for g in GAMES:
        for e in entries(us[g]):
            for n in names(e):
                if n in fr[g]:
                    en_to_fr[g].setdefault(e['text'], fr[g][n])

    for game in GAMES:
        other = 'seasons' if game == 'ages' else 'ages'
        # d'abord le même jeu (le hack a déplacé des textes vers de nouveaux
        # numéros), puis l'autre jeu
        other_en_to_fr = dict(en_to_fr[other], **en_to_fr[game])

        stats = {'vf': 0, 'texte identique': 0, 'manuel': 0, 'vide': 0}
        missing = []
        for e in entries(us[game]):
            key = next((n for n in names(e) if n in fr[game]), None)
            if key:
                e['text'] = fr[game][key]
                stats['vf'] += 1
            elif e['text'] == '':
                stats['vide'] += 1
            elif e['text'] in other_en_to_fr:
                e['text'] = other_en_to_fr[e['text']]
                stats['texte identique'] += 1
            elif names(e)[0] in manual.get(game, {}):
                e['text'] = manual[game][names(e)[0]]
                stats['manuel'] += 1
            else:
                missing.append((names(e)[0], e['text']))

        # Textes propres à la VF (raccourci vers Vasu…), à la fin de leur groupe
        extras = [] if os.environ.get('ZOC_TEXT_BASE') else load(os.path.join(ROOT, 'fr', 'extra_text.yaml')).get(game, [])
        for extra in extras:
            group = next(g for g in us[game]['groups'] if g['group'] == extra['group'])
            group['data'].append({'name': extra['name'], 'index': 'auto', 'text': extra['text'][LANG_CODE]})
            stats['ajouté'] = stats.get('ajouté', 0) + 1
        dump(us[game], us_path[game])
        print(game, LANG_CODE, stats)
        for n, t in missing:
            print('  A TRADUIRE %s : %r' % (n, t))


main()
