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
import attrs
from .parse import parse

def _gdecl(*parts):
    not_none = (part for part in parts if part is not None)
    return '{};'.format(' '.join(not_none))

def location_str(location):
    if location is None:
        return None
    else:
        return 'layout(location={})'.format(int(location))

@attr.s
class GlslVar(object):
    """Represent a GLSL variable declaration (or struct member)."""

    name = attr.ib()
    gtype = attr.ib()
    interpolation = attr.ib(default=None)

    def declare(self):
        return _gdecl(self.interpolation, self.gtype, self.name)

    def declare_uniform(self):
        return _gdecl('uniform', self.gtype, self.name)

    def declare_attribute(self, location=None):
        return _gdecl(location_str(location), self.interpolation,
                      'in', self.gtype, self.name)

    def declare_output(self, location=None):
        return _gdecl(self.interpolation, location_str(location),
                      'out', self.gtype, self.name)

def snake_case(string):
    output = ''
    first = True
    for char in string:
        lower = char.lower()
        if char != lower:
            if first:
                first = False
            else:
                output += '_'
        output += lower
    return output


def _declare_block(block_type, block_name, instance_name, members,
                   array):
    # TODO
    assert len(members) != 0
    assert block_type in ('in', 'out', 'uniform')

    array_string = ''
    if array is not None:
        if isinstance(array, bool):
            array_string = '[]'
        else:
            raise NotImplementedError('only unsized arrays are supported')

    yield '{} {} {{'.format(block_type, block_name)

    for member in members:
        # TODO
        assert not member.name.startswith('gl_')
        yield '    ' + member.declare()

    yield '}} {}{};'.format(instance_name, array_string)


# https://www.opengl.org/wiki/Interface_Block_(GLSL)
class ShaderInterface(object):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_vars(cls):
        # ast is used here instead of inspecting the attributes
        # directly because currently most of the types are just
        # aliases of GlslType rather than subclasses
        src = parse(cls)
        cls_node = src.body[0]
        for item in cls_node.body:
            if isinstance(item, ast.Assign):
                name = item.targets[0].id
                # Ignore builtins
                if name.startswith('gl_'):
                    continue
                if not isinstance(item.value, ast.Call):
                    raise TypeError('member is not a constructor: {}'
                                    .format(ast.dump(item)))
                gtype = item.value.func.id
                interp = None
                if len(item.value.args) == 1:
                    interp = item.value.args[0].id
                yield GlslVar(name, gtype, interpolation=interp)

    @classmethod
    def _declare_block(cls, instance_name, block_type, array=None):
        members = list(cls.get_vars())
        if len(members) == 0:
            return []
        else:
            return list(_declare_block(block_type, cls.block_name(),
                                       instance_name, members, array))

    @classmethod
    def declare_input_block(cls, instance_name, array=None):
        return cls._declare_block(instance_name, 'in', array=array)

    @classmethod
    def declare_output_block(cls, array=None):
        instance_name = snake_case(cls.instance_name())
        return cls._declare_block(instance_name, 'out', array=array)

    @classmethod
    def block_name(cls):
        return cls.__name__

    @classmethod
    def instance_name(cls):
        return snake_case(cls.__name__)


class UniformBlock(ShaderInterface):
    @classmethod
    def declare_input_block(cls, instance_name, array=None):
        if array is not None:
            raise NotImplementedError('uniform arrays not implemented')

        for member in cls.get_vars():
            yield member.declare_uniform()


class AttributeBlock(ShaderInterface):
    # For whatever reason GLSL doesn't allow attributes to be
    # aggregated into an interface block
    @classmethod
    def declare_input_block(cls, instance_name=None, array=None):
        if array is not None:
            raise NotImplementedError('attribute arrays not implemented')

        location = 0
        for member in cls.get_vars():
            # TODO(nicholasbishop): correctly handle type size when
            # incrementing location
            yield member.declare_attribute(location)
            location += 1


class FragmentShaderOutputBlock(ShaderInterface):
    # As with attributes, blocks aren't allowed here
    @classmethod
    def declare_output_block(cls, array=None):
        if array is not None:
            raise NotImplementedError('fs output arrays not implemented')

        # TODO(nicholasbishop): dedup
        location = 0
        for member in cls.get_vars():
            # TODO(nicholasbishop): correctly handle type size when
            # incrementing location
            yield member.declare_output(location)
            location += 1
