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

from .interface import ShaderInterface, UniformBlock, AttributeBlock, FragmentShaderOutputBlock
from .types import GlslType, GlslArray, GlslStruct

# Explicit export list to control namespace pollution when using 'from pyglsl.glsl import *'
__all__ = [
    # Interface classes
    'ShaderInterface', 'UniformBlock', 'AttributeBlock', 'FragmentShaderOutputBlock',
    # Type classes  
    'GlslType', 'GlslArray', 'GlslStruct',
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
    # Array types
    'Array1', 'Array2', 'Array3', 'Array4', 'Array5', 'Array6', 'Array7', 'Array8',
    'Array9', 'Array10', 'Array11', 'Array12', 'Array13', 'Array14', 'Array15', 'Array16',
    # Special classes
    'void', 'discard',
    # Built-in functions (WARNING: These shadow Python built-ins when imported with *)
    'abs', 'min', 'max', 'round', 'pow', 'all', 'any',
    # Math functions
    'ceil', 'floor', 'mod', 'clamp', 'mix', 'step', 'smoothstep',
    'sqrt', 'exp', 'log', 'exp2', 'log2',
    # Trigonometric functions
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'radians', 'degrees',
    # Vector functions
    'length', 'distance', 'dot', 'cross', 'normalize', 'reflect', 'refract',
    # Matrix functions
    'vecX', 'matX', 'transpose', 'inverse', 'outerProduct', 'determinant',
    # Texture functions
    'texture', 'textureLod', 'textureProj', 'textureOffset', 'texelFetch',
    # Noise functions
    'noise1', 'noise2', 'noise3', 'noise4',
    # Derivative functions
    'dFdx', 'dFdy', 'fwidth',
    # Utility functions
    'isnan', 'isinf', 'floatBitsToInt', 'intBitsToFloat',
    'packUnorm2x16', 'unpackUnorm2x16',
    # Geometry shader primitives
    'points', 'lines', 'lines_adjacency', 'triangles', 'triangles_adjacency',
    'line_strip', 'triangle_strip',
    # Geometry shader functions
    'EmitVertex', 'EndPrimitive',
    # Geometry shader decorator
    'geometry_shader_layout',
    # Geometry shader built-in interface
    'GlGsIn',
    # Interpolation qualifiers
    'noperspective', 'flat', 'smooth',
    # Tessellation primitives/spacings/orders
    'quads', 'isolines', 'equal_spacing', 'fractional_even_spacing', 'fractional_odd_spacing', 'cw', 'ccw',
    # Tessellation decorators
    'tessellation_control_layout', 'tessellation_evaluation_layout',
    # Tessellation built-in interface
    'GlTessIn',
    # Compute shader decorator
    'compute_shader_layout',
    # Compute shader qualifiers
    'shared',
    # Compute shader built-ins
    'barrier', 'memoryBarrier', 'memoryBarrierAtomicCounter', 'memoryBarrierBuffer', 'memoryBarrierImage', 'memoryBarrierShared', 'groupMemoryBarrier',
    'atomicAdd', 'atomicMin', 'atomicMax', 'atomicAnd', 'atomicOr', 'atomicXor', 'atomicExchange', 'atomicCompSwap',
    'imageLoad', 'imageStore', 'imageAtomicAdd', 'imageAtomicMin', 'imageAtomicMax', 'imageAtomicAnd', 'imageAtomicOr', 'imageAtomicXor', 'imageAtomicExchange', 'imageAtomicCompSwap',
]

bool = GlslType
int = GlslType
uint = GlslType
float = GlslType
double = GlslType

vec2 = GlslType
vec3 = GlslType
vec4 = GlslType
bvec2 = GlslType
bvec3 = GlslType
bvec4 = GlslType
ivec2 = GlslType
ivec3 = GlslType
ivec4 = GlslType
uvec2 = GlslType
uvec3 = GlslType
uvec4 = GlslType
dvec2 = GlslType
dvec3 = GlslType
dvec4 = GlslType

