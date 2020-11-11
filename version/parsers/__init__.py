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
