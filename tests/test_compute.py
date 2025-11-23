import pytest
from pyglsl.glsl import *
from pyglsl.stage import ComputeStage

def compile_function(func, stage_type=ComputeStage):
    stage = stage_type(func)
    return stage.compile()

# ==================== COMPUTE SHADER TESTS ====================

def test_compute_basic():
    """Test basic compute shader with local size."""
    
    @compute_shader_layout(local_size_x=16, local_size_y=16)
    def cs_shader():
        idx = uvec2(gl_GlobalInvocationID.xy)
        
    glsl = compile_function(cs_shader)
    
    assert "layout(local_size_x = 16, local_size_y = 16, local_size_z = 1) in;" in glsl
    assert "uvec2 idx = uvec2(gl_GlobalInvocationID.xy);" in glsl

def test_compute_shared_memory():
    """Test shared memory declaration."""
    
    @compute_shader_layout(local_size_x=1)
    def cs_shader():
        # Shared memory declaration
        data = shared(float[256])
        
        data[gl_LocalInvocationID.x] = 1.0
        barrier()
        
    glsl = compile_function(cs_shader)
    
    assert "shared float data[256];" in glsl
    assert "data[gl_LocalInvocationID.x] = 1.0;" in glsl
    assert "barrier();" in glsl

def test_compute_atomics():
    """Test atomic operations."""
    
    class Buffer(UniformBlock):
        counter = uint()
        
    @compute_shader_layout(local_size_x=1)
    def cs_shader(buf: Buffer):
        old = uint(atomicAdd(buf.counter, uint(1)))
        
    glsl = compile_function(cs_shader)
    
    assert "uint old = uint(atomicAdd(counter, uint(1)));" in glsl

def test_compute_image_load_store():
    """Test image load/store operations."""
    
    class Images(UniformBlock):
        img_in = image2D()
        img_out = image2D()
        
    @compute_shader_layout(local_size_x=16, local_size_y=16)
    def cs_shader(imgs: Images):
        pos = ivec2(gl_GlobalInvocationID.xy)
        color = vec4(imageLoad(imgs.img_in, pos))
        imageStore(imgs.img_out, pos, color)
        
    glsl = compile_function(cs_shader)
    
    assert "vec4 color = vec4(imageLoad(img_in, pos));" in glsl
    assert "imageStore(img_out, pos, color);" in glsl

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