mat2 = GlslType
mat3 = GlslType
mat4 = GlslType
mat2x2 = GlslType
mat2x3 = GlslType
mat2x4 = GlslType
mat3x2 = GlslType
mat3x3 = GlslType
mat3x4 = GlslType
mat4x2 = GlslType
mat4x3 = GlslType
mat4x4 = GlslType

dmat2 = GlslType
dmat3 = GlslType
dmat4 = GlslType
dmat2x2 = GlslType
dmat2x3 = GlslType
dmat2x4 = GlslType
dmat3x2 = GlslType
dmat3x3 = GlslType
dmat3x4 = GlslType
dmat4x2 = GlslType
dmat4x3 = GlslType
dmat4x4 = GlslType

sampler1D = GlslType
sampler2D = GlslType
sampler3D = GlslType
samplerCube = GlslType
sampler1DShadow = GlslType
sampler2DShadow = GlslType
samplerCubeShadow = GlslType

isampler1D = GlslType
isampler2D = GlslType
isampler3D = GlslType
isamplerCube = GlslType
usampler1D = GlslType
usampler2D = GlslType
usampler3D = GlslType
usamplerCube = GlslType
sampler2DRect = GlslType
sampler2DRectShadow = GlslType
isampler2DRect = GlslType
usampler2DRect = GlslType
samplerBuffer = GlslType
isamplerBuffer = GlslType
usamplerBuffer = GlslType
sampler1DArray = GlslType
sampler2DArray = GlslType
samplerCubeArray = GlslType
sampler1DArrayShadow = GlslType
sampler2DArrayShadow = GlslType
samplerCubeArrayShadow = GlslType
isampler1DArray = GlslType
isampler2DArray = GlslType
isamplerCubeArray = GlslType
usampler1DArray = GlslType
usampler2DArray = GlslType
usamplerCubeArray = GlslType

image1D = GlslType
iimage1D = GlslType
uimage1D = GlslType
image2D = GlslType
iimage2D = GlslType
uimage2D = GlslType
image3D = GlslType
iimage3D = GlslType
uimage3D = GlslType
image2DRect = GlslType
iimage2DRect = GlslType
uimage2DRect = GlslType
imageCube = GlslType
iimageCube = GlslType
uimageCube = GlslType
imageBuffer = GlslType
iimageBuffer = GlslType
uimageBuffer = GlslType
image1DArray = GlslType
iimage1DArray = GlslType
uimage1DArray = GlslType
image2DArray = GlslType
iimage2DArray = GlslType
uimage2DArray = GlslType
imageCubeArray = GlslType
iimageCubeArray = GlslType
uimageCubeArray = GlslType

Array1 = GlslArray
Array2 = GlslArray
Array3 = GlslArray
Array4 = GlslArray
Array5 = GlslArray
Array6 = GlslArray
Array7 = GlslArray
Array8 = GlslArray
Array9 = GlslArray
Array10 = GlslArray
Array11 = GlslArray
Array12 = GlslArray
Array13 = GlslArray
Array14 = GlslArray
Array15 = GlslArray
Array16 = GlslArray

class void(object):
    pass

class discard(object):
    pass

def abs(*args, **kwargs):
    pass

def ceil(*args, **kwargs):
    pass

def floor(*args, **kwargs):
    pass

def round(*args, **kwargs):
    pass

def mod(*args, **kwargs):
    pass

def min(*args, **kwargs):
    pass

def max(*args, **kwargs):
    pass

def clamp(*args, **kwargs):
    pass

def mix(*args, **kwargs):
    pass

def step(*args, **kwargs):
    pass

def smoothstep(*args, **kwargs):
    pass

def sqrt(*args, **kwargs):
    pass

def pow(*args, **kwargs):
    pass

def exp(*args, **kwargs):
    pass

def log(*args, **kwargs):
    pass

def exp2(*args, **kwargs):
    pass

def log2(*args, **kwargs):
    pass

