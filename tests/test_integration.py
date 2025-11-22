import pytest
import sys
import os

# Add the tests directory to sys.path to import shader.py and tester.py
sys.path.append(os.path.dirname(__file__))

from shader import export as test_shader_def
from tester import opengl_context, compile_shader

def test_example_shader_compilation():
    try:
        import glfw
        from OpenGL.GL import GL_TRUE
    except ImportError:
        pytest.skip("glfw or PyOpenGL not installed", allow_module_level=True)

    # We need to run this in a separate process or ensure context is clean
    # But for now, let's just try to use the context manager
    
    try:
        with opengl_context():
            vs, fs = test_shader_def.compile()
            assert compile_shader(vs, fs)
    except Exception as e:
        # If we can't create a window (e.g. headless), skip
        if "glfw" in str(e).lower() or "window" in str(e).lower():
            pytest.skip(f"Could not create OpenGL context: {e}")
        else:
            raise e

def test_simple_shader_compilation():
    try:
        import glfw
        from OpenGL.GL import GL_TRUE
    except ImportError:
        pytest.skip("glfw or PyOpenGL not installed", allow_module_level=True)

    from pyglsl.glsl import vec4
    from pyglsl.stage import VertexStage, FragmentStage
    from pyglsl.interface import ShaderInterface, FragmentShaderOutputBlock

    class VsOut(ShaderInterface):
        color = vec4()

    class FsOut(FragmentShaderOutputBlock):
        color = vec4()

    def vert() -> VsOut:
        return VsOut(gl_position=vec4(0,0,0,1), color=vec4(1,0,0,1))

    def frag(vs: VsOut) -> FsOut:
        return FsOut(color=vs.color)

    vs_stage = VertexStage(vert)
    fs_stage = FragmentStage(frag)
    
    vs_src = vs_stage.compile()
    fs_src = fs_stage.compile()

    try:
        with opengl_context():
            assert compile_shader(vs_src, fs_src)
    except Exception as e:
         if "glfw" in str(e).lower() or "window" in str(e).lower():
            pytest.skip(f"Could not create OpenGL context: {e}")
         else:
            raise e
