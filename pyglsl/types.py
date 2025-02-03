# Purely pythonic fast first-rate fully-functioning flexible feature-rich framework for fun
#
# Copyright (C) 2016 Nicholas Bishop
# Copyright (C) 2025 George Watson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ast
import attr
from typing import SupportsAbs, SupportsInt, SupportsFloat, TypeVar, Generic

class GlslType(SupportsAbs, SupportsInt, SupportsFloat):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, name) -> 'GlslType':
        return GlslType(self, name)

    def __getitem__(self, index) -> 'GlslType':
        return GlslType(self, index)

    def __setitem__(self, index, val) -> 'GlslType':
        return GlslType(self, index, val)

    def __abs__(self) -> 'GlslType':
        return GlslType(self)

    def __add__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __sub__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __mul__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __truediv__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __int__(self):
        pass

    def __float__(self):
        pass

GlslArrayElem = TypeVar('GlslArrayElem')
class GlslArray(Generic[GlslArrayElem]):
    def __init__(self, gtype):
        pass

    def __getitem__(self, index):
        return GlslType(self, index)

    def __setitem__(self, index, val):
        return GlslType(self, index, val)

@attr.s
class ArraySpec(object):
    """Represents an array declaration.

    This type isn't currently intended to be used by client code
    directly, it's just a convenient form for internal use.
    """

    element_type = attr.ib()
    length = attr.ib()

    @classmethod
    def from_ast_node(cls, node):
        """Create a GlslArray from an AST node if possible.

        If the node cannot be converted then None is returned.
        """
        if not isinstance(node, ast.Subscript):
            return None
        if not isinstance(node.value, ast.Name):
            return None
        name = node.value.id
        prefix = 'Array'
        if not name.startswith(prefix):
            return None
        try:
            num = int(name[len(prefix):])
        except ValueError:
            return None
        if not isinstance(node.slice, ast.Name):
            return None
        gtype = node.slice.id
        return cls(gtype, num)
