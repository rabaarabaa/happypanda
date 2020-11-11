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

from typing import Callable

from lark import UnexpectedToken
from lark.parsers.lalr_puppet import ParserPuppet

from version.parsers.title import _parse


def _assert_fail_msg(case: str, n: int, s: str) -> str:
    return '{} #{} failed. {}'.format(case, n, repr(s))


def debug_puppet(src: str) -> Callable[[UnexpectedToken], bool]:
    def on_err(e: UnexpectedToken) -> bool:
        puppet: ParserPuppet = e.puppet
        print('HEYO', puppet.pretty(), e.get_context(src), sep='\n')
        return False
    return on_err


def test_inner_parse():
    s = '  Artist   -  Somehoe '
    obj = _parse(s)
    expected = {
        "artist": "Somehoe",
        "title": "Artist - Somehoe",
        "alt_title": "",
        "series": "",
        "circle": "",
        "translator": "",
        "language": "",
        "convention": "",
        "extras": []
    }
    assert dict(obj) == expected, _assert_fail_msg('artist_case', 1, s)

    s = '(C97) [Hai Dai (Hai Tai) Hatsujou '
    obj = _parse(s)
    expected = {
        "artist": "Hai Tai",
        "circle": "Hai Dai",
        "title": "Hatsujou",
        "convention": "C97",
        "alt_title": "",
        "series": "",
        "translator": "",
        "language": "",
        "extras": []
    }
    assert dict(obj) == expected, _assert_fail_msg('default_case', 1, s)

    s = "(Tei 11 Kei Kuchikiiki Shingou no Tame no Doujinshi Kouzu Kai) [K.R's BRST (K.R)] " \
        "Houfeku? Houfeke? 7 (Kyuukao Senjuu he Horseon) [English] {Douhito.com}"
    obj = _parse(s, on_error=debug_puppet(s))
    expected = {
        "artist": "K.R",
        "circle": "K.R's BRST",
        "title": "Houfeku? Houfeke? 7",
        "convention": "Tei 11 Kei Kuchikiiki Shingou no Tame no Doujinshi Kouzu Kai",
        # when the suggested values below become parseable this 'extras' will not have these values
        "extras": ['Kyuukao Senjuu he Horseon', 'English', 'Douhito.com'],
        "alt_title": "",
        "series": "",  # "Kyuukao Senjuu he Horseon"
        "translator": "",  # "Douhito.com"
        "language": ""  # "English"
    }
    assert dict(obj) == expected, _assert_fail_msg('default_case', 2, s)

    s = "(C90) [Fries Fish (Jaka)] Bishoujo Mama Sensei Kaigai Shuuren Nikki | A Big Beautiful Teacher's Abroad " \
        "Training Diary (Bumble Gaal) [English] {Douboro.org}"
    obj = _parse(s, on_error=debug_puppet(s))
    expected = {
        "artist": "Jaka",
        "circle": "Fries Fish",
        "title": "A Big Beautiful Teacher's Abroad Training Diary",
        "alt_title": "Bishoujo Mama Sensei Kaigai Shuuren Nikki",
        "convention": "C90",
        # when the suggested values below become parseable this 'extras' will not have these values
        "extras": ['Bumble Gaal', 'English', 'Douboro.org'],
        "series": "",  # "Bumble Gaal"
        "language": "",  # "English"
        "translator": "",  # "Douboro.org"
    }
    assert dict(obj) == expected, _assert_fail_msg('default_case', 3, s)

    s = "[Chinbachin (chen] Saimin Sister to KimoOta ha Kimoi! | Hypnotizing a Sister Girl Gross A Otaku! " \
        "(Toufuu Project) [English] {Daikoku.jp.com} [Digital]"
    obj = _parse(s, on_error=debug_puppet(s))
    expected = {
        "artist": "chen",
        "circle": "Chinbachin",
        "title": "Hypnotizing a Sister Girl Gross A Otaku!",
        "alt_tile": "Saimin Sister to KimoOta ha Kimoi!",
        "extras": ["Toufuu Project", "English", "Daikoku.jp.com", "Digital"],
        "translator": "",
        "series": "",
        "language": "",
        "convention": ""
    }