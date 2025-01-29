from pyglsl.glsl import *
from pyglsl.stage import Stage
from pyglsl import Compiler
from dataclasses import dataclass

@dataclass
class FsOut(FragmentShaderOutputBlock):
    color = vec4()

@dataclass
class VsOut(ShaderInterface):
    color = vec4()

def frag_shader(vs_out: VsOut) -> FsOut:
    color = vec4((vs_out.normal.x + 1.0) * 0.5,
                 (vs_out.normal.y + 1.0) * 0.5,
                 (vs_out.normal.z + 1.0) * 0.5,
                 1.0)

    # Adapted from
    # http://strattonbrazil.blogspot.com/2011/09/single-pass-wireframe-rendering_10.html
    nearest = float(min(min(vs_out.altitudes[0], vs_out.altitudes[1]), vs_out.altitudes[2]))
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
test = Stage(frag_shader)
test.translate()
print('\n'.join(test.lines))