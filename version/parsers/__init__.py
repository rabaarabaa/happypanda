import os

from lark import Lark

PARSERS_FOLDER = os.path.abspath(os.path.dirname(__file__))
LARK_GRAMMARS_FOLDER = os.path.join(PARSERS_FOLDER, 'grammars')


def load_lark_grammar(filename: str, **options) -> Lark:
    fp = os.path.join(LARK_GRAMMARS_FOLDER, filename)
    if not os.path.isfile(fp):
        raise FileNotFoundError("Grammar '{}' does not exist in version/parsers/grammars folder.".format(filename))

    with open(fp) as f:
        return Lark(f, **options)
