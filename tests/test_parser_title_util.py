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

from typing import List, Any, TYPE_CHECKING

from lark import Token

if TYPE_CHECKING:
    from version.parsers.title.item import TokenOrItem
from version.parsers.title.title import ParenthesizedItem, CirclePlusArtistItem, ConventionItem
from version.parsers.title.util import flatten_strings


def new_stoken(s: str) -> Token:
    return Token('STRING', s)


def new_pitem(tks: List[TokenOrItem], paren: str = '(') -> ParenthesizedItem:
    tks.insert(0, Token('LPAREN', paren))
    return ParenthesizedItem(tks)


def test_flatten_strings():
    pitem = new_pitem([new_stoken('artistName')])
    convi = ConventionItem([new_pitem([new_stoken('C80')])])
    cplusa = CirclePlusArtistItem([new_stoken('circleName'), pitem])
    tks = [
        new_stoken('Hello'),
        cplusa,
        convi,
        new_stoken('World')
    ]
    s, others = flatten_strings(tks)
    assert s == 'Hello World'
    assert [o for _, o in others] == [cplusa, convi]
