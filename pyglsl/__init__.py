from typing import Callable, Any, Optional, Union, List
from .stage import Stage

class GlslCompilerException(Exception):
    def __str__(self):
        return "Source hasn't been compiled, execute Compiler.compile() first"

class Compiler:
    def __init__(self,
                 vert: Callable[..., Any],
                 frag: Callable[..., Any],
                 geom: Optional[Callable[..., Any]] = None,
                 version: Optional[Union[str, int]] = "330 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        self.vertex_stage = Stage(vert)
        self.fragment_stage = Stage(frag)
        self.geometry_stage = Stage(geom) if geom else None
        self._vertex = None
        self._fragment = None
        self._geometry = None
        self.version = version
        self.library = library

    @property
    def vertex_source(self):
        if not self._vertex:
            raise GlslCompilerException()
        return self._vertex

    @property
    def fragment_source(self):
        if not self._fragment:
            raise GlslCompilerException()
        return self._fragment

    @property
    def geometry_source(self):
        if not self._geometry and self.geometry_stage:
            raise GlslCompilerException()
        return self._geometry

    def add_function(self, func: Union[Callable[..., Any], List[Callable[..., Any]]]):
        self.library = list(set(self.library + (func if isinstance(func, list) else [func])))

    def compile(self):
        self._vertex = self.vertex_stage.translate(self.version, self.library)
        self._fragment = self.fragment_stage.translate(self.version, self.library)
        if self.geometry_stage:
            self._geometry = self.fragment_stage.translate(self.version, self.library)
        def j(lines):
            return '\n'.join(lines) if lines else None
        return j(self._vertex), j(self._fragment), j(self._geometry)

