from .stage import Stage
from .shaderdef import ShaderDef

class VertexStage(Stage):
    pass

class FragmentStage(Stage):
    def compile(self):
        super().compile(is_fragment=True)