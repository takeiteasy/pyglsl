# pyglsl -- https://github.com/takeiteasy/pyglsl
#
# Copyright (C) 2016 Nicholas Bishop
# Copyright (C) 2025 George Watson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ast
from inspect import getsource
from typing import Generator
from .types import ArraySpec
from .constants import GLSL_INDENT, GLSL_STATEMENT_TERMINATORS, GLSL_BUILTIN_TYPES

class GlslCode:
    """Accumulator for generated GLSL source code lines.
    
    This class manages the collection of GLSL code lines with automatic
    indentation and statement termination.
    
    Example:
        >>> code = GlslCode('void main() {')
        >>> code('    vec3 pos = vec3(0.0);')
        >>> code('}')
        >>> print('\\n'.join(code.lines))
        void main() {
            vec3 pos = vec3(0.0);
        }
    """
    def __init__(self, initial_line=None):
        self.lines = []
        if initial_line is not None:
            self.lines.append(initial_line)
        self._indent_string = GLSL_INDENT

    def __call__(self, line):
        self.lines.append(line)

    def append_block(self, code):
        for line in code.lines:
            line = self._indent_string + line
            if line[-1] not in GLSL_STATEMENT_TERMINATORS:
                line += ';'
            self.lines.append(line)

    def one(self):
        if len(self.lines) != 1:
            raise ValueError('expected exactly one line', self)
        return self.lines[0]

def op_symbol(op_node: ast.AST) -> str:
    """Get the GLSL symbol for a Python operator.
    
    Args:
        op_node: An AST operator node (UnaryOp, BinOp, BoolOp, or Comparison)
    
    Returns:
        The corresponding GLSL operator symbol
    """
    ops = {
        # UnaryOp
        ast.UAdd: '+',
        ast.USub: '-',
        ast.Not: '!',
        # BinOp
        ast.Add: '+',
        ast.Sub: '-',
        ast.Mult: '*',
        ast.MatMult: '*',
        ast.Div: '/',
        ast.Mod: '%',
        ast.LShift: '<<',
        ast.RShift: '>>',
        ast.BitOr: '|',
        ast.BitXor: '^',
        ast.BitAnd: '&',
        # BoolOp
        ast.And: '&&',
        ast.Or: '||',
        # Comparison
        ast.Eq: '==',
        ast.NotEq: '!=',
        ast.Lt: '<',
        ast.LtE: '<=',
        ast.Gt: '>',
        ast.GtE: '>=',
        ast.Is: '==',
        ast.IsNot: '!='
    }
    return ops[op_node.__class__]

