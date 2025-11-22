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

def test_break_statement():
    """Test that break statement works in loops."""
    def shader():
        for i in range(10):
            if i == 5:
                break
            a = int(i)
    
    glsl = compile_function(shader)
    assert "break;" in glsl, f"Expected 'break;' in:\n{glsl}"

def test_continue_statement():
    """Test that continue statement works in loops."""
    def shader():
        for i in range(10):
            if i == 3:
                continue
            a = int(i)
    
    glsl = compile_function(shader)
    assert "continue;" in glsl, f"Expected 'continue;' in:\n{glsl}"

def test_break_continue_together():
    """Test break and continue in same loop."""
    def shader():
        for i in range(10):
            if i == 5:
                break
            if i == 3:
                continue
            a = int(i)
    
    glsl = compile_function(shader)
    assert "break;" in glsl
    assert "continue;" in glsl

def test_dynamic_range_variable():
    """Test for loop with variable end value."""
    def shader():
        n = int(10)
        for i in range(n):
            a = int(i)
    
    glsl = compile_function(shader)
    assert "for (int i = 0; i < n; i++) {" in glsl, f"Expected 'for (int i = 0; i < n; i++) {{' in:\n{glsl}"

def test_dynamic_range_two_args():
    """Test for loop with variable start and end."""
    def shader():
        start = int(2)
        end = int(10)
        for i in range(start, end):
            a = int(i)
    
    glsl = compile_function(shader)
    assert "for (int i = start; i < end; i++) {" in glsl, f"Expected 'for (int i = start; i < end; i++) {{' in:\n{glsl}"

def test_dynamic_range_with_step():
    """Test for loop with constant step."""
    def shader():
        for i in range(0, 10, 2):
            a = int(i)
    
    glsl = compile_function(shader)
    assert "for (int i = 0; i < 10; i += 2) {" in glsl, f"Expected 'for (int i = 0; i < 10; i += 2) {{' in:\n{glsl}"

def test_dynamic_range_variable_step():
    """Test for loop with variable step."""
    def shader():
        step = int(2)
        for i in range(0, 10, step):
            a = int(i)
    
    glsl = compile_function(shader)
    assert "for (int i = 0; i < 10; i += step) {" in glsl, f"Expected 'for (int i = 0; i < 10; i += step) {{' in:\n{glsl}"

def test_nested_loops_with_break():
    """Test nested loops with break statements."""
    def shader():
        for i in range(10):
            for j in range(5):
                if j == 2:
                    break
    
    glsl = compile_function(shader)
    assert "for (int i = 0; i < 10; i++) {" in glsl
    assert "for (int j = 0; j < 5; j++) {" in glsl
    assert "break;" in glsl

def test_array_literal_float():
    """Test array initialization with float literals."""
    def shader():
        arr = [1.0, 2.0, 3.0]
    
    glsl = compile_function(shader)
    assert "float arr[3] = float[3](1.0, 2.0, 3.0);" in glsl, f"Expected array declaration in:\n{glsl}"

def test_array_literal_int():
    """Test array initialization with int literals."""
    def shader():
        arr = [1, 2, 3, 4]
    
    glsl = compile_function(shader)
    assert "int arr[4] = int[4](1, 2, 3, 4);" in glsl, f"Expected array declaration in:\n{glsl}"

def test_array_literal_mixed_becomes_float():
    """Test that mixed int/float arrays become float[] (GLSL behavior)."""
    def shader():
        arr = [1, 2.0, 3]
    
    glsl = compile_function(shader)
    # Should be float array since one element has decimal
    assert "float arr[3]" in glsl, f"Expected float array in:\n{glsl}"
    assert "float[3]" in glsl

def test_array_literal_single_element():
    """Test single-element array."""
    def shader():
        arr = [42.0]
    
    glsl = compile_function(shader)
    assert "float arr[1] = float[1](42.0);" in glsl

def test_array_literal_empty_raises_error():
    """Test that empty arrays raise an error."""
    def shader():
        arr = []
    
    with pytest.raises(ValueError, match="empty array literals"):
        compile_function(shader)
