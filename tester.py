import glfw
from OpenGL.GL import *

def compile_shader(vertex: str, fragment: str) -> bool:
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, False)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    window = glfw.create_window(100, 100, "hidden", None, None)
    glfw.make_context_current(window)

    vertex_id = glCreateShader(GL_VERTEX_SHADER)
    fragment_id = glCreateShader(GL_FRAGMENT_SHADER)

    def make_shader(shader, src, name):
        glShaderSource(shader, src)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error_log = glGetShaderInfoLog(shader)
            if error_log:
                print(f"{name} shader compilation failed:\n{error_log}")
                return False
        return True

    if (not make_shader(vertex_id, vertex, "Vertex") or
        not make_shader(fragment_id, fragment, "Fragment")):
        return False

    program = glCreateProgram()
    glAttachShader(program, vertex_id)
    glAttachShader(program, fragment_id)
    glLinkProgram(program)

    if glGetProgramiv(program, GL_VALIDATE_STATUS) != GL_TRUE:
        error_log = glGetProgramInfoLog(program)
        if error_log:
            print(f"Program validation failed:\n{error_log}")
            return False

    print(vertex_id, fragment_id, program)
    glDeleteProgram(program)  # Deallocate program when finished
    glDeleteShader(vertex_id)  # Deallocate shaders
    glDeleteShader(fragment_id)
    glfw.terminate()
    return True