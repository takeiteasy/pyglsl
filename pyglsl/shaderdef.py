from dataclasses import dataclass, field
from typing import Callable, Any, Optional, List, Union
from .stage import Stage

@dataclass
class ShaderDef:
    vertex_shader: Callable[..., Any]
    fragment_shader: Callable[..., Any]
    version: Optional[Union[str, int]] = "330 core"
    vertex_functions: Optional[List[Callable[..., Any]]] = field(default_factory=list)
    fragment_functions: Optional[List[Callable[..., Any]]] = field(default_factory=list)

    def compile(self):
        v = Stage(self.vertex_shader, self.version, self.vertex_functions)
        f = Stage(self.fragment_shader, self.version, self.fragment_functions)
        return v.compile(), f.compile(is_fragment=True)