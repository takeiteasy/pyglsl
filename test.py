from shader import export as test_shader_def
from tester import compile_shader

vs, fs = test_shader_def.compile()
print("--- vertex source ---")
print(vs)
print("--- fragment source ---")
print(fs)
print("--- compiling shaders ---")
print(f"{"SUCCESS" if compile_shader(vs, fs) else "NOOOOO"}")
