import pytest
from pyglsl.glsl import *
from pyglsl.stage import VertexStage, FragmentStage, GeometryStage

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

# ==================== TESTS FOR WHILE LOOPS ====================

def test_while_loop():
    """Test basic while loop."""
    def shader():
        i = int(0)
        while i < 10:
            i = i + 1
    
    glsl = compile_function(shader)
    assert "while (i < 10) {" in glsl, f"Expected 'while (i < 10) {{' in:\n{glsl}"
    assert "i = (i + 1);" in glsl

def test_while_with_break():
    """Test while loop with break."""
    def shader():
        i = int(0)
        while True:
            if i >= 10:
                break
            i = i + 1
    
    glsl = compile_function(shader)
    assert "while (true) {" in glsl, f"Expected 'while (true) {{' in:\n{glsl}"
    assert "break;" in glsl

def test_while_with_continue():
    """Test while loop with continue."""
    def shader():
        i = int(0)
        while i < 10:
            i = i + 1
            if i % 2 == 0:
                continue
            x = float(i)
    
    glsl = compile_function(shader)
    assert "while (i < 10) {" in glsl
    assert "continue;" in glsl

# ==================== TESTS FOR LIST COMPREHENSIONS ====================

def test_list_comp_simple():
    """Test simple list comprehension."""
    def shader():
        arr = [i * 2 for i in range(5)]
    
    glsl = compile_function(shader)
    assert "int arr[5]" in glsl, f"Expected 'int arr[5]' in:\n{glsl}"
    assert "for (int i = 0; i < 5; i++) {" in glsl
    assert "arr[i] = (i * 2);" in glsl

def test_list_comp_with_filter():
    """Test list comprehension with if clause."""
    def shader():
        arr = [i for i in range(10) if i % 2 == 0]
    
    glsl = compile_function(shader)
    assert "int arr[10]" in glsl, f"Expected 'int arr[10]' in:\n{glsl}"
    assert "if ((i % 2) == 0) {" in glsl
    assert "arr[i] = i;" in glsl

def test_list_comp_with_expression():
    """Test list comprehension with complex expression."""
    def shader():
        squares = [i * i for i in range(8)]
    
    glsl = compile_function(shader)
    assert "int squares[8]" in glsl
    assert "squares[i] = (i * i);" in glsl

# ==================== TESTS FOR GEOMETRY SHADERS ====================

def test_geometry_shader_basic():
    """Test basic geometry shader with layout qualifiers."""
    from typing import Sequence, Iterator
    from pyglsl.glsl import geometry_shader_layout, triangles, triangle_strip, EmitVertex, EndPrimitive, GlGsIn
    
    class VsOut(ShaderInterface):
        color = vec4()
    
    class GsOut(ShaderInterface):
        gl_Position = vec4()
        color = vec4()
    
    @geometry_shader_layout(input_primitive=triangles,
                            output_primitive=triangle_strip,
                            max_vertices=3)
    def geom_shader(gl_in: Sequence[GlGsIn], vs_out: Sequence[VsOut]) -> Iterator[GsOut]:
        for i in range(3):
            yield GsOut(gl_Position=gl_in[i].gl_Position, color=vs_out[i].color)
        EndPrimitive()
    
    stage = GeometryStage(geom_shader)
    glsl = stage.compile()
    
    # Verify layout qualifiers
    assert "layout(triangles) in;" in glsl, f"Expected layout(triangles) in:\\n{glsl}"
    assert "layout(triangle_strip, max_vertices = 3) out;" in glsl
    
    # Verify input/output blocks
    assert "in VsOut {" in glsl
    assert "out GsOut {" in glsl
    
    # Verify EmitVertex and EndPrimitive
    assert "EmitVertex()" in glsl
    assert "EndPrimitive()" in glsl
    
    # Verify gl_Position assignments
    assert "gl_Position = gl_in[i].gl_Position;" in glsl or "gl_Position = gl_in[0].gl_Position;" in glsl

