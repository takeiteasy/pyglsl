import pytest
from pyglsl.glsl import *
from pyglsl.stage import VertexStage
from pyglsl.parse import parse, MultipleReturnTransformer, GlslVisitor
import ast

def compile_function(func, stage_type=VertexStage):
    stage = stage_type(func)
    return stage.compile()

# ==================== TESTS FOR MULTIPLE RETURN STATEMENTS ====================

def test_multiple_returns_simple():
    """Test function with 2 return statements in if/else."""
    def shader(flag: bool) -> vec4:
        if flag:
            return vec4(1.0)
        else:
            return vec4(0.0)
    
    tree = parse(shader, return_type='vec4')
    visitor = GlslVisitor()
    glsl = visitor.visit(tree)
    glsl_code = '\n'.join(glsl.lines)
    
    # Should have temp variable declaration
    assert 'vec4 _return_value = vec4();' in glsl_code, f"Expected temp variable in:\\n{glsl_code}"
    # Should have assignments instead of returns in branches  
    assert '_return_value = vec4(1.0)' in glsl_code or '_return_value = vec4(1.0);' in glsl_code
    assert '_return_value = vec4(0.0)' in glsl_code or '_return_value = vec4(0.0);' in glsl_code
    # Should have single final return
    assert 'return _return_value' in glsl_code

def test_multiple_returns_early():
    """Test early return pattern."""
    def shader(x: float) -> float:
        if x < 0.0:
            return float(0.0)
        if x > 1.0:
            return float(1.0)
        return x
    
    tree = parse(shader, return_type='float')
    visitor = GlslVisitor()
    glsl = visitor.visit(tree)
    glsl_code = '\n'.join(glsl.lines)
    
    # Should have temp variable
    assert 'float _return_value = float();' in glsl_code, f"Expected temp variable in:\\n{glsl_code}"
    # Should have single final return
    assert glsl_code.count('return _return_value') == 1, f"Expected single return in:\\n{glsl_code}"

def test_single_return_unchanged():
    """Test that functions with single return aren't transformed."""
    def shader(x: float) -> float:
        return x * 2.0
    
    tree = parse(shader, return_type='float')
    visitor = GlslVisitor()
    glsl = visitor.visit(tree)
    glsl_code = '\n'.join(glsl.lines)
    
    # Should NOT have temp variable (single return, no transformation)
    assert '_return_value' not in glsl_code, f"Should not transform single return:\\n{glsl_code}"
    # Should have original return
    assert 'return (x * 2.0)' in glsl_code

def test_no_return_unchanged():
    """Test that functions with no return aren't transformed."""
    def shader():
        a = vec3(1.0)
    
    tree = parse(shader)
    visitor = GlslVisitor()
    glsl = visitor.visit(tree)
    glsl_code = '\n'.join(glsl.lines)
    
    # Should NOT have temp variable
    assert '_return_value' not in glsl_code

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
