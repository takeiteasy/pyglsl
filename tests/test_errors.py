"""Test that unsupported Python constructs raise helpful errors."""
import pytest
from pyglsl.stage import VertexStage


def test_while_loop_error():
    """while loops should raise informative error."""
    def shader():
        i = int(0)
        while i < 10:
            i += 1
    
    with pytest.raises(NotImplementedError, match="while loops are not supported"):
        VertexStage(shader).compile()

def test_list_comprehension_error():
    """List comprehensions should raise informative error."""
    def shader():
        values = [i * 2 for i in range(10)]
    
    with pytest.raises(NotImplementedError, match="List comprehensions are not supported"):
        VertexStage(shader).compile()


def test_with_statement_error():
    """'with' statements should raise informative error."""
    def shader():
        with open("file.txt") as f:
            pass
    
    with pytest.raises(NotImplementedError, match="'with' statements are not supported"):
        VertexStage(shader).compile()


def test_try_except_error():
    """try/except should raise informative error."""
    def shader():
        try:
            x = float(1.0)
        except:
            x = float(0.0)
    
    with pytest.raises(NotImplementedError, match="try/except blocks are not supported"):
        VertexStage(shader).compile()


def test_break_continue_support():
    """break and continue should be supported."""
    def shader():
        for i in range(10):
            if i == 5:
                break
            if i == 3:
                continue
            x = float(i)
    
    glsl = VertexStage(shader).compile()
    assert "break;" in glsl
    assert "continue;" in glsl