def sin(*args, **kwargs):
    pass

def cos(*args, **kwargs):
    pass

def tan(*args, **kwargs):
    pass

def asin(*args, **kwargs):
    pass

def acos(*args, **kwargs):
    pass

def atan(*args, **kwargs):
    pass

def atan2(*args, **kwargs):
    pass

def radians(*args, **kwargs):
    pass

def degrees(*args, **kwargs):
    pass

def length(*args, **kwargs):
    pass

def distance(*args, **kwargs):
    pass

def dot(*args, **kwargs):
    pass

def cross(*args, **kwargs):
    pass

def normalize(*args, **kwargs):
    pass

def reflect(*args, **kwargs):
    pass

def refract(*args, **kwargs):
    pass

def vecX(*args, **kwargs):
    pass

def matX(*args, **kwargs):
    pass

def transpose(*args, **kwargs):
    pass

def inverse(*args, **kwargs):
    pass

def outerProduct(*args, **kwargs):
    pass

def determinant(*args, **kwargs):
    pass

def texture(*args, **kwargs):
    pass

def textureLod(*args, **kwargs):
    pass

def textureProj(*args, **kwargs):
    pass

def textureOffset(*args, **kwargs):
    pass

def texelFetch(*args, **kwargs):
    pass

def noise1(*args, **kwargs):
    pass

def noise2(*args, **kwargs):
    pass

def noise3(*args, **kwargs):
    pass

def noise4(*args, **kwargs):
    pass

def dFdx(*args, **kwargs):
    pass

def dFdy(*args, **kwargs):
    pass

def fwidth(*args, **kwargs):
    pass

def any(*args, **kwargs):
    pass

def all(*args, **kwargs):
    pass

def isnan(*args, **kwargs):
    pass

def isinf(*args, **kwargs):
    pass

def floatBitsToInt(*args, **kwargs):
    pass

def intBitsToFloat(*args, **kwargs):
    pass

def packUnorm2x16(*args, **kwargs):
    pass

def unpackUnorm2x16(*args, **kwargs):
    pass

class points(object):
    pass

class lines(object):
    pass

class lines_adjacency(object):
    pass

class triangles(object):
    pass

class triangles_adjacency(object):
    pass

class line_strip(object):
    pass

class triangle_strip(object):
    pass

class quads(object):
    pass

class isolines(object):
    pass

class equal_spacing(object):
    pass

class fractional_even_spacing(object):
    pass

class fractional_odd_spacing(object):
    pass

class cw(object):
    pass

class ccw(object):
    pass

def EmitVertex():
    pass

def EndPrimitive():
    pass

def geometry_shader_layout(input_primitive, output_primitive, max_vertices):
    """Decorator to specify geometry shader layout qualifiers.
    
    Args:
        input_primitive: Input primitive type (points, lines, triangles, etc.)
        output_primitive: Output primitive type (points, line_strip, triangle_strip)
        max_vertices: Maximum number of vertices the shader can output
    
    Example:
        >>> @geometry_shader_layout(input_primitive=triangles,
        ...                          output_primitive=triangle_strip,
        ...                          max_vertices=3)
        ... def geom_shader(...) -> Iterator[Output]:
        ...     yield Output(...)
    """
    def decorator(func):
        # Store metadata on the function for later retrieval during compilation
        func._geometry_layout = {
            'input_primitive': input_primitive,
            'output_primitive': output_primitive,
            'max_vertices': max_vertices
        }
        return func
        return func
    return decorator

def tessellation_control_layout(vertices):
    """Decorator to specify tessellation control shader layout qualifiers.
    
    Args:
        vertices: Number of vertices in the output patch
    
    Example:
        >>> @tessellation_control_layout(vertices=3)
        ... def tcs_shader(...) -> None:
        ...     pass
    """
    def decorator(func):
        func._tess_control_layout = {
            'vertices': vertices
        }
        return func
    return decorator

