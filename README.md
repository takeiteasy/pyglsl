# pyglsl

Transform Python to GLSL. Fork from long abandoned [nicholasbishop/shaderdef](https://github.com/nicholasbishop/shaderdef). Most of the work was done by the original author, I've just fixed and updated some stuff.

> `pip install pyglsl==0.1.0`

## Example

> **IMPORTANT**
> Shaders are only translated, not compiled. This is to avoid dependency issues and makes it more portable. There is also no static analysis beyond what is valid Python. Errors will have to be deciphered after compiling or runtime.

> **WARNING: Namespace Pollution**
> Using `from pyglsl.glsl import *` shadows Python built-in functions: `abs`, `min`, `max`, `round`, `pow`, `all`, `any`, `int`, `float`, and `bool`. After importing, these names will refer to GLSL type proxies instead of Python functions.
>
> **Safer alternatives:**
> ```python
> # Option 1: Import specific items you need
> from pyglsl.glsl import vec3, vec4, mat4, normalize, dot
> 
> # Option 2: Use qualified imports
> import pyglsl.glsl as glsl
> position = glsl.vec3(0.0, 1.0, 2.0)
> 
> # Option 3: Import in shader file only, not main code
> # shader.py - only GLSL code here
> from pyglsl.glsl import *
> ```

## Supported Features

### Control Flow
- **Conditionals**: `if`, `elif`, `else`
- **Loops**: 
  - `for i in range()` with support for dynamic parameters
  - `while condition:` loops
  - List comprehensions: `[expr for var in range(...)]` (unrolled to loops)
  - `break` and `continue` statements
- **Comparison operators**: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Boolean operators**: `and` (`&&`), `or` (`||`), `not` (`!`)

### Data Types
- **Scalars**: `int`, `float`, `bool`
- **Vectors**: `vec2`, `vec3`, `vec4`, `ivec2`, `ivec3`, `ivec4`, `bvec2`, `bvec3`, `bvec4`
- **Matrices**: `mat2`, `mat3`, `mat4`
- **Arrays**: 
  - Traditional syntax: `arr = Array3[float]()`
  - List literals with automatic type inference: `arr = [1.0, 2.0, 3.0]`
  - Mixed int/float arrays become `float[]` (GLSL behavior)

### Functions
- Function definitions with type hints
- Return statements
- Library functions (passed via `library=` parameter)
- GLSL built-in functions: `normalize`, `dot`, `cross`, `length`, `mix`, etc.

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Augmented assignment: `+=`, `-=`, `*=`, `/=`
- Matrix multiplication: `@` or `*`
- Swizzling: `vec.xyz`, `vec.xxyy`
- Subscripting: `arr[i]`, `mat[row][col]`

### Geometry Shaders
- **Layout Qualifiers**: `@geometry_shader_layout` decorator for primitive configuration
- **Input Primitives**: `points`, `lines`, `triangles`, `lines_adjacency`, `triangles_adjacency`
- **Output Primitives**: `points`, `line_strip`, `triangle_strip`
- **Vertex Emission**: `yield` statements automatically convert to `EmitVertex()`
- **Primitive Completion**: `EndPrimitive()` function
- **Built-in Access**: `gl_in` array for vertex shader outputs (type: `GlGsIn`)
- **Array Inputs**: Use `Sequence[InterfaceType]` for geometry shader inputs
- **Generator Output**: Use `Iterator[InterfaceType]` as return type

Example:
```python
@geometry_shader_layout(input_primitive=triangles,
                        output_primitive=triangle_strip,
                        max_vertices=3)
def geom_shader(gl_in: Sequence[GlGsIn], vs_out: Sequence[VsOut]) -> Iterator[GsOut]:
    for i in range(3):
        yield GsOut(gl_Position=gl_in[i].gl_Position, color=vs_out[i].color)
    EndPrimitive()
    EndPrimitive()
```

### Tessellation Shaders
- **Control Stage**: `TessControlStage` with `@tessellation_control_layout`
- **Evaluation Stage**: `TessEvalStage` with `@tessellation_evaluation_layout`
- **Patch Output**: `layout(vertices = N) out`
- **Primitive Modes**: `quads`, `isolines`, `triangles`
- **Spacing**: `equal_spacing`, `fractional_even_spacing`, `fractional_odd_spacing`
- **Ordering**: `cw`, `ccw`
- **Built-ins**: `gl_TessLevelInner`, `gl_TessLevelOuter`, `gl_TessCoord`

Example:
```python
@tessellation_control_layout(vertices=3)
def tcs_shader(gl_in: Sequence[GlTessIn]) -> TcsOut:
    gl_TessLevelInner[0] = 3.0
    gl_TessLevelOuter[0] = 2.0
    return TcsOut(pos=gl_in[gl_InvocationID].gl_Position)

@tessellation_evaluation_layout(primitive_mode=triangles,
                                spacing=equal_spacing,
                                vertex_order=ccw)
def tes_shader(gl_in: Sequence[GlTessIn]) -> TesOut:
    # Interpolate position using gl_TessCoord
    p0 = vec4(gl_in[0].gl_Position)
    p1 = vec4(gl_in[1].gl_Position)
    p2 = vec4(gl_in[2].gl_Position)
    pos = p0 * gl_TessCoord.x + p1 * gl_TessCoord.y + p2 * gl_TessCoord.z
    return TesOut(gl_Position=pos)
```

### Compute Shaders
- **Stage**: `ComputeStage` with `@compute_shader_layout`
- **Workgroup Size**: `local_size_x`, `local_size_y`, `local_size_z`
- **Shared Memory**: `shared(type)` for `shared` storage qualifier
- **Synchronization**: `barrier()`, `memoryBarrier()`, etc.
- **Atomics**: `atomicAdd`, `atomicMin`, `atomicMax`, etc.
- **Image Load/Store**: `imageLoad`, `imageStore`, `imageAtomic*`

Example:
```python
@compute_shader_layout(local_size_x=16, local_size_y=16)
def compute_shader(img_in: Uniform[image2D], img_out: Uniform[image2D]):
    pos = ivec2(gl_GlobalInvocationID.xy)
    # Shared memory example
    local_data = shared(float[256])
    
    # Image processing
    color = vec4(imageLoad(img_in, pos))
    imageStore(img_out, pos, color)
```

### Interpolation Qualifiers
- **`noperspective`**: Disable perspective-correct interpolation
- **`flat`**: No interpolation (use value from provoking vertex)
- **`smooth`**: Perspective-correct interpolation (default, can be explicit)

Used in interface blocks:
```python
class VsOut(ShaderInterface):
    screenSpaceColor = vec3(noperspective)  # No perspective correction
    vertexID = int(flat)                     # No interpolation
    normal = vec3(smooth)                    # Explicit smooth (default)
    position = vec4()                        # Default (smooth)
```

## Known Limitations

### List Comprehensions
- **Constant Bounds**: `range()` arguments in list comprehensions must be constant expressions computable at transpile time to determine array size.
- **Full Allocation**: Comprehensions with filters (e.g., `[x for x in range(10) if x > 5]`) still allocate the full array size (10 in this case) because GLSL arrays must have a fixed size. The filtered elements are initialized, but the array length remains static.

### Arrays
- **Fixed Size**: All arrays must have a size determined at compile time.
- **No Dynamic Resizing**: `append()`, `pop()`, etc. are not supported.

### Recursion
- GLSL does not support recursion. Recursive function calls will cause a GLSL compilation error (though pyglsl will transpile them).

### Geometry Shaders
- GLSL geometry shaders require version 1.50+ (OpenGL 3.2+). The default version "330 core" supports them.
- Geometry shaders must specify layout qualifiers via the `@geometry_shader_layout` decorator.

## Examples

### Basic Vertex + Fragment Shader

Python input:

```python
# shader.py

from pyglsl.glsl import *

class VertAttrs(AttributeBlock):
    vert_loc = vec3()
    vert_nor = vec3()
    vert_col = vec4()

class View(UniformBlock):
    projection = mat4()
    camera = mat4()
    model = mat4()

class VsOut(ShaderInterface):
    gl_Position = vec4()
    normal = vec3()
    color = vec4()

class FsOut(FragmentShaderOutputBlock):
    fs_color = vec4()

def perspective_projection(projection: mat4, camera: mat4, model: mat4, point: vec3) -> vec4:
    return projection * camera * model * vec4(point, 1.0)

def vert_shader(view: View, attr: VertAttrs) -> VsOut:
    return VsOut(gl_position=perspective_projection(view.projection, view.camera, view.model, attr.vert_loc),
                 normal=attr.vert_nor,
                 color=attr.vert_col)

def frag_shader(vs_out: VsOut) -> FsOut:
    color = vec4((vs_out.normal.x + 1.0) * 0.5,
                 (vs_out.normal.y + 1.0) * 0.5,
                 (vs_out.normal.z + 1.0) * 0.5,
                 1.0)
    return FsOut(fs_color=mix(vs_out.color, color, 1.0))

# ShaderDef class is optional. Makes shaders easier to export+import
export = ShaderDef(vertex_shader=vert_shader,
                   fragment_shader=frag_shader,
                   vertex_functions=[perspective_projection])
```

Then import the shader module and compile.

```python
# example.py

# import shader module (shader.py)
from shader import export as test_shader

# NOTE: You can compile each stage individually by using the *Stage classes. This is if you
#       don't want to use the ShaderDef class inside of your pyglsl shader.
# from pyglsl import VertexStage, FragmentStage
# from shader import vert_shader, frag_shader, perspective_projection
# vs_stage = VertexStage(vert_shader, library=[perspective_projection])
# fs_stage = FragmentStage(frag_shader)
# vs = vs_stage.compile()
# fs = fs_stage.compile()

# Compile Python AST to GLSL + print
vs, fs = test_shader.compile()
print(vs)
print(fs)
```

### Vertex shader output
```glsl
#version 330 core

layout(location=0) in vec3 vert_loc;
layout(location=1) in vec3 vert_nor;
layout(location=2) in vec4 vert_col;

uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;

vec4 perspective_projection(mat4 projection, mat4 camera, mat4 model, vec3 point) {
    return (((projection * camera) * model) * vec4(point, 1.0));
}

out VsOut {
    vec3 normal;
    vec4 color;
} vs_out;

void main() {
    gl_Position = perspective_projection(projection, camera, model, vert_loc);
    vs_out.normal = vert_nor;
    vs_out.color = vert_col;
}
```

### Fragment shader output

```glsl
#version 330 core

in VsOut {
    vec3 normal;
    vec4 color;
} vs_out;

layout(location=0) out vec4 fs_color;

void main() {
    vec4 color = vec4(((vs_out.normal.x + 1.0) * 0.5), ((vs_out.normal.y + 1.0) * 0.5), ((vs_out.normal.z + 1.0) * 0.5), 1.0);
    fs_color = mix(vs_out.color, color, 1.0);
}
```

Voilà.

## LICENSE
```
pyglsl

Copyright (C) 2016 Nicholas Bishop
Copyright (C) 2025 George Watson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
