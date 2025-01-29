from pyglsl import Compiler
from shader import (vert_shader, frag_shader,
                    triangle_2d_altitudes,
                    viewport_to_screen_space,
                    perspective_projection)
from tester import compile_shader

test = Compiler(vert_shader, frag_shader, library=[viewport_to_screen_space,
                                                   triangle_2d_altitudes,
                                                   perspective_projection])
v, f, _ = test.compile()
print("--- vertex source ---")
print(v)
print("--- fragment source ---")
print(f)
print("--- compiling shaders ---")
print(f"{"SUCCESS" if compile_shader(v, f) else "NOOOOO"}")
