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

from dataclasses import dataclass, field
from typing import Callable, Any, Optional, List, Union
from .stage import Stage, GeometryStage

@dataclass
class ShaderDef:
    vertex_shader: Callable[..., Any]
    fragment_shader: Callable[..., Any]
    geometry_shader: Optional[Callable[..., Any]] = None
    version: Optional[Union[str, int]] = "330 core"
    vertex_functions: Optional[List[Callable[..., Any]]] = field(default_factory=list)
    geometry_functions: Optional[List[Callable[..., Any]]] = field(default_factory=list)
    fragment_functions: Optional[List[Callable[..., Any]]] = field(default_factory=list)

    def compile(self):
        """Compile vertex, optional geometry, and fragment shaders.
        
        Returns:
            tuple: (vertex_glsl, fragment_glsl) if no geometry shader,
                   (vertex_glsl, geometry_glsl, fragment_glsl) if geometry shader present
        """
        v = Stage(self.vertex_shader, self.version, self.vertex_functions)
        f = Stage(self.fragment_shader, self.version, self.fragment_functions)
        
        if self.geometry_shader is not None:
            g = GeometryStage(self.geometry_shader, self.version, self.geometry_functions)
            return v.compile(), g.compile(), f.compile(is_fragment=True)
        else:
            return v.compile(), f.compile(is_fragment=True)
