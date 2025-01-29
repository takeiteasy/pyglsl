from typing import Optional, Union, Sequence, get_type_hints
from .parse import parse, GlslVisitor

class Stage:
    def __init__(self, func, version: Optional[Union[str, int]] = "330 core"):
        self.root = parse(func)
        self.params = get_type_hints(func)
        self.params.pop("return", None)
        self.return_type = get_type_hints(func).get('return')
        self.lines = [f"#version {version}"]

    def declare_inputs(self, lines):
        for name, param_type in sorted(self._params.items()):
            # TODO(nicholasbishop): dedup with return type
            origin = getattr(param_type, '__origin__', None)
            array = None
            if origin is not None and origin == Sequence:
                param_type = param_type.__parameters__[0]
                array = True
            lines += param_type.declare_input_block(instance_name=name,
                                                    array=array)

    def translate(self):
        visitor = GlslVisitor()
        for name, ptype in sorted(self.params.items()):
            origin = getattr(ptype, "__origin__", None)
            is_array = None
            if origin is not None and origin == Sequence:
                ptype = ptype.__parameters__[0]
                array = True
            self.lines += ptype.declare_input_block(instance_name=name,
                                                    array=is_array)

        self.lines.extend(visitor.visit(self.root).lines)
        pass