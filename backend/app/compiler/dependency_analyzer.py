"""
Program Dependency Analyzer for Stage 2/3 and Modular 1,000-line Processing.
Builds call graphs and dependency ordering for functions, classes, and globals.
"""
from typing import Dict, List, Set, Any
from .parser.ast_nodes import ProgramNode, FunctionDefNode, CallNode, VarDeclNode, AssignNode, ASTNode

class DependencyAnalyzer:
    """Extracts call dependencies and topologically sorts program declarations."""

    def __init__(self):
        pass

    def analyze_program(self, ast_root: ProgramNode) -> Dict[str, Any]:
        """Analyzes AST functions and global dependencies."""
        if not ast_root or not ast_root.body:
            return {"functions": [], "call_graph": {}, "topological_order": []}

        functions: Dict[str, FunctionDefNode] = {}
        call_graph: Dict[str, Set[str]] = {}
        globals_list: List[str] = []

        # 1. Identify functions and top-level declarations
        for stmt in ast_root.body:
            if isinstance(stmt, FunctionDefNode):
                functions[stmt.name] = stmt
                call_graph[stmt.name] = set()
            elif isinstance(stmt, VarDeclNode):
                globals_list.append(stmt.name)

        # 2. Extract calls inside functions
        for fn_name, fn_node in functions.items():
            calls = self._extract_callees(fn_node.body)
            # Filter callees to defined functions in this module
            call_graph[fn_name] = {c for c in calls if c in functions and c != fn_name}

        # 3. Compute topological order (dependencies first)
        topological_order = self._topological_sort(call_graph)

        return {
            "functions": list(functions.keys()),
            "globals": globals_list,
            "call_graph": {k: list(v) for k, v in call_graph.items()},
            "topological_order": topological_order
        }

    def _extract_callees(self, stmts: List[ASTNode]) -> Set[str]:
        callees = set()
        for s in stmts:
            self._find_calls(s, callees)
        return callees

    def _find_calls(self, node: Any, callees: Set[str]):
        if not node or not isinstance(node, ASTNode):
            return
        if isinstance(node, CallNode):
            callees.add(node.callee)
        # Traverse child attributes
        for _, val in vars(node).items():
            if isinstance(val, ASTNode):
                self._find_calls(val, callees)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, ASTNode):
                        self._find_calls(item, callees)

    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        visited = set()
        order = []

        def dfs(node: str, path: Set[str]):
            if node in path:
                # Cycle detected, break recursion
                return
            if node in visited:
                return
            visited.add(node)
            path.add(node)
            for neighbor in graph.get(node, set()):
                dfs(neighbor, path)
            path.remove(node)
            order.append(node)

        for n in graph:
            if n not in visited:
                dfs(n, set())

        return order
