from typing import Callable, Any
from .stage import Stage

class Compiler:
    def __init__(self, vert: Callable[..., Any], frag: Callable[..., Any], **kwargs):
        self.vertex = Stage(vert)
        self.fragment = Stage(frag)
