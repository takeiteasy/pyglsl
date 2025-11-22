import pytest
from pyglsl.glsl import *
from pyglsl.stage import VertexStage, FragmentStage

def compile_function(func, stage_type=VertexStage):
    stage = stage_type(func)
    return stage.compile()

def test_basic_types():
    def shader():
        a = vec3(1.0, 2.0, 3.0)
        b = mat4(1.0)
        c = float(1.0)
    
    glsl = compile_function(shader)
    assert "vec3 a = vec3(1.0, 2.0, 3.0);" in glsl, f"Expected 'vec3 a = vec3(1.0, 2.0, 3.0);' in:\n{glsl}"
    assert "mat4 b = mat4(1.0);" in glsl, f"Expected 'mat4 b = mat4(1.0);' in:\n{glsl}"
    assert "float c = float(1.0);" in glsl, f"Expected 'float c = float(1.0);' in:\n{glsl}"

def test_arithmetic():
    def shader():
        a = vec3(1.0)
        b = vec3(2.0)
        c = vec3(0.0)
        c = a + b * 2.0
    
    glsl = compile_function(shader)
    assert "vec3 c = vec3(0.0);" in glsl
    assert "c = (a + (b * 2.0));" in glsl, f"Expected 'c = (a + (b * 2.0));' in:\n{glsl}"

def test_control_flow():
    def shader():
        if True:
            a = int(1)
        else:
            a = int(2)
            
        for i in range(10):
            b = int(i)
            
    glsl = compile_function(shader)
    assert "if (true) {" in glsl, f"Expected 'if (true) {{' in:\n{glsl}"
    assert "int a = int(1);" in glsl, f"Expected 'int a = int(1);' in:\n{glsl}"
    assert "} else {" in glsl, f"Expected '}} else {{' in:\n{glsl}"
    assert "int a = int(2);" in glsl, f"Expected 'int a = int(2);' in:\n{glsl}"
    assert "for (int i = 0; i < 10; i++) {" in glsl, f"Expected 'for (int i = 0; i < 10; i++) {{' in:\n{glsl}"

def test_functions():
    def helper(x: float) -> float:
        return x * 2.0
        
    def main_shader():
        y = float(0.0)
        y = helper(1.0)
        
    stage = VertexStage(main_shader, library=[helper])
    glsl = stage.compile()
    
    assert "float helper(float x) {" in glsl, f"Expected 'float helper(float x) {{' in:\n{glsl}"
    assert "return (x * 2.0);" in glsl, f"Expected 'return (x * 2.0);' in:\n{glsl}"
    assert "y = helper(1.0);" in glsl, f"Expected 'y = helper(1.0);' in:\n{glsl}"

def test_builtins():
    def shader():
        v = vec3(1.0)
        l = float(0.0)
        l = length(v)
        n = vec3(0.0)
        n = normalize(v)
        d = float(0.0)
        d = dot(v, v)
        c = vec3(0.0)
        c = cross(v, v)
        m = vec3(0.0)
        m = mix(v, v, 0.5)
        
    glsl = compile_function(shader)
    assert "l = length(v);" in glsl, f"Expected 'l = length(v);' in:\n{glsl}"
    assert "n = normalize(v);" in glsl, f"Expected 'n = normalize(v);' in:\n{glsl}"
    assert "d = dot(v, v);" in glsl, f"Expected 'd = dot(v, v);' in:\n{glsl}"
    assert "c = cross(v, v);" in glsl, f"Expected 'c = cross(v, v);' in:\n{glsl}"
    assert "m = mix(v, v, 0.5);" in glsl, f"Expected 'm = mix(v, v, 0.5);' in:\n{glsl}"

def test_comparison():
    def shader():
        if 1 != 2:
            a = int(1)
            
    glsl = compile_function(shader)
    assert "if (1 != 2) {" in glsl, f"Expected 'if (1 != 2) {{' in:\n{glsl}"

def test_equality():
    def shader():
        if 1 == 2:
            a = int(1)
            
    glsl = compile_function(shader)
    assert "if (1 == 2) {" in glsl, f"Expected 'if (1 == 2) {{' in:\n{glsl}"

def test_interface_blocks():
    from pyglsl.interface import UniformBlock, AttributeBlock, ShaderInterface
    
    class Uniforms(UniformBlock):
        u_time = float()
        u_matrix = mat4()
        
    class Attributes(AttributeBlock):
        a_pos = vec3()
        
    class Outputs(ShaderInterface):
        v_pos = vec3()
        
    def shader(u: Uniforms, a: Attributes) -> Outputs:
        return Outputs(v_pos=a.a_pos)
        
    stage = VertexStage(shader)
    glsl = stage.compile()
    
    assert "uniform float u_time;" in glsl
    assert "uniform mat4 u_matrix;" in glsl
    assert "layout(location=0) in vec3 a_pos;" in glsl
    assert "out Outputs {" in glsl
    assert "vec3 v_pos;" in glsl
    assert "outputs.v_pos = a_pos;" in glsl
