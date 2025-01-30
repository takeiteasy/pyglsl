# pyglsl

> [!CAUTION]
> Work in progress

Transform Python to GLSL. Fork from long abandoned [nicholasbishop/shaderdef](https://github.com/nicholasbishop/shaderdef).

> [!IMPORTANT]
> Shaders are only translated, not compiled. This is to avoid dependency issues and makes it more portable.

```python
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
    return FsOut(fs_color=mix(vs_out.color, color))

export = ShaderDef(vertex_shader=vert_shader,
                   fragment_shader=frag_shader,
                   vertex_functions=[perspective_projection])
```

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

```glsl
#version 330 core

in VsOut {
    vec3 normal;
    vec4 color;
} vs_out;

layout(location=0) out vec4 fs_color;

void main() {
    vec4 color = vec4(((vs_out.normal.x + 1.0) * 0.5), ((vs_out.normal.y + 1.0) * 0.5), ((vs_out.normal.z + 1.0) * 0.5), 1.0);
    fs_color = mix(vs_out.color, color);
}
```

## TODO

- [ ] Finish adding GLSL types + builtins
- [ ] Geometry Shaders

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
