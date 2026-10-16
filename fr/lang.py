"""Langue de la ROM générée, commune aux scripts fr/*.py.

Les ROMs Europe contiennent 5 langues, dans cet ordre (et non celui du nom de
fichier En,Fr,De,Es,It) : anglais, français, allemand, italien, espagnol.

Choix : argument --lang=xx, sinon variable d'environnement ZOC_LANG, sinon fr.
"""
import os
import sys

LANGS = {'en': 0, 'fr': 1, 'de': 2, 'it': 3, 'es': 4}


def current():
    """(code, index dans les ROMs EU), ex. ('de', 2)"""
    code = os.environ.get('ZOC_LANG', 'fr')
    for arg in sys.argv[1:]:
        if arg.startswith('--lang='):
            code = arg.split('=', 1)[1]
    if code not in LANGS:
        sys.exit('Langue inconnue : %s (choix : %s)' % (code, ', '.join(LANGS)))
    return code, LANGS[code]
