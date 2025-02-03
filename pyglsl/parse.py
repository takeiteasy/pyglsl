# Purely pythonic fast first-rate fully-functioning flexible feature-rich framework for fun
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
from .types import ArraySpec

class GlslCode(object):
    def __init__(self, initial_line=None):
        self.lines = []
        if initial_line is not None:
            self.lines.append(initial_line)
        self._indent_string = '    '

    def __call__(self, line):
        self.lines.append(line)

    def append_block(self, code):
        for line in code.lines:
            line = self._indent_string + line
            if line[-1] not in (';', '{', '}'):
                line += ';'
            self.lines.append(line)

    def one(self):
        if len(self.lines) != 1:
            raise ValueError('expected exactly one line', self)
        return self.lines[0]

def op_symbol(op_node):
    """Get the GLSL symbol for a Python operator."""
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
        ast.Eq: '=',
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

    def visit_Pass(self, _):
        # pylint: disable=no-self-use
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

    def visit_Name(self, node):
        # pylint: disable=no-self-use
        return GlslCode(node.id)

    def visit_Attribute(self, node):
        return GlslCode('{}{}'.format(self.visit(node.value).one() + "." if hasattr(node, "value") else "", node.attr))

    @staticmethod
    def is_var_decl(node):
        target = node.targets[0]
        return (isinstance(target, ast.Name) and
                not target.id.startswith('gl_') and
                isinstance(node.value, ast.Call))

    def get_array_decl(self, node):
        # TODO(nicholasbishop): clean mess up
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

    def visit_Num(self, node):
        # pylint: disable=no-self-use
        return GlslCode(str(node.n))

    def visit_Call(self, node):
        args = (self.visit(arg).one() for arg in node.args)
        name = self.visit(node.func).one()
        return GlslCode('{}({})'.format(name, ', '.join(args)))

    def visit_Return(self, node):
        return GlslCode('return {}'.format(self.visit(node.value).one()))

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Str(self, node):
        # pylint: disable=no-self-use,unused-argument
        return GlslCode()

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
        return GlslCode('{}[{}]'.format(self.visit(node.value).one(),
                                        self.visit(node.slice).one()))

    def visit_Index(self, node):
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
        # TODO(nicholasbishop): emit "else if" to make output cleaner
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
        if len(itr.args) != 1 or not isinstance(itr.args[0], ast.Num):
            raise NotImplementedError('only 0..n for loops are supported')
        end = self.visit(itr.args[0]).one()
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
            raise ValueError(ast.dump(node))
        return glsl

def dedent(lines):
    """De-indent based on the first line's indentation."""
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
