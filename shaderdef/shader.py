from shaderdef.ast_util import (make_assign,
                                make_self_attr_load,
                                make_self_attr_store,
                                rename_function)
from shaderdef.find_method import find_method_ast
from shaderdef.glsl_types import Attribute, FragOutput, Uniform
from shaderdef.material import create_stages, find_external_links
from shaderdef.stage import make_prefix


class ShaderDef(object):
    def __init__(self, material):
        self._material = material

        self._stages = []
        self._external_links = None
        self._vert_shader = None
        self._frag_shader = None

    def _thread_deps(self):
        """Link inputs and outputs between stages."""
        iter1 = reversed(self._stages)
        iter2 = reversed(self._stages)
        next(iter2)
        for stage, prev_stage in zip(iter1, iter2):
            stage.input_prefix = make_prefix(prev_stage.name)
            prev_stage.provide_deps(stage)

    def translate(self):
        self._stages = list(create_stages(self._material))
        self._external_links = find_external_links(self._material)

        self._thread_deps()

        # TODO
        self._vert_shader = self._stages[0].to_glsl(self._external_links)
        self._frag_shader = self._stages[1].to_glsl(self._external_links)

    @property
    def vert_shader(self):
        # TODO: declare inputs/outputs
        return self._vert_shader

    @property
    def frag_shader(self):
        # TODO: declare inputs/outputs
        return self._frag_shader
