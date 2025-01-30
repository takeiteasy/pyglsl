from shader import export as test_shader_def
from tester import opengl_context, compile_shader

with opengl_context():
    vs, fs = test_shader_def.compile()
    print("--- vertex source ---")
    print(vs)
    print("--- fragment source ---")
    print(fs)
    print("--- compiling shaders ---")
    print(f"{"SUCCESS!" if compile_shader(vs, fs) else "FAILED!"}")
