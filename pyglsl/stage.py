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
import inspect
from typing import Optional, Union, Sequence, List, Callable, Any, get_type_hints
from .constants import GLSL_BUILTIN_RENAMES
from pyglsl.interface import snake_case, ShaderInterface
from pyglsl.parse import parse, GlslVisitor

class NoDeclAssign(ast.Assign):
    """Mark an assignment as one that doesn't need to be declared.

    For example, `return Output(pos=vec2(0, 1))` should have GLSL output
       pos = vec2(0, 1);
    instead of
       vec2 pos = vec2(0, 1);
    """
    pass

def kwargs_as_assignments(call_node: ast.Call, parent: ast.AST):
    """Yield NoDeclAssign nodes from kwargs in a Call node.
    
    Args:
        call_node: AST Call node containing keyword arguments
        parent: Parent AST node for attribute generation
    
    Yields:
        NoDeclAssign instances for each keyword argument
    
    Raises:
        TypeError: If call_node is not an ast.Call
        ValueError: If positional arguments are present
    """
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
        x = list(kwargs_as_assignments(node.value, parent))
        return x

    def visit_Return(self, node):
        return self._output_to_list(node)

    def visit_Expr(self, node):
        return node

class _Renamer(ast.NodeTransformer):
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

class _Remover(ast.NodeTransformer):
    def __init__(self, names):
        self.names = names

    def visit_Attribute(self, node):
        if hasattr(node, "value"):
            if isinstance(node.value, ast.Attribute):
                node.value = self.visit(node.value)
            elif isinstance(node.value, ast.Name) and node.value.id in self.names:
                return ast.Name(id=node.attr, ctx=node.ctx)
        return node

