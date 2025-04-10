import ast
import networkx as nx
from typing import Dict, List, Tuple, Set
import os

class CodeAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.current_file = None
        self.current_class = None
        self.current_function = None
        self.defined_functions: Set[str] = set()
        self.function_calls: List[Tuple[str, str]] = []

    def analyze_code(self, code_files: Dict[str, str]) -> nx.DiGraph:
        """Analyze Python code files and generate a graph representation."""
        self.graph = nx.DiGraph()
        self.defined_functions.clear()
        self.function_calls.clear()
        
        # First pass: collect all defined functions and add nodes
        for file_path, code in code_files.items():
            self.current_file = file_path
            self._add_file_node(file_path)
            try:
                tree = ast.parse(code)
                self._collect_definitions(tree)
            except SyntaxError as e:
                self._add_error_node(file_path, str(e))
        
        # Second pass: analyze relationships and function calls
        for file_path, code in code_files.items():
            self.current_file = file_path
            self.current_class = None
            self.current_function = None
            try:
                tree = ast.parse(code)
                self._process_relationships(tree)
            except SyntaxError:
                continue
        
        # Process collected function calls
        self._process_function_calls()
        
        return self.graph

    def _add_file_node(self, file_path: str):
        """Add a file node to the graph."""
        name = os.path.basename(file_path)
        self.graph.add_node(file_path, type='file', name=name)

    def _add_error_node(self, file_path: str, error_msg: str):
        """Add an error node to the graph."""
        error_id = f"{file_path}_error"
        self.graph.add_node(error_id, type='error', name=error_msg)
        self.graph.add_edge(file_path, error_id, type='contains_error')

    def _collect_definitions(self, tree: ast.AST):
        """Collect all function and class definitions."""
        class_stack = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_stack.append(node)
                class_id = f"{self.current_file}:{node.name}"
                self.graph.add_node(class_id, type='class', name=node.name)
                self.graph.add_edge(self.current_file, class_id, type='defines')
                
                # Process class methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_id = f"{class_id}:{item.name}"
                        self.graph.add_node(method_id, type='method', name=item.name)
                        self.graph.add_edge(class_id, method_id, type='defines')
                        self.defined_functions.add(method_id)
                
                class_stack.pop()
            
            elif isinstance(node, ast.FunctionDef):
                # Check if this function is inside a class
                if not class_stack:  # Only top-level functions
                    func_id = f"{self.current_file}:{node.name}"
                    self.graph.add_node(func_id, type='function', name=node.name)
                    self.graph.add_edge(self.current_file, func_id, type='defines')
                    self.defined_functions.add(func_id)

    def _process_relationships(self, tree: ast.AST):
        """Process the AST to add relationships between nodes."""
        class_stack = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_stack.append(node.name)
                self.current_class = node.name
            
            elif isinstance(node, ast.FunctionDef):
                self.current_function = node.name
            
            elif isinstance(node, ast.Import):
                for name in node.names:
                    self._add_import_relationship(name.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    self._add_import_relationship(f"{module}.{name.name}")
            
            elif isinstance(node, ast.Call):
                self._process_call(node)
            
            # Handle exiting class/function context
            if isinstance(node, ast.ClassDef):
                class_stack.pop()
                self.current_class = class_stack[-1] if class_stack else None
            elif isinstance(node, ast.FunctionDef):
                self.current_function = None

    def _process_call(self, node: ast.Call):
        """Process a function call node."""
        caller = self._get_current_context()
        
        if isinstance(node.func, ast.Name):
            callee = node.func.id
            self.function_calls.append((caller, callee))
        
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                callee = f"{node.func.value.id}.{node.func.attr}"
                self.function_calls.append((caller, callee))

    def _get_current_context(self) -> str:
        """Get the current context (class method or function)."""
        if self.current_class:
            if self.current_function:
                return f"{self.current_file}:{self.current_class}:{self.current_function}"
            return f"{self.current_file}:{self.current_class}"
        if self.current_function:
            return f"{self.current_file}:{self.current_function}"
        return self.current_file

    def _add_import_relationship(self, import_name: str):
        """Add an import relationship to the graph."""
        import_id = f"import:{import_name}"
        self.graph.add_node(import_id, type='import', name=import_name)
        self.graph.add_edge(self.current_file, import_id, type='imports')

    def _process_function_calls(self):
        """Process collected function calls and add edges."""
        for caller, callee in self.function_calls:
            # Try to find the actual function node
            potential_callees = [
                f for f in self.defined_functions
                if f.endswith(f":{callee}")
            ]
            
            if potential_callees:
                for target in potential_callees:
                    self.graph.add_edge(caller, target, type='calls')
            else:
                # If not found, create a reference node
                ref_id = f"ref:{callee}"
                if ref_id not in self.graph:
                    self.graph.add_node(ref_id, type='function', name=callee)
                self.graph.add_edge(caller, ref_id, type='calls') 