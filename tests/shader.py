from pyglsl.glsl import *
from pyglsl import ShaderDef


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

class FsIn(UniformBlock):
    tex = sampler2D()

class FsOut(FragmentShaderOutputBlock):
    fs_color = vec4()

def perspective_projection(projection: mat4, camera: mat4, model: mat4, point: vec3) -> vec4:
    return projection * camera * model * vec4(point, 1.0)

def vert_shader(view: View, attr: VertAttrs) -> VsOut:
    return VsOut(gl_position=perspective_projection(view.projection, view.camera, view.model, attr.vert_loc),
                 normal=attr.vert_nor,
                 color=attr.vert_col)

def frag_shader(vs_out: VsOut, fs_in: FsIn) -> FsOut:
    color = vec4((vs_out.normal.x + 1.0) * 0.5,
                 (vs_out.normal.y + 1.0) * 0.5,
                 (vs_out.normal.z + 1.0) * 0.5,
                 1.0)
    return FsOut(fs_color=mix(vs_out.color, color, 1.0))

export = ShaderDef(vertex_shader=vert_shader,
                   fragment_shader=frag_shader,
                   vertex_functions=[perspective_projection])