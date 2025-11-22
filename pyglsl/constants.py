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

"""Constants used throughout the pyglsl package."""

# Code generation constants
GLSL_INDENT = '    '
GLSL_STATEMENT_TERMINATORS = (';', '{', '}')

# GLSL built-in variable renames (Python convention -> GLSL convention)
GLSL_BUILTIN_RENAMES = {
    'gl_position': 'gl_Position',
    'gl_fragcolor': 'gl_FragColor',
    'gl_fragcoord': 'gl_FragCoord',
    'gl_fragdepth': 'gl_FragDepth',
    'gl_pointcoord': 'gl_PointCoord',
    'gl_pointsize': 'gl_PointSize',
    'gl_vertexid': 'gl_VertexID',
    'gl_instanceid': 'gl_InstanceID',
}

# GLSL type names (for variable declaration detection)
GLSL_BUILTIN_TYPES = frozenset([
    # Scalar types
    'bool', 'int', 'uint', 'float', 'double',
    # Vector types
    'vec2', 'vec3', 'vec4',
    'bvec2', 'bvec3', 'bvec4',
    'ivec2', 'ivec3', 'ivec4',
    'uvec2', 'uvec3', 'uvec4',
    'dvec2', 'dvec3', 'dvec4',
    # Matrix types
    'mat2', 'mat3', 'mat4',
    'mat2x2', 'mat2x3', 'mat2x4',
    'mat3x2', 'mat3x3', 'mat3x4',
    'mat4x2', 'mat4x3', 'mat4x4',
    'dmat2', 'dmat3', 'dmat4',
    'dmat2x2', 'dmat2x3', 'dmat2x4',
    'dmat3x2', 'dmat3x3', 'dmat3x4',
    'dmat4x2', 'dmat4x3', 'dmat4x4',
    # Sampler types
    'sampler1D', 'sampler2D', 'sampler3D', 'samplerCube',
    'sampler1DShadow', 'sampler2DShadow', 'samplerCubeShadow',
    'isampler1D', 'isampler2D', 'isampler3D', 'isamplerCube',
    'usampler1D', 'usampler2D', 'usampler3D', 'usamplerCube',
    'sampler2DRect', 'sampler2DRectShadow',
    'isampler2DRect', 'usampler2DRect',
    'samplerBuffer', 'isamplerBuffer', 'usamplerBuffer',
    'sampler1DArray', 'sampler2DArray', 'samplerCubeArray',
    'sampler1DArrayShadow', 'sampler2DArrayShadow', 'samplerCubeArrayShadow',
    'isampler1DArray', 'isampler2DArray', 'isamplerCubeArray',
    'usampler1DArray', 'usampler2DArray', 'usamplerCubeArray',
    # Image types
    'image1D', 'iimage1D', 'uimage1D',
    'image2D', 'iimage2D', 'uimage2D',
    'image3D', 'iimage3D', 'uimage3D',
    'image2DRect', 'iimage2DRect', 'uimage2DRect',
    'imageCube', 'iimageCube', 'uimageCube',
    'imageBuffer', 'iimageBuffer', 'uimageBuffer',
    'image1DArray', 'iimage1DArray', 'uimage1DArray',
    'image2DArray', 'iimage2DArray', 'uimage2DArray',
    'imageCubeArray', 'iimageCubeArray', 'uimageCubeArray',
])