class GlslVisitor(ast.NodeVisitor):
    """AST visitor that translates Python code to GLSL.
    
    This visitor walks a Python AST and generates GLSL source code. It handles
    a subset of Python syntax that maps cleanly to GLSL constructs.
    
    Supported Python features:
        - Function definitions with type hints
        - Variable assignments and declarations
        - Arithmetic and comparison operators
        - if/else conditionals
        - for loops with range()
        - break and continue statements
        - Function calls
        - Attribute access and subscripting
    
    Unsupported features (will raise NotImplementedError):
        - while loops
        - with statements
        - try/except blocks
        - lambda functions
        - List/dict/set comprehensions
        - Generator expressions
    
    Example:
        >>> import ast
        >>> def shader():
        ...     x = vec3(1.0, 2.0, 3.0)
        ...     return x
        >>> visitor = GlslVisitor()
        >>> tree = parse(shader)
        >>> glsl = visitor.visit(tree)
    """
    def visit_Module(self, node):
        if len(node.body) != 1:
            raise NotImplementedError()
        child = node.body[0]
        return self.visit(child)

    def visit_FunctionDef(self, node):
        if getattr(node, 'returns', None) is None:
            return_type = 'void'
        else:
            return_type = self.visit(node.returns).one()
        params = node.args.args[:]
        # Skip self
        if len(params) != 0 and params[0].arg == 'self':
            params = params[1:]
        params = (self.visit(param).one() for param in params)
        code = GlslCode()
        code('{} {}({}) {{'.format(return_type, node.name,
                                   ', '.join(params)))
        for child in node.body:
            code.append_block(self.visit(child))
        code('}')
        return code

    @staticmethod
    def visit_Pass(_):
        return GlslCode()

    def visit_arg(self, node):
        if node.annotation is None:
            raise ValueError('untyped argument: {}'.format(ast.dump(node)))
        adecl = ArraySpec.from_ast_node(node.annotation)
        if adecl is not None:
            return GlslCode('{} {}[{}]'.format(adecl.element_type, node.arg,
                                               adecl.length))

        gtype = self.visit(node.annotation).one()
        return GlslCode('{} {}'.format(gtype, node.arg))

    @staticmethod
    def visit_Name(node):
        return GlslCode(node.id)

    def visit_Attribute(self, node):
        return GlslCode('{}{}'.format(self.visit(node.value).one() + "." if hasattr(node, "value") else "", node.attr))

    @staticmethod
    def is_var_decl(node):
        target = node.targets[0]
        if not (isinstance(target, ast.Name) and
                not target.id.startswith('gl_') and
                isinstance(node.value, ast.Call)):
            return False
            
        # Check if the function being called looks like a type constructor
        func_name = node.value.func.id
        
        # Check against known GLSL types or user-defined types (capitalized)
        return func_name in GLSL_BUILTIN_TYPES or (len(func_name) > 0 and func_name[0].isupper())

    def get_array_decl(self, node):
        target = node.targets[0]
        aspec = ArraySpec.from_ast_node(node.value)
        if aspec is None:
            return None
        return GlslCode('{} {}[{}]'.format(aspec.element_type,
                                           self.visit(target).one(),
                                           aspec.length))

    def make_var_decl(self, node):
        target = node.targets[0]
        gtype = node.value.func.id
        return GlslCode('{} {} = {}'.format(gtype,
                                            self.visit(target).one(),
                                            self.visit(node.value).one()))

    def visit_NoDeclAssign(self, node):
        return self.visit_Assign(node, allow_decl=False)

    def visit_Assign(self, node, allow_decl=True):
        if len(node.targets) != 1:
            raise ValueError('multiple assignment targets not allowed', node)
        target = node.targets[0]
        if allow_decl and self.is_var_decl(node):
            return self.make_var_decl(node)
        adecl = self.get_array_decl(node)
        if adecl is not None:
            return adecl
        return GlslCode('{} = {}'.format(self.visit(target).one(),
                                         self.visit(node.value).one()))

    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            return GlslCode('true' if node.value else 'false')
        elif isinstance(node.value, (int, float)):
            return GlslCode(str(node.value))
        elif isinstance(node.value, str):
            return GlslCode() # Strings are ignored/empty in GLSL context usually, or handled elsewhere? 
            # visit_Str returned GlslCode(), so we do the same.
        elif node.value is None:
             return GlslCode('null') # Or whatever GLSL equivalent, or maybe empty.
        else:
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

    def visit_Num(self, node):
        # Keep for backward compatibility if running on older python (unlikely with 3.13 but good practice)
        return GlslCode(str(node.n))

    def visit_Str(self, node):
        return GlslCode()

    def visit_Call(self, node):
        args = (self.visit(arg).one() for arg in node.args)
        name = self.visit(node.func).one()
        return GlslCode('{}({})'.format(name, ', '.join(args)))

    def visit_Return(self, node):
        return GlslCode('return {}'.format(self.visit(node.value).one()))

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_UnaryOp(self, node):
        return GlslCode('{}{}'.format(op_symbol(node.op),
                                      self.visit(node.operand).one()))

    def visit_BinOp(self, node):
        return GlslCode('({} {} {})'.format(
            self.visit(node.left).one(),
            op_symbol(node.op),
            self.visit(node.right).one(),
        ))

    def visit_Subscript(self, node):
        # Handle Python < 3.9 ast.Index if present, otherwise use slice directly
        slice_node = node.slice
        if isinstance(slice_node, ast.Index):
             slice_val = slice_node.value
        else:
             slice_val = slice_node
        return GlslCode('{}[{}]'.format(self.visit(node.value).one(),
                                        self.visit(slice_val).one()))

    def visit_Index(self, node):
        # Deprecated in 3.9, but might still be present in older ASTs or if we manually construct
        return GlslCode('[{}]'.format(self.visit(node.value).one()))

    def visit_AugAssign(self, node):
        return GlslCode('{} {}= {}'.format(self.visit(node.target).one(),
                                           op_symbol(node.op),
                                           self.visit(node.value).one()))

    def visit_Compare(self, node):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise NotImplementedError('only one op/comparator is supported',
                                      node)
        op = node.ops[0]
        right = node.comparators[0]
        return GlslCode('{} {} {}'.format(self.visit(node.left).one(),
                                          op_symbol(op),
                                          self.visit(right).one()))

    def visit_If(self, node):
        code = GlslCode('if ({}) {{'.format(self.visit(node.test).one()))
        for child in node.body:
            code.append_block(self.visit(child))
        if len(node.orelse) != 0:
            code('} else {')
            for child in node.orelse:
                code.append_block(self.visit(child))
        code('}')
        return code

    def visit_For(self, node):
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError('for-loop target must be an ast.Name')
        itr = node.iter
        if not isinstance(itr, ast.Call) or itr.func.id != 'range':
            raise NotImplementedError('only range() for loops are supported')
        
        # Handle both Num (old) and Constant (new)
        if len(itr.args) != 1:
             raise NotImplementedError('only 0..n for loops are supported')
        
        arg = itr.args[0]
        if isinstance(arg, ast.Num):
            end_val = str(arg.n)
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
            end_val = str(arg.value)
        else:
            raise NotImplementedError('only 0..n for loops are supported')

        end = end_val # We already got the string value
        var = self.visit(node.target).one()
        code = GlslCode()
        code('for (int {var} = 0; {var} < {end}; {var}++) {{'.format(var=var,
                                                                     end=end))
        for child in node.body:
            code.append_block(self.visit(child))
        code('}')
        return code

    def visit(self, node):
        glsl = super().visit(node)
        if not glsl:
            # Node type not handled - raise informative error
            node_type = node.__class__.__name__
            raise NotImplementedError(
                f"Unsupported Python construct '{node_type}' cannot be translated to GLSL. "
                f"Check the documentation for supported syntax."
            )
        return glsl

    # Explicit handlers for unsupported constructs with helpful messages
    def visit_While(self, node):
        raise NotImplementedError(
            "while loops are not supported in GLSL. "
            "Use 'for i in range(...)' instead."
        )

    def visit_With(self, node):
        raise NotImplementedError(
            "'with' statements are not supported in GLSL. "
            "Context managers have no equivalent in shader code."
        )

    def visit_Try(self, node):
        raise NotImplementedError(
            "try/except blocks are not supported in GLSL. "
            "Shaders do not support exception handling."
        )

    def visit_Lambda(self, node):
        raise NotImplementedError(
            "Lambda functions are not supported. "
            "Define a regular function instead."
        )

    def visit_ListComp(self, node):
        raise NotImplementedError(
            "List comprehensions are not supported in GLSL. "
            "Use explicit for loops instead."
        )

    def visit_DictComp(self, node):
        raise NotImplementedError(
            "Dictionary comprehensions are not supported in GLSL."
        )

    def visit_SetComp(self, node):
        raise NotImplementedError(
            "Set comprehensions are not supported in GLSL."
        )

    def visit_GeneratorExp(self, node):
        raise NotImplementedError(
            "Generator expressions are not supported in GLSL."
        )

    def visit_Break(self, node):
        return GlslCode('break')

    def visit_Continue(self, node):
        return GlslCode('continue')

def dedent(lines: list[str]) -> Generator[str, None, None]:
    """De-indent based on the first line's indentation.
    
    Args:
        lines: List of source code lines
    
    Yields:
        De-indented lines
    
    Raises:
        ValueError: If any line has less indentation than the first line
    """
    if len(lines) != 0:
        first = lines[0].lstrip()
        strip_len = len(lines[0]) - len(first)
        for line in lines:
            if len(line[:strip_len].strip()) != 0:
                raise ValueError('less indentation than first line: ' +
                                 line)
            else:
                yield line[strip_len:]

def parse(func):
    return ast.parse('\n'.join(dedent(getsource(func).splitlines())))