def test_geometry_shader_with_uniforms():
    """Test geometry shader with uniform blocks."""
    from typing import Sequence, Iterator
    from pyglsl.glsl import geometry_shader_layout, triangles, triangle_strip, EndPrimitive, GlGsIn
    
    class Params(UniformBlock):
        scale = float()
    
    class VsOut(ShaderInterface):
        normal = vec3()
    
    class GsOut(ShaderInterface):
        gl_Position = vec4()
        scaled_normal = vec3()
    
    @geometry_shader_layout(input_primitive=triangles,
                            output_primitive=triangle_strip,
                            max_vertices=3)
    def geom_shader(params: Params, gl_in: Sequence[GlGsIn], vs_out: Sequence[VsOut]) -> Iterator[GsOut]:
        yield GsOut(gl_Position=gl_in[0].gl_Position,
                    scaled_normal=vs_out[0].normal * params.scale)
        yield GsOut(gl_Position=gl_in[1].gl_Position,
                    scaled_normal=vs_out[1].normal * params.scale)
        yield GsOut(gl_Position=gl_in[2].gl_Position,
                    scaled_normal=vs_out[2].normal * params.scale)
        EndPrimitive()
    
    stage = GeometryStage(geom_shader)
    glsl = stage.compile()
    
    # Verify uniform declaration
    assert "uniform float scale;" in glsl, f"Expected uniform in:\\n{glsl}"
    
    # Verify interface blocks
    assert "in VsOut {" in glsl
    assert "out GsOut {" in glsl
    
    # Verify EmitVertex calls (should be 3)
    assert glsl.count("EmitVertex()") == 3
    
    # Verify uniform usage
    assert "(vs_out[0].normal * scale)" in glsl or "(vs_out[0].normal * params.scale)" in glsl

def test_geometry_shader_points_output():
    """Test geometry shader with points output."""
    from typing import Sequence, Iterator
    from pyglsl.glsl import geometry_shader_layout, triangles, points, GlGsIn
    
    class GsOut(ShaderInterface):
        gl_Position = vec4()
        size = float()
    
    @geometry_shader_layout(input_primitive=triangles,
                            output_primitive=points,
                            max_vertices=1)
    def geom_shader(gl_in: Sequence[GlGsIn]) -> Iterator[GsOut]:
        # Emit centroid
        center = vec4((gl_in[0].gl_Position + gl_in[1].gl_Position + gl_in[2].gl_Position).xyz / 3.0, 1.0)
        yield GsOut(gl_Position=center, size=1.0)
    
    stage = GeometryStage(geom_shader)
    glsl = stage.compile()
    
    # Verify layout qualifiers for points output
    assert "layout(triangles) in;" in glsl
    assert "layout(points, max_vertices = 1) out;" in glsl, f"Expected points layout in:\\n{glsl}"

def test_interpolation_qualifiers():
    """Test noperspective, flat, and smooth interpolation qualifiers."""
    from pyglsl.glsl import noperspective, flat, smooth
    
    class VsOut(ShaderInterface):
        barycentric = vec3(noperspective)
        instanceID = int(flat)
        normal = vec3(smooth)
        position = vec4()  # No qualifier (default)
    
    def shader() -> VsOut:
        return VsOut(
            barycentric=vec3(1.0, 0.0, 0.0),
            instanceID=int(0),
            normal=vec3(0.0, 1.0, 0.0),
            position=vec4(0.0)
        )
    
    glsl = compile_function(shader)
    
    # Verify interpolation qualifiers are present
    assert "noperspective vec3 barycentric;" in glsl, f"Expected 'noperspective vec3 barycentric;' in:\\n{glsl}"
    assert "flat int instanceID;" in glsl, f"Expected 'flat int instanceID;' in:\\n{glsl}"
    assert "smooth vec3 normal;" in glsl, f"Expected 'smooth vec3 normal;' in:\\n{glsl}"
    # No qualifier for position
    assert "vec4 position;" in glsl and "noperspective vec4 position;" not in glsl
