# pyglsl

> **CAUTION**
> Work in progress, see [TODO](#todo) section.

Transform Python to GLSL. Fork from long abandoned [nicholasbishop/shaderdef](https://github.com/nicholasbishop/shaderdef). Most of the work was done by the original author, I've just fixed and updated some stuff.

> `pip install pyglsl==0.0.8`

## Example

> **IMPORTANT**
> Shaders are only translated, not compiled. This is to avoid dependency issues and makes it more portable. There is also no static analysis beyond what is valid Python. Errors will have to be deciphered after compiling or runtime.

> **WARNING**
> Not every aspect of Python is supported when writing a shader. For example, loops are limited to `for i in range()` type loops.

> **TIP**
> It is a good idea to keep your pyglsl shader code in a separate file and importing with `from pyglsl.glsl import *`. This will avoid naming conflicts as `pyglsl.glsl` contains the builtin types + functions from GLSL.

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


### Python input

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
