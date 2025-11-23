# pyglsl -- https://github.com/takeiteasy/pyglsl
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

@attr.s
class StructMember:
    """Represents a member field in a GLSL struct.
    
    This type is used internally to track struct member names and types
    when generating GLSL struct declarations.
    """
    name = attr.ib()
    gtype = attr.ib()

class GlslStruct:
    """Base class for GLSL struct definitions.
    
    Subclass this to define custom GLSL struct types. Members are defined
    as class variables with GLSL type constructors.
    
    Example:
        >>> from pyglsl.glsl import GlslStruct, vec3, float
        >>> class Material(GlslStruct):
        ...     ambient = vec3()
        ...     diffuse = vec3()
        ...     specular = vec3()
        ...     shininess = float()
        >>> 
        >>> # Use in shader:
        >>> def shader():
        ...     mat = Material(
        ...         ambient=vec3(0.2),
        ...         diffuse=vec3(0.8),
        ...         specular=vec3(1.0),
        ...         shininess=float(32.0)
        ...     )
    
    The struct definition will be transpiled to GLSL as:
        struct Material {
            vec3 ambient;
            vec3 diffuse;
            vec3 specular;
            float shininess;
        };
    """
    
    def __init__(self, **kwargs):
        """Initialize struct instance with keyword arguments."""
        pass
    
    @classmethod
    def get_members(cls):
        """Extract struct member definitions from class variables.
        
        Returns:
            List of StructMember objects representing the struct fields.
        """
        from inspect import getsource
        
        # Parse the class definition to extract members
        # This uses the same approach as ShaderInterface.get_vars()
        src_code = getsource(cls)
        try:
            src = ast.parse(src_code)
        except SyntaxError:
            # Fallback for built-in or dynamically created classes
            return []
        
        cls_node = src.body[0]
        if not isinstance(cls_node, ast.ClassDef):
            return []
        
        members = []
        for item in cls_node.body:
            if isinstance(item, ast.Assign):
                name = item.targets[0].id
                if name.startswith('_'):
                    continue
                if not isinstance(item.value, ast.Call):
                    continue
                # Extract type name from the constructor call
                if isinstance(item.value.func, ast.Name):
                    gtype = item.value.func.id
                    members.append(StructMember(name, gtype))
        
        return members
    
    @classmethod
    def struct_name(cls):
        """Get the GLSL struct type name.
        
        Returns:
            The class name to use as the struct name in GLSL.
        """
        return cls.__name__
    
    @classmethod
    def declare_struct(cls):
        """Generate GLSL struct declaration.
        
        Returns:
            List of strings containing the GLSL struct declaration lines.
        """
        lines = [f'struct {cls.struct_name()} {{']
        members = cls.get_members()
        for member in members:
            lines.append(f'    {member.gtype} {member.name};')
        lines.append('};')
        return lines