def tessellation_evaluation_layout(primitive_mode, spacing=None, vertex_order=None):
    """Decorator to specify tessellation evaluation shader layout qualifiers.
    
    Args:
        primitive_mode: Input primitive type (triangles, quads, isolines)
        spacing: Vertex spacing (equal_spacing, fractional_even_spacing, fractional_odd_spacing)
        vertex_order: Vertex winding order (cw, ccw)
    
    Example:
        >>> @tessellation_evaluation_layout(primitive_mode=triangles,
        ...                                 spacing=equal_spacing,
        ...                                 vertex_order=ccw)
        ... def tes_shader(...) -> None:
        ...     pass
    """
    def decorator(func):
        func._tess_eval_layout = {
            'primitive_mode': primitive_mode,
            'spacing': spacing,
            'vertex_order': vertex_order
        }
        return func
    return decorator

def compute_shader_layout(local_size_x=1, local_size_y=1, local_size_z=1):
    """Decorator to specify compute shader layout qualifiers.
    
    Args:
        local_size_x: Local workgroup size in X dimension (default 1)
        local_size_y: Local workgroup size in Y dimension (default 1)
        local_size_z: Local workgroup size in Z dimension (default 1)
    
    Example:
        >>> @compute_shader_layout(local_size_x=16, local_size_y=16)
        ... def compute_shader():
        ...     pass
    """
    def decorator(func):
        func._compute_layout = {
            'local_size_x': local_size_x,
            'local_size_y': local_size_y,
            'local_size_z': local_size_z
        }
        return func
    return decorator

# Interpolation qualifiers for interface block members
class noperspective(object):
    """No perspective correction interpolation qualifier.
    
    Use in interface blocks: member = vec3(noperspective)
    Generates: noperspective vec3 member;
    """
    pass

class flat(object):
    """Flat (no interpolation) qualifier.
    
    Use in interface blocks: member = int(flat)
    Generates: flat int member;
    """
    pass

class smooth(object):
    """Smooth (perspective-correct) interpolation qualifier (default).
    
    Use in interface blocks: member = vec3(smooth)
    Generates: smooth vec3 member;
    """
    pass

class shared(object):
    """Shared memory storage qualifier for compute shaders.
    
    Use in function body: data = shared(float[256])
    Generates: shared float data[256];
    """
    def __init__(self, type_):
        pass

# Compute shader built-in functions
def barrier(): pass
def memoryBarrier(): pass
def memoryBarrierAtomicCounter(): pass
def memoryBarrierBuffer(): pass
def memoryBarrierImage(): pass
def memoryBarrierShared(): pass
def groupMemoryBarrier(): pass

def atomicAdd(*args, **kwargs): pass
def atomicMin(*args, **kwargs): pass
def atomicMax(*args, **kwargs): pass
def atomicAnd(*args, **kwargs): pass
def atomicOr(*args, **kwargs): pass
def atomicXor(*args, **kwargs): pass
def atomicExchange(*args, **kwargs): pass
def atomicCompSwap(*args, **kwargs): pass

def imageLoad(*args, **kwargs): pass
def imageStore(*args, **kwargs): pass
def imageAtomicAdd(*args, **kwargs): pass
def imageAtomicMin(*args, **kwargs): pass
def imageAtomicMax(*args, **kwargs): pass
def imageAtomicAnd(*args, **kwargs): pass
def imageAtomicOr(*args, **kwargs): pass
def imageAtomicXor(*args, **kwargs): pass
def imageAtomicExchange(*args, **kwargs): pass
def imageAtomicCompSwap(*args, **kwargs): pass

# Import GlGsIn from interface module (will be defined there)
# We import it here for convenience so users can do: from pyglsl.glsl import GlGsIn
# The actual definition is in interface.py to avoid circular imports
def __getattr__(name):
    """Lazy import for GlGsIn to avoid circular dependencies."""
    if name == 'GlGsIn':
        from .interface import GlGsIn
        return GlGsIn
    if name == 'GlTessIn':
        from .interface import GlTessIn
        return GlTessIn
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
