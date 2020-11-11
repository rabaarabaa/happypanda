# """
# This file is part of Happypanda.
# Happypanda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Happypanda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Happypanda.  If not, see <http://www.gnu.org/licenses/>.
# """

from typing import Optional, Callable

from lark import Lark, UnexpectedToken, UnexpectedInput

from version.parsers import load_lark_grammar
from version.parsers.title.title import TitleTransformer, Title

grammar_options = {
    'regex': True,
    'start': 'start',
    'parser': 'lalr',
    'transformer': TitleTransformer()
}
parser: Lark = load_lark_grammar('title_grammar.lark', **grammar_options)


# noinspection PyTypeChecker
def _parse(text: str, start: Optional[str] = None,
           on_error: Optional[Callable[[UnexpectedToken], bool]] = None) -> Title:
    return parser.parse(text, start=start, on_error=on_error)


def parse(text: str, dummy: bool = True) -> Title:
    """
    Returns a Title object, that contains information extracted from the text.
    If dummy is True, on parsing error it will return a mostly empty Title object with only the "title" key set to
        the original "text".
    Otherwise it will raise an exception.
    """
    text = text.strip()
    if not text:
        raise ValueError("can't parse a blank string.")

    try:
        return _parse(text)
    except UnexpectedInput as e:
        if dummy:
            return Title.dummy({"title": text})
        else:
            raise ValueError("error on parsing, context: {}".format(e.get_context(text)))



