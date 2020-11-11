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
from typing import Iterable, Optional, Tuple, List, Any, Generator, TYPE_CHECKING

from lark.lexer import Token

if TYPE_CHECKING:
    from version.parsers.title.item import TokenOrItem


def flatten_strings(args: Iterable[TokenOrItem], types_considered: Optional[Iterable[str]] = ('STRING', 'RAW_STRING')) \
        -> Tuple[str, List[Tuple[int, TokenOrItem]]]:
    """
    Returns all tokens' value, whose type is in types_considered joined as one string, and a list of tuples of
    Objects with its original index in args.

    types_considered: Must be an iterable of strings, which token.type will be considered to be a string.
                      Or None in which case every token will be considered a string.
    """
    strs = []
    others = []
    for i, arg in enumerate(args):
        if isinstance(arg, Token) and (types_considered is None or arg.type in types_considered):
            strs.append(arg)
        else:
            others.append((i, arg))

    return ' '.join(map(str, strs)), others


def flatten_strings_no_index(args: Iterable[TokenOrItem],
                             types_considered: Optional[Iterable[str]] = ('STRING', 'RAW_STRING')) \
        -> Tuple[str, Generator[Any, None, None]]:
    s, others = flatten_strings(args, types_considered=types_considered)
    return s, (o for _, o in others)


def text_contents(args: Iterable[TokenOrItem]) -> str:
    """
    Returns all STRING tokens' value joined as one string.
    """
    s, _ = flatten_strings(args)
    return s


def contents_as_string(args: Iterable[TokenOrItem]) -> str:
    """
    Returns all tokens' value (regardless of their type) joined as one string.
    """
    s, _ = flatten_strings(args, types_considered=None)
    return s