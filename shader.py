from pyglsl.glsl import *

class VertAttrs(AttributeBlock):
    vert_loc = vec3()
    vert_nor = vec3()
    vert_col = vec4()

class View(UniformBlock):
    projection = mat4()
    camera = mat4()
    model = mat4()
    fb_size = vec2()

class VsOut(ShaderInterface):
    gl_Position = vec4()
    normal = vec3()
    color = vec4()

class FsOut(FragmentShaderOutputBlock):
    fs_color = vec4()

def perspective_projection(projection: mat4, camera: mat4, model: mat4, point: vec3) -> vec4:
    return projection * camera * model * vec4(point, 1.0)

def viewport_to_screen_space(framebuffer_size: vec2, point: vec4) -> vec2:
    """Transform point in viewport space to screen space."""
    return (framebuffer_size * point.xy) / point.w

# Distance of each triangle vertex to the opposite edge
def triangle_2d_altitudes(triangle: Array3[vec2]) -> vec3:
    ed0 = vec2(triangle[2] - triangle[1])
    ed1 = vec2(triangle[2] - triangle[0])
    ed2 = vec2(triangle[1] - triangle[0])

    area = float(abs((ed1.x * ed2.y) -
                     (ed1.y * ed2.x)))

    return vec3(area / length(ed0),
                area / length(ed1),
                area / length(ed2))


def vert_shader(view: View, attr: VertAttrs) -> VsOut:
    return VsOut(gl_position=perspective_projection(view.projection,
                                                    view.camera,
                                                    view.model,
                                                    attr.vert_loc),
                 normal=attr.vert_nor,
                 color=attr.vert_col)


def frag_shader(vs_out: VsOut) -> FsOut:
    color = vec4((vs_out.normal.x + 1.0) * 0.5,
                 (vs_out.normal.y + 1.0) * 0.5,
                 (vs_out.normal.z + 1.0) * 0.5,
                 1.0)

    # Adapted from
    # http://strattonbrazil.blogspot.com/2011/09/single-pass-wireframe-rendering_10.html
    nearest = float(min(min(vs_out.altitudes[0], vs_out.altitudes[1]),
                        vs_out.altitudes[2]))
    edge_intensity = float(1.0 - exp2(-1.0 * nearest * nearest))

    color *= edge_intensity

    # TODO, dijkstra viz hack
    dista = float(vs_out.color[0])

    if dista < 0:
        color *= vec4(0.3, 0.3, 0.3, 1.0)
    else:
        # color[0] = dista;
        rep = float(0.1)
        fac = float(1.0 / rep)
        color[0] = pow(mod(vs_out.color[0], rep) * fac, 4)

    return FsOut(fs_color=color)