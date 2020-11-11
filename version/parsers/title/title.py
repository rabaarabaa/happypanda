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

from collections import UserList
from typing import ClassVar, Tuple, Dict, Iterable, Set, List, Any, Optional, Union

from lark import Transformer, Token

from version.parsers.title.item import Item, TokenOrItem
from version.parsers.title.util import text_contents, contents_as_string, flatten_strings, flatten_strings_no_index
from version.utils import normalize_spaces


# HEADS UP: maybe in some parts of the code there's Token where it should be Any
# and some others where it IS Token and can only be Token like in ParenthesizedItem (for now atleast)
# From later: a lot of changes... maybe this is not that true now... since now the transformer combines
# Token and Item


class ParenthesizedItem(UserList, Item):
    """
    Class to replace t_paren_* rules in transformation.
    Subclasses list, and its always a list of Token.
    """
    PARENTHESIS: ClassVar[int] = 0
    SQUARE: ClassVar[int] = 1
    BRACES: ClassVar[int] = 2
    ANGLE: ClassVar[int] = 3  # incredibily rare i know but maybe
    NO_PAREN: ClassVar[int] = 4  # for consitency's sake

    map: ClassVar[Dict[str, int]] = {
        "(": PARENTHESIS,
        "[": SQUARE,
        "{": BRACES,
        "<": ANGLE
    }
    paren_types: ClassVar[Tuple[str, ...]] = ('LPAR', 'RPAR')

    tokens: List[Token]
    data: List[Token]
    type: int
    strict: bool

    @property
    def value(self) -> List[Token]:
        return self.tokens

    @property
    def tokens(self) -> List[Token]:
        return self.data

    def __init__(self, args: List[Token], strict: bool = True) -> None:
        super().__init__()
        Item.__init__(self, args)
        self.type = self.NO_PAREN
        self.strict = strict
        for i, arg in enumerate(args):
            if arg.type == 'LPAR':
                self.type = self.map[arg.type]
            elif arg.type not in self.paren_types:
                self.tokens.append(arg)


class ConventionItem(Item):
    def __init__(self, parenthesized: Union[ParenthesizedItem, Iterable[ParenthesizedItem]]) -> None:
        if isinstance(parenthesized, ParenthesizedItem):
            parenthesized = [parenthesized]
        super().__init__(parenthesized)
        name_item: ParenthesizedItem
        name_item, = parenthesized
        name = name_item.text_contents()
        self._value = name

    @property
    def value(self) -> str:
        return self._value


class CirclePlusArtistItem(Item):
    circle: Optional[str]
    artist: str

    def __init__(self, args: Iterable[TokenOrItem]) -> None:
        super().__init__(args)
        self.circle = None
        maybe_circle, others = flatten_strings(args)
        if others:
            pitem: ParenthesizedItem
            (_, pitem), = others
            self.circle = maybe_circle
            self.artist = pitem.text_contents()
        else:
            self.artist = maybe_circle

    @property
    def value(self) -> Dict[str, Optional[str]]:
        return {
            "artist": self.artist,
            "circle": self.circle
        }


class TitleItem(Item):
    title: str
    alt_title: Optional[str]

    def __init__(self, args: List[TokenOrItem], has_alt_title: bool = False):
        super().__init__(args)
        self.has_alt_title = has_alt_title
        self.alt_title = None

        if has_alt_title:
            l_title = []  # Assume romaji title
            r_title = []  # Assume english title
            i = 0
            for i in range(len(args)):
                arg = args[i]
                if isinstance(arg, Token):
                    if arg.type == 'TK_SEPARATOR':
                        break
                l_title.append(arg)

            for i in range(i + 1, len(args)):
                r_title.append(args[i])

            self.title = text_contents(r_title)
            self.alt_title = text_contents(l_title)
        else:
            self.title = text_contents(args)

    @property
    def value(self):
        return {
            "title": self.title,
            "alt_title": self.alt_title
        }


def _title_prop(s: str):
    def get(self) -> str:
        if s not in self._props:
            raise AttributeError(
                "{} property not implemented in this Title subclass '{}'."
                    .format(s, self.__class__.__name__)
            )

        return self._props[s]

    return property(get)


