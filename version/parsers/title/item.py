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

from __future__ import annotations
from typing import Iterable, Union, Any

from lark.lexer import Token

from version.parsers.title.util import text_contents


class Item:
    """
    Base class for every helper class to TitleTransformer.

    """

    def __init__(self, args: Iterable[Union[Token, Item]]) -> None:
        self.args = args

    @property
    def value(self) -> Any:
        return self.args

    def text_contents(self) -> str:
        return text_contents(self.args)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.value))

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self.value))


TokenOrItem = Union[Token, Item]
