import pytest
from typing import Sequence, Iterator
from pyglsl.glsl import *
from pyglsl.stage import TessControlStage, TessEvalStage

def compile_function(func, stage_type):
    stage = stage_type(func)
    return stage.compile()

# ==================== TESSELLATION CONTROL SHADER TESTS ====================

def test_tess_control_basic():
    """Test basic tessellation control shader."""
    
    class TcsOut(ShaderInterface):
        pos = vec3()
        
    @tessellation_control_layout(vertices=3)
    def tcs_shader(gl_in: Sequence[GlTessIn]) -> TcsOut:
        # Set tessellation levels
        gl_TessLevelInner[0] = 3.0
        gl_TessLevelOuter[0] = 2.0
        
        # Pass through position
        return TcsOut(pos=gl_in[gl_InvocationID].gl_Position.xyz)
        
    glsl = compile_function(tcs_shader, TessControlStage)
    
    assert "layout(vertices = 3) out;" in glsl
    assert "gl_TessLevelInner[0] = 3.0;" in glsl
    assert "gl_TessLevelOuter[0] = 2.0;" in glsl
    
    # Check output assignment with index
    # The exact format depends on how we implemented the rewriter
    # Expected: tcs_out[gl_InvocationID].pos = ...
    assert "tcs_out[gl_InvocationID].pos = gl_in[gl_InvocationID].gl_Position.xyz;" in glsl

def test_tess_control_with_uniforms():
    """Test TCS with uniform blocks."""
    
    class Params(UniformBlock):
        tess_level = float()
        
    class TcsOut(ShaderInterface):
        pos = vec3()
        
    @tessellation_control_layout(vertices=4)
    def tcs_shader(params: Params, gl_in: Sequence[GlTessIn]) -> TcsOut:
        gl_TessLevelInner[0] = params.tess_level
        gl_TessLevelOuter[0] = params.tess_level
        return TcsOut(pos=gl_in[gl_InvocationID].gl_Position.xyz)
        
    glsl = compile_function(tcs_shader, TessControlStage)
    
    assert "uniform float tess_level;" in glsl
    assert "gl_TessLevelInner[0] = tess_level;" in glsl

# ==================== TESSELLATION EVALUATION SHADER TESTS ====================

def test_tess_eval_triangles():
    """Test TES with triangles primitive mode."""
    
    class TesOut(ShaderInterface):
        gl_Position = vec4()
        
    @tessellation_evaluation_layout(primitive_mode=triangles,
                                    spacing=equal_spacing,
                                    vertex_order=ccw)
    def tes_shader(gl_in: Sequence[GlTessIn]) -> TesOut:
        # Barycentric interpolation
        p0 = vec4(gl_in[0].gl_Position)
        p1 = vec4(gl_in[1].gl_Position)
        p2 = vec4(gl_in[2].gl_Position)
        
        pos = p0 * gl_TessCoord.x + p1 * gl_TessCoord.y + p2 * gl_TessCoord.z
        return TesOut(gl_Position=pos)
        
    glsl = compile_function(tes_shader, TessEvalStage)
    
    assert "layout(triangles, equal_spacing, ccw) in;" in glsl
    assert "vec4 p0 = vec4(gl_in[0].gl_Position);" in glsl
    assert "gl_Position = pos;" in glsl

def test_tess_eval_quads():
    """Test TES with quads primitive mode."""
    
    class TesOut(ShaderInterface):
        gl_Position = vec4()
        
    @tessellation_evaluation_layout(primitive_mode=quads,
                                    spacing=fractional_even_spacing,
                                    vertex_order=cw)
    def tes_shader(gl_in: Sequence[GlTessIn]) -> TesOut:
        return TesOut(gl_Position=vec4(gl_TessCoord, 1.0))
        
    glsl = compile_function(tes_shader, TessEvalStage)
    
    assert "layout(quads, fractional_even_spacing, cw) in;" in glsl
    assert "gl_Position = vec4(gl_TessCoord, 1.0);" in glsl

def test_tess_eval_isolines():
    """Test TES with isolines primitive mode."""
    
    class TesOut(ShaderInterface):
        gl_Position = vec4()
        
    @tessellation_evaluation_layout(primitive_mode=isolines)
    def tes_shader(gl_in: Sequence[GlTessIn]) -> TesOut:
        return TesOut(gl_Position=vec4(gl_TessCoord.x, 0.0, 0.0, 1.0))
        
    glsl = compile_function(tes_shader, TessEvalStage)
    
    # Default spacing and order
    assert "layout(isolines, equal_spacing, ccw) in;" in glsl

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