class Stage:
    """Base class for shader compilation stages.
    
    Orchestrates the transformation of Python functions into GLSL shader code.
    Handles type hint extraction, interface block generation, AST transformations,
    and code generation.
    
    Args:
        func: Python function to compile into a shader
        version: GLSL version string (default: "330 core")
        library: Optional list of helper functions to include in the shader
    
    Example:
        >>> from pyglsl.glsl import vec3, vec4
        >>> from pyglsl.interface import AttributeBlock
        >>> 
        >>> class Input(AttributeBlock):
        ...     position = vec3()
        >>> 
        >>> def vert_shader(input: Input) -> None:
        ...     gl_Position = vec4(input.position, 1.0)
        >>> 
        >>> stage = Stage(vert_shader)
        >>> glsl_code = stage.compile()
    """
    def __init__(self,
                 func: Callable[..., Any],
                 version: Optional[Union[str, int]] = "330 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        self.library = library
        self.version = version
        self.func = func  # Store original function for struct collection
        self.root = parse(func)
        self.params = get_type_hints(func)
        self.params.pop("return", None)
        self.return_type = get_type_hints(func).get('return')

    def add_function(self, func: Union[Callable[..., Any], List[Callable[..., Any]]]):
        self.library = list(set(self.library + (func if isinstance(func, list) else [func])))

    def collect_struct_definitions(self, func):
        """Collect all GlslStruct subclass definitions used in the function.
        
        Args:
            func: The shader function to analyze
            
        Returns:
            List of GlslStruct subclasses found in the function's scope
        """
        from .types import GlslStruct
        import inspect
        
        structs = []
        seen_names = set()
        
        # Get the function's global scope
        if hasattr(func, '__globals__'):
            for name, value in func.__globals__.items():
                # Check if it's a class and a subclass of GlslStruct
                if (inspect.isclass(value) and 
                    issubclass(value, GlslStruct) and 
                    value is not GlslStruct):
                    structs.append(value)
                    seen_names.add(value.__name__)
        
        # Also check the current frame's locals (for structs defined in test functions)
        frame = inspect.currentframe()
        try:
            # Walk up the call stack to find structs in calling scopes
            for _ in range(10):  # Limit depth to avoid infinite loops
                if frame is None:
                    break
                frame_locals = frame.f_locals
                for name, value in frame_locals.items():
                    if (inspect.isclass(value) and 
                        issubclass(value, GlslStruct) and 
                        value is not GlslStruct and
                        value.__name__ not in seen_names):
                        structs.append(value)
                        seen_names.add(value.__name__)
                frame = frame.f_back
        finally:
            del frame  # Avoid reference cycles
        
        return structs

    def compile(self, is_fragment: Optional[bool] = False):
        lines = [f"#version {self.version}"]
        visitor = GlslVisitor()
        
        # Collect and emit struct definitions before everything else
        struct_classes = self.collect_struct_definitions(self.func)
        # Get the original function from self.root
        if hasattr(self, 'params'):
            # Extract structs from parameter types as well
            for ptype in self.params.values():
                origin_type = getattr(ptype, "__origin__", None)
                if origin_type is not None:
                    # Unwrap generic types
                    from typing import get_args
                    args = get_args(ptype)
                    if args:
                        ptype = args[0]
                
                # Check if ptype itself is a struct
                from .types import GlslStruct
                import inspect
                if (inspect.isclass(ptype) and 
                    issubclass(ptype, GlslStruct) and 
                    ptype is not GlslStruct):
                    if ptype not in struct_classes:
                        struct_classes.append(ptype)
        
        # Emit struct declarations
        if struct_classes:
            for struct_class in struct_classes:
                lines.extend(struct_class.declare_struct())
            lines.append("")  # Blank line for readability

        for name, ptype in sorted(self.params.items()):
            origin = getattr(ptype, "__origin__", None)
            is_array = None
            if origin is not None and origin == Sequence:
                ptype = ptype.__parameters__[0]
                is_array = True
            lines += ptype.declare_input_block(instance_name=name,
                                               array=is_array)

        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
        node.name = "main"
        node.args.args = []
        node.returns = None

        node = _RewriteReturn(self.return_type).visit(node)
        ast.fix_missing_locations(node)
        node = _Renamer(GLSL_BUILTIN_RENAMES).visit(node)

        if is_fragment:
            rem_names = [name for name, ptype in self.params.items() if ptype.__bases__[0].__name__ != 'ShaderInterface']
            rem_names.append(snake_case(self.return_type.__name__))
        else:
            rem_names = [name for name, _ in self.params.items()]
        node = _Remover(rem_names).visit(node)

        if self.return_type is not None:
            lines += self.return_type.declare_output_block()

        # Include all library functions (no dead code elimination yet)
        if self.library is not None:
            for f in self.library:
                lines.extend(GlslVisitor().visit(parse(f)).lines)

        return '\n'.join(lines + visitor.visit(self.root).lines)

class VertexStage(Stage):
    """Vertex shader compilation stage.
    
    Specialization of Stage for vertex shaders. Handles attribute inputs
    and interface block outputs to fragment shaders.
    
    Example:
        >>> from pyglsl import VertexStage
        >>> glsl_code = VertexStage(my_vertex_function).compile()
    """
    pass

class FragmentStage(Stage):
    """Fragment shader compilation stage.
    
    Specialization of Stage for fragment shaders. Handles interface block
    inputs from vertex shaders and framebuffer outputs.
    
    Example:
        >>> from pyglsl import FragmentStage
        >>> glsl_code = FragmentStage(my_fragment_function).compile()
    """
    def compile(self, is_fragment=True):
        return super().compile(is_fragment=True)

class GeometryStage(Stage):
    """Geometry shader compilation stage.
    
    Handles geometry shader specifics including layout qualifiers,
    primitive input/output, and vertex emission via yield statements.
    
    Geometry shaders must be decorated with @geometry_shader_layout to
    specify input primitive, output primitive, and max vertices.
    
    Example:
        >>> from typing import Sequence, Iterator
        >>> from pyglsl.glsl import geometry_shader_layout, triangles, triangle_strip
        >>> @geometry_shader_layout(input_primitive=triangles,
        ...                          output_primitive=triangle_strip,
        ...                          max_vertices=3)
        ... def geom_shader(gl_in: Sequence[GlGsIn], vs_out: Sequence[VsOut]) -> Iterator[GsOut]:
        ...     for i in range(3):
        ...         yield GsOut(gl_position=gl_in[i].gl_Position, color=vs_out[i].color)
        ...     EndPrimitive()
    """
    def __init__(self,
                 func: Callable[..., Any],
                 version: Optional[Union[str, int]] = "330 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        super().__init__(func, version, library)
        
        # Extract geometry shader layout metadata from decorator
        if not hasattr(func, '_geometry_layout'):
            raise ValueError(
                'Geometry shader must be decorated with @geometry_shader_layout. '
                'Example: @geometry_shader_layout(input_primitive=triangles, '
                'output_primitive=triangle_strip, max_vertices=3)'
            )
        
        self.layout = func._geometry_layout
        
    def compile(self):
        """Compile geometry shader with layout qualifiers."""
        from typing import get_origin, get_args
        
        lines = [f"#version {self.version}"]
        
        # Generate layout qualifiers
        input_prim = self.layout['input_primitive'].__name__
        output_prim = self.layout['output_primitive'].__name__
        max_verts = self.layout['max_vertices']
        
        lines.append(f"layout({input_prim}) in;")
        lines.append(f"layout({output_prim}, max_vertices = {max_verts}) out;")
        lines.append("")  # Blank line for readability
        
        visitor = GlslVisitor()
        
        # Handle input parameters (typically Sequence[Type] for arrays)
        for name, ptype in sorted(self.params.items()):
            origin = get_origin(ptype)
            
            # Check if this is a Sequence type (geometry shader array input)
            if origin is not None:
                # Handle typing.Sequence[Type]
                if hasattr(origin, '__name__') and origin.__name__ == 'Sequence':
                    # Get the element type
                    args = get_args(ptype)
                    if args:
                        element_type = args[0]
                        
                        # Special handling for GlGsIn - it's the built-in gl_in array
                        if element_type.__name__ == 'GlGsIn':
                            # gl_in is automatically available, don't declare it
                            continue
                        
                        # For other sequence types, declare as input array
                        lines += element_type.declare_input_block(instance_name=name, array=True)
                    else:
                        raise ValueError(f'Sequence type hint for {name} must have element type')
                else:
                    # Other generic types - try to handle as regular input
                    lines += ptype.declare_input_block(instance_name=name)
            else:
                # Non-generic type - regular input
                lines += ptype.declare_input_block(instance_name=name)
        
        # Process the function AST
        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
        
        node.name = "main"
        node.args.args = []
        node.returns = None
        
        # Rewrite return statements (even though geometry shaders use yield, 
        # there might be early returns)
        if self.return_type is not None:
            # For geometry shaders, return type should be Iterator[OutputType]
            # Extract the actual output type
            from typing import get_origin, get_args
            ret_origin = get_origin(self.return_type)
            if ret_origin is not None:
                ret_args = get_args(self.return_type)
                if ret_args:
                    actual_return_type = ret_args[0]
                else:
                    actual_return_type = self.return_type
            else:
                actual_return_type = self.return_type
            
            node = _RewriteReturn(actual_return_type).visit(node)
            ast.fix_missing_locations(node)
        
        # Rename built-in variables
        node = _Renamer(GLSL_BUILTIN_RENAMES).visit(node)
        
        # For geometry shaders, we don't remove parameter name prefixes
        # because we access arrays like gl_in[i] and vs_out[i]
        
        # Declare output block
        if self.return_type is not None:
            from typing import get_origin, get_args
            ret_origin = get_origin(self.return_type)
            if ret_origin is not None:
                ret_args = get_args(self.return_type)
                if ret_args:
                    actual_output = ret_args[0]
                    lines += actual_output.declare_output_block()
            elif self.return_type is not None:
                lines += self.return_type.declare_output_block()
        
        # Include library functions
        if self.library is not None:
            for f in self.library:
                lines.extend(GlslVisitor().visit(parse(f)).lines)
        
        return '\n'.join(lines + visitor.visit(self.root).lines)

class TessControlStage(Stage):
    """Tessellation control shader compilation stage.
    
    Handles tessellation control shader specifics including layout qualifiers,
    patch size, and per-vertex output.
    
    Example:
        >>> @tessellation_control_layout(vertices=3)
        ... def tcs_shader(gl_in: Sequence[GlTessIn]) -> TcsOut:
        ...     gl_TessLevelInner[0] = 3.0
        ...     return TcsOut(pos=gl_in[gl_InvocationID].gl_Position)
    """
    def __init__(self,
                 func: Callable[..., Any],
                 version: Optional[Union[str, int]] = "400 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        super().__init__(func, version, library)
        
        if not hasattr(func, '_tess_control_layout'):
            raise ValueError(
                'Tessellation control shader must be decorated with @tessellation_control_layout'
            )
        
        self.layout = func._tess_control_layout
        
    def compile(self):
        from typing import get_origin, get_args
        
        lines = [f"#version {self.version}"]
        
        # Generate layout qualifiers
        vertices = self.layout['vertices']
        lines.append(f"layout(vertices = {vertices}) out;")
        lines.append("")
        
        visitor = GlslVisitor()
        
        # Handle input parameters
        for name, ptype in sorted(self.params.items()):
            origin = get_origin(ptype)
            if origin is not None and hasattr(origin, '__name__') and origin.__name__ == 'Sequence':
                args = get_args(ptype)
                if args:
                    element_type = args[0]
                    if element_type.__name__ == 'GlTessIn':
                        continue # gl_in is built-in
                    lines += element_type.declare_input_block(instance_name=name, array=True)
            else:
                lines += ptype.declare_input_block(instance_name=name)
                
        # Process function AST
        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
            
        node.name = "main"
        node.args.args = []
        node.returns = None
        
        # Rewrite return statements to assign to output array
        if self.return_type is not None:
            # Custom rewriter for TCS that assigns to gl_out[gl_InvocationID]
            # We need to modify _RewriteReturn or do something similar
            # For now, let's use a modified approach where we set the instance name to include the index
            
            # Hack: modify the interface instance name temporarily? 
            # Or better, subclass _RewriteReturn
            pass

        # Remove parameter name prefixes
        rem_names = [name for name, _ in self.params.items()]
        node = _Remover(rem_names).visit(node)

        # Rename built-in variables
        node = _Renamer(GLSL_BUILTIN_RENAMES).visit(node)
        
        # Declare output block (as array)
        if self.return_type is not None:
            lines += self.return_type.declare_output_block(array=True)
            
        if self.library is not None:
            for f in self.library:
                lines.extend(GlslVisitor().visit(parse(f)).lines)
                
        # We need to handle the return statement specially for TCS
        # The default _RewriteReturn assigns to "instance_name.member = ..."
        # We want "instance_name[gl_InvocationID].member = ..."
        
        # Let's implement a specific TCS return rewriter here
        class _TCSRewriteReturn(ast.NodeTransformer):
            def __init__(self, interface):
                self.interface = interface
            
            def visit_Return(self, node):
                from .stage import kwargs_as_assignments
                # Create parent node representing instance_name[gl_InvocationID]
                instance_name = self.interface.instance_name()
                parent = ast.Subscript(
                    value=ast.Name(id=instance_name, ctx=ast.Load()),
                    slice=ast.Name(id='gl_InvocationID', ctx=ast.Load()),
                    ctx=ast.Load()
                )
                return list(kwargs_as_assignments(node.value, parent))
                
            def visit_Expr(self, node):
                return node

        if self.return_type is not None:
            node = _TCSRewriteReturn(self.return_type).visit(node)
            ast.fix_missing_locations(node)

        return '\n'.join(lines + visitor.visit(self.root).lines)


class TessEvalStage(Stage):
    """Tessellation evaluation shader compilation stage.
    
    Example:
        >>> @tessellation_evaluation_layout(primitive_mode=triangles,
        ...                                 spacing=equal_spacing,
        ...                                 vertex_order=ccw)
        ... def tes_shader(gl_in: Sequence[GlTessIn]) -> TesOut:
        ...     pass
    """
    def __init__(self,
                 func: Callable[..., Any],
                 version: Optional[Union[str, int]] = "400 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        super().__init__(func, version, library)
        
        if not hasattr(func, '_tess_eval_layout'):
            raise ValueError(
                'Tessellation evaluation shader must be decorated with @tessellation_evaluation_layout'
            )
        
        self.layout = func._tess_eval_layout
        
    def compile(self):
        from typing import get_origin, get_args
        
        lines = [f"#version {self.version}"]
        
        # Generate layout qualifiers
        prim = self.layout['primitive_mode'].__name__
        spacing = self.layout['spacing'].__name__ if self.layout['spacing'] else 'equal_spacing'
        order = self.layout['vertex_order'].__name__ if self.layout['vertex_order'] else 'ccw'
        
        lines.append(f"layout({prim}, {spacing}, {order}) in;")
        lines.append("")
        
        visitor = GlslVisitor()
        
        # Handle input parameters
        for name, ptype in sorted(self.params.items()):
            origin = get_origin(ptype)
            if origin is not None and hasattr(origin, '__name__') and origin.__name__ == 'Sequence':
                args = get_args(ptype)
                if args:
                    element_type = args[0]
                    if element_type.__name__ == 'GlTessIn':
                        continue
                    lines += element_type.declare_input_block(instance_name=name, array=True)
            else:
                lines += ptype.declare_input_block(instance_name=name)
                
        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
            
        node.name = "main"
        node.args.args = []
        node.returns = None
        
        # Standard return rewriting works for TES (per-vertex output)
        if self.return_type is not None:
            node = _RewriteReturn(self.return_type).visit(node)
            ast.fix_missing_locations(node)
            
        # Remove parameter name prefixes
        rem_names = [name for name, _ in self.params.items()]
        node = _Remover(rem_names).visit(node)

        node = _Renamer(GLSL_BUILTIN_RENAMES).visit(node)
        
        if self.return_type is not None:
            lines += self.return_type.declare_output_block()
            
        if self.library is not None:
            for f in self.library:
                lines.extend(GlslVisitor().visit(parse(f)).lines)
                
        return '\n'.join(lines + visitor.visit(self.root).lines)


class ComputeStage(Stage):
    """Compute shader compilation stage.
    
    Example:
        >>> @compute_shader_layout(local_size_x=16, local_size_y=16)
        ... def cs_shader():
        ...     pass
    """
    def __init__(self,
                 func: Callable[..., Any],
                 version: Optional[Union[str, int]] = "430 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        super().__init__(func, version, library)
        
        if not hasattr(func, '_compute_layout'):
            raise ValueError(
                'Compute shader must be decorated with @compute_shader_layout'
            )
        
        self.layout = func._compute_layout
        
    def compile(self):
        lines = [f"#version {self.version}"]
        
        # Generate layout qualifiers
        x = self.layout['local_size_x']
        y = self.layout['local_size_y']
        z = self.layout['local_size_z']
        lines.append(f"layout(local_size_x = {x}, local_size_y = {y}, local_size_z = {z}) in;")
        lines.append("")
        
        visitor = GlslVisitor()
        
        # Handle shared memory declarations in body
        # We need a custom visitor or pre-pass to find shared() calls and move them to global scope?
        # Or just let them be local static variables if GLSL supports that?
        # GLSL shared variables must be global.
        
        # Let's extract shared variables from the function body
        class SharedVarExtractor(ast.NodeTransformer):
            def __init__(self):
                self.shared_decls = []
                
            def visit_Assign(self, node):
                # Check for: var = shared(type)
                if (isinstance(node.value, ast.Call) and 
                    isinstance(node.value.func, ast.Name) and 
                    node.value.func.id == 'shared'):
                    
                    # Extract type
                    if len(node.value.args) != 1:
                        raise ValueError('shared() requires exactly one type argument')
                    
                    type_node = node.value.args[0]
                    
                    target = node.targets[0]
                    if not isinstance(target, ast.Name):
                        raise ValueError('shared variable must be assigned to a name')

                    if isinstance(type_node, ast.Subscript):
                        # Array type: float[256] -> shared float var_name[256];
                        elem_type = GlslVisitor().visit(type_node.value).one()
                        size = GlslVisitor().visit(type_node.slice).one()
                        self.shared_decls.append(f"shared {elem_type} {target.id}[{size}];")
                    else:
                        # Simple type
                        type_str = GlslVisitor().visit(type_node).one()
                        self.shared_decls.append(f"shared {type_str} {target.id};")
                    
                    # Remove the assignment from the body
                    return None
                return node
                
        extractor = SharedVarExtractor()
        self.root = extractor.visit(self.root)
        lines.extend(extractor.shared_decls)
        if extractor.shared_decls:
            lines.append("")
            
        # Handle input parameters (uniforms mostly)
        for name, ptype in sorted(self.params.items()):
            lines += ptype.declare_input_block(instance_name=name)
            
        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
            
        node.name = "main"
        node.args.args = []
        node.returns = None
        
        # Remove parameter name prefixes
        rem_names = [name for name, _ in self.params.items()]
        node = _Remover(rem_names).visit(node)

        node = _Renamer(GLSL_BUILTIN_RENAMES).visit(node)
        
        if self.library is not None:
            for f in self.library:
                lines.extend(GlslVisitor().visit(parse(f)).lines)
                
        return '\n'.join(lines + visitor.visit(self.root).lines)
