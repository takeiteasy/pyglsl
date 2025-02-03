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

from .interface import ShaderInterface, UniformBlock, AttributeBlock, FragmentShaderOutputBlock
from .types import GlslType, GlslArray
from .shaderdef import ShaderDef

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

def abs(*args, **kwargs):
    pass

def acos(*args, **kwargs):
    pass

def asin(*args, **kwargs):
    pass

def atan(*args, **kwargs):
    pass

def atan2(*args, **kwargs):
    pass

def ceil(*args, **kwargs):
    pass

def clamp(*args, **kwargs):
    pass

def cos(*args, **kwargs):
    pass

def cosh(*args, **kwargs):
    pass

def degrees(*args, **kwargs):
    pass

def exp(*args, **kwargs):
    pass

def exp2(*args, **kwargs):
    pass

def floor(*args, **kwargs):
    pass

def fract(*args, **kwargs):
    pass

def fwidth(*args, **kwargs):
    pass

def inversesqrt(*args, **kwargs):
    pass

def log(*args, **kwargs):
    pass

def log2(*args, **kwargs):
    pass

def max(*args, **kwargs):
    pass

def min(*args, **kwargs):
    pass

def mod(*args, **kwargs):
    pass

def normalize(*args, **kwargs):
    pass

def pow(*args, **kwargs):
    pass

def radians(*args, **kwargs):
    pass

def round(*args, **kwargs):
    pass

def roundEven(*args, **kwargs):
    pass

def sign(*args, **kwargs):
    pass

def sin(*args, **kwargs):
    pass

def sinh(*args, **kwargs):
    pass

def smoothstep(*args, **kwargs):
    pass

def sqrt(*args, **kwargs):
    pass

def step(*args, **kwargs):
    pass

def tan(*args, **kwargs):
    pass

def tanh(*args, **kwargs):
    pass

def trunc(*args, **kwargs):
    pass

def cross(*args, **kwargs):
    pass

def distance(*args, **kwargs):
    pass

def dot(*args, **kwargs):
    pass

def length(*args, **kwargs):
    pass

def reflect(*args, **kwargs):
    pass

def refract(*args, **kwargs):
    pass

def equal(*args, **kwargs):
    pass

def greaterThan(*args, **kwargs):
    pass

def greaterThanEqual(*args, **kwargs):
    pass

def lessThan(*args, **kwargs):
    pass

def lessThanEqual(*args, **kwargs):
    pass

def notEqual(*args, **kwargs):
    pass

def texture(*args, **kwargs):
    pass

def textureLod(*args, **kwargs):
    pass

def textureProj(*args, **kwargs):
    pass

def textureGrad(*args, **kwargs):
    pass

def textureFetch(*args, **kwargs):
    pass

def textureSamples(*args, **kwargs):
    pass

def textureSize(*args, **kwargs):
    pass

def imageLoad(*args, **kwargs):
    pass

def imageStore(*args, **kwargs):
    pass

def imageAtomicAdd(*args, **kwargs):
    pass

def imageAtomicAnd(*args, **kwargs):
    pass

def imageAtomicCompSwap(*args, **kwargs):
    pass

def imageAtomicExchange(*args, **kwargs):
    pass

def imageAtomicMax(*args, **kwargs):
    pass

def imageAtomicMin(*args, **kwargs):
    pass

def imageAtomicOr(*args, **kwargs):
    pass

def imageAtomicSub(*args, **kwargs):
    pass

def imageAtomicXor(*args, **kwargs):
    pass

def mix(*args, **kwargs):
    pass

def fma(*args, **kwargs):
    pass

def interpolateAtCentroid(*args, **kwargs):
    pass

def interpolateAtSample(*args, **kwargs):
    pass

def interpolateAtVertex(*args, **kwargs):
    pass

def packUnorm4x8(*args, **kwargs):
    pass

def packSnorm4x8(*args, **kwargs):
    pass

def unpackUnorm4x8(*args, **kwargs):
    pass

def unpackSnorm4x8(*args, **kwargs):
    pass

def packHalf2x16(*args, **kwargs):
    pass

def unpackHalf2x16(*args, **kwargs):
    pass

def packDouble2x32(*args, **kwargs):
    pass

def unpackDouble2x32(*args, **kwargs):
    pass

def bitfieldExtract(*args, **kwargs):
    pass

def bitfieldInsert(*args, **kwargs):
    pass

def bitfieldReverse(*args, **kwargs):
    pass

def findLSB(*args, **kwargs):
    pass

def findMSB(*args, **kwargs):
    pass

def fma(*args, **kwargs):
    pass

def atomicAdd(*args, **kwargs):
    pass

def atomicMin(*args, **kwargs):
    pass

def atomicMax(*args, **kwargs):
    pass

def atomicAnd(*args, **kwargs):
    pass

def atomicOr(*args, **kwargs):
    pass

def atomicXor(*args, **kwargs):
    pass

def atomicExchange(*args, **kwargs):
    pass

def atomicCompSwap(*args, **kwargs):
    pass

def barrier(*args, **kwargs):
    pass

def memoryBarrier(*args, **kwargs):
    pass

def memoryBarrierAtomicCounter(*args, **kwargs):
    pass

def memoryBarrierBuffer(*args, **kwargs):
    pass

def memoryBarrierImage(*args, **kwargs):
    pass

def memoryBarrierShared(*args, **kwargs):
    pass

def groupMemoryBarrier(*args, **kwargs):
    pass

def groupMemoryBarrierShared(*args, **kwargs):
    pass