class Title:
    """
    Base class for every handler to a *_case rule in the grammar should subclass.

    All subclasses have to update their internals dict `_props` to have all and only the keys that are listed in the
    ClassVar `PROPERTIES`.
    """
    PROPERTIES: ClassVar[Tuple[str, ...]] = (
        'title', 'alt_title', 'series', 'artist', 'circle', 'translator', 'language', 'convention', 'extras'
    )
    _PROPERTIES_SET: ClassVar[Set[str, ...]] = set(PROPERTIES)

    __slots__ = ('_props',)

    def __init__(self) -> None:
        self._props = {}

    title = _title_prop('title')
    alt_title = _title_prop('alt_title')
    series = _title_prop('series')
    language = _title_prop('language')
    artist = _title_prop('artist')
    circle = _title_prop('circle')
    translator = _title_prop('translator')
    convention = _title_prop('convention')

    @property
    def extras(self) -> List[str]:
        if 'extras' not in self._props:
            raise AttributeError(
                "'extras' property not implemented in this Title subclass '{}'."
                    .format(self.__class__.__name__)
            )

        return self._props['extras']

    def _update_and_fill_empty(self, upd: Dict, extras: Optional[Iterable[TokenOrItem]] = None) -> None:
        """

        If extras is supplied in upd it must be a list of strings, if supplied in the keyword it must be a object that
        can be flatten to a string. But actually I'm just considering instances of ParenthesizedItem, any other object
        types will be ignored, in the future it may handle Token s too, saa.
        """
        if any(prop not in self._PROPERTIES_SET for prop in upd.keys()):
            raise ValueError(
                'upd argument contains invalid keys: {}.'
                    .format([k for k in upd.keys() if k not in self._PROPERTIES_SET])
            )
        self._props.update(upd)
        not_added = self._PROPERTIES_SET - set(self._props.keys())

        if 'extras' not in not_added and extras:
            raise ValueError("duplicate 'extras' in upd and supplied as keyword.")
        else:
            if extras:
                x: ParenthesizedItem
                self._props['extras'] = [x.text_contents() for x in extras if isinstance(x, ParenthesizedItem)]
            elif extras is None:
                self._props['extras'] = []
            not_added.remove('extras')

        for k in not_added:
            self._props[k] = ''

    def __getitem__(self, item: str) -> str:
        if isinstance(item, str):
            if item in self.PROPERTIES:
                return getattr(self, item)
            else:
                raise ValueError("expected subscript with one of {} got '{}'.".format(self.PROPERTIES, item))
        raise TypeError('subscript of Title must be str.')

    def to_dict(self) -> Dict:
        """Same as `dict(self)`."""
        return dict(self)

    def __iter__(self) -> Iterable[Tuple[str, Union[str, List[str]]]]:
        return iter((attr, getattr(self, attr)) for attr in self.PROPERTIES)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self._props))

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self._props))

    @classmethod
    def dummy(cls, dct: Optional[Dict[str, Union[str, List[str]]]] = None):
        if dct is None:
            dct = {}
        t = cls()
        t._update_and_fill_empty(dct)
        return t


class ArtistCaseTitle(Title):
    """
    Handles artist_case rule.
    At the moment only sets artist and title.
    """

    def __init__(self, tokens: List[Token]):
        super().__init__()

        artist = text_contents(tokens)
        artist = normalize_spaces(artist.replace('-', ''))
        title = contents_as_string(tokens)

        self._update_and_fill_empty({
            "artist": artist,
            "title": title
        })


class FallbackCaseTitle(Title):
    """
    Fallback rule, a rule to be considered a net safety. If the other *_case rules fail, this will ensure that we have
    some basic processing and analysis.

    At the moment only returns the top surface STRINGs as one.
    That means "Artist - somedude (UPDATED November 2018) [ENG]" becomes "Artist - somedude".
    This is open to change.
    """

    # TODO: decide if fallback should include parenthesized items, or just the top most level of strings
    # by top most i mean given a string like
    # Artist - somedude (UPDATED November 2018) [ENG]
    # Anything between any type of parenthesis would be ignored
    # so title would be "Artist - somedude" which might be what we want, or maybe we want it configurable
    def __init__(self, tokens: List[Token]) -> None:
        super().__init__()
        title, extras = flatten_strings_no_index(tokens, types_considered=None)
        self._update_and_fill_empty({
            "title": title
        }, extras=extras)


class DefaultCaseTile(Title):
    def __init__(self, tokens: List[TokenOrItem]) -> None:
        super().__init__()
        default = ''
        title: TitleItem = None
        circl_p_art: CirclePlusArtistItem = None
        conv: Optional[ConventionItem] = None

        # used to be a separate rule
        first = tokens[0]
        if isinstance(first, ParenthesizedItem):
            conv = ConventionItem(first)
            tokens = tokens[1:]

        for tk in tokens:
            if isinstance(tk, CirclePlusArtistItem):
                circl_p_art = tk
            elif isinstance(tk, TitleItem):
                title = tk

        self._update_and_fill_empty({
            "title": title.title,
            "alt_title": title.alt_title if title.has_alt_title else default,
            "convention": conv.value if conv is not None else default,
            "artist": circl_p_art.artist,
            "circle": circl_p_art.circle or default
        }, extras=tokens)


# noinspection PyMethodMayBeStatic
class TitleTransformer(Transformer):

    def default_case(self, tks: List[Any]):
        return DefaultCaseTile(tks)

    def artist_case(self, tks: List[Token]) -> ArtistCaseTitle:
        return ArtistCaseTitle(tks)

    def fallback_case(self, tks: List[Token]) -> FallbackCaseTitle:
        return FallbackCaseTitle(tks)

    def t_paren_strict(self, tks: List[Token]) -> ParenthesizedItem:
        return ParenthesizedItem(tks)

    def t_paren_malformed(self, tks: List[Token]) -> ParenthesizedItem:
        return ParenthesizedItem(tks, strict=False)

    def convention(self, wrapped_paren: List[ParenthesizedItem]) -> ConventionItem:
        return ConventionItem(wrapped_paren)

    def circle_plus_artist(self, tks: List[Token]) -> CirclePlusArtistItem:
        return CirclePlusArtistItem(tks)

    def double_title(self, args: List[Any]) -> TitleItem:
        return TitleItem(args, has_alt_title=True)

    def title(self, args: List[Any]) -> TitleItem:
        first = args[0]
        if isinstance(first, TitleItem):
            return first
        else:
            return TitleItem(args)
