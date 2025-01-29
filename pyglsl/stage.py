import ast
from typing import Union, Sequence, List, Callable, Any, get_type_hints
from .parse import parse, GlslVisitor

class NoDeclAssign(ast.Assign):
    """Mark an assignment as one that doesn't need to be declared.

    For example, `return Output(pos=vec2(0, 1))` should have GLSL output
       pos = vec2(0, 1);
    instead of
       vec2 pos = vec2(0, 1);
    """
    pass

def kwargs_as_assignments(call_node, parent):
    """Yield NoDeclAssign nodes from kwargs in a Call node."""
    if not isinstance(call_node, ast.Call):
        raise TypeError('node must be an ast.Call')

    if len(call_node.args) > 0:
        raise ValueError('positional args not allowed')

    for keyword in call_node.keywords:
        dst_name = keyword.arg

        if dst_name.startswith('gl_'):
            # Write to builtins directly
            target = [ast.Name(id=keyword.arg, ctx=ast.Load())]
        else:
            # Non-builtins are part of an interface block
            target = [ast.Attribute(value=parent, attr=keyword.arg,
                                    ctx=ast.Store())]

        yield NoDeclAssign(targets=target, value=keyword.value)

class _RewriteReturn(ast.NodeTransformer):
    def __init__(self, interface):
        self.interface = interface

    def _output_to_list(self, node):
        parent = ast.Name(id=self.interface.instance_name(), ctx=ast.Load())
        return list(kwargs_as_assignments(node.value, parent))

    def visit_Return(self, node):  # pylint: disable=invalid-name
        return self._output_to_list(node)

    def visit_Expr(self, node):  # pylint: disable=invalid-name
        if isinstance(node.value, ast.Yield):
            lst = self._output_to_list(node.value)
            lst.append(ast.parse('EmitVertex()'))
            return lst
        else:
            return node

class _Renamer(ast.NodeTransformer):
    # pylint: disable=invalid-name
    def __init__(self, names):
        self.names = names

    def visit_Name(self, node):
        new_name = self.names.get(node.id)
        if new_name is not None:
            node.id = new_name
        return node

    def visit_Attribute(self, node):
        node.value = self.visit(node.value)

        new_name = self.names.get(node.attr)
        if new_name is not None:
            node.attr = new_name

        return node


def rename_ast_nodes(root_node, names):
    return _Renamer(names).visit(root_node)

class Stage:
    def __init__(self, func: Callable[..., Any]):
        self.root = parse(func)
        self.params = get_type_hints(func)
        self.params.pop("return", None)
        self.return_type = get_type_hints(func).get('return')

    def translate(self, version: Union[str, int], library: List[Callable[..., Any]]):
        lines = [f"#version {version}\n"]
        visitor = GlslVisitor()

        for name, ptype in sorted(self.params.items()):
            origin = getattr(ptype, "__origin__", None)
            is_array = None
            if origin is not None and origin == Sequence:
                ptype = ptype.__parameters__[0]
                is_array = True
            lines += ptype.declare_input_block(instance_name=name,
                                               array=is_array)

        # TODO(nicholasbishop): for now we don't attempt to check if
        # the function is actually used, just define them all
        for f in library:
            lines.extend(GlslVisitor().visit(parse(f)).lines)

        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
        node.name = "main"
        node.args.args = []
        node.returns = None

        node = _RewriteReturn(self.return_type).visit(node)
        ast.fix_missing_locations(node)
        node = _Renamer({'gl_position': 'gl_Position'}).visit(node)

        if self.return_type is not None:
            lines += self.return_type.declare_output_block()

        return lines + visitor.visit(self.root).lines