"""
Modular Translation Coordinator for Large Programs (up to 1,000 lines).
Decomposes large codebases into logical units (imports, global definitions, functions, classes),
determines topological translation order using DependencyAnalyzer, and reconstructs cohesive target code.
"""
import time
from typing import Dict, Any, List, Optional
from .dependency_analyzer import DependencyAnalyzer
from .parser import parse_code
from .parser.ast_nodes import ProgramNode, FunctionDefNode, VarDeclNode
from .codegen import generate_target_code, validate_target_code
from ..ai.provider import AIProvider

class ModularTranslator:
    """Manages chunked, dependency-aware translation for large 1,000-line programs."""

    def __init__(self):
        self.dep_analyzer = DependencyAnalyzer()
        self.ai_provider = AIProvider()

    def translate_large_program(
        self,
        source_lang: str,
        target_lang: str,
        source_code: str,
        ai_enabled: bool = False
    ) -> Dict[str, Any]:
        """Translates a large program by decomposing it into logical function and global chunks."""
        t0 = time.perf_counter()

        # Step 1: Parse AST
        ast_root, syn_errors = parse_code(source_lang, source_code)
        if not ast_root:
            return {
                "success": False,
                "error": "Failed to parse source program into AST for modular translation.",
                "errors": [e.to_dict() for e in syn_errors],
                "transpiled_code": "",
                "chunks_processed": 0,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # Step 2: Dependency Analysis
        dep_info = self.dep_analyzer.analyze_program(ast_root)
        topo_order = dep_info.get("topological_order", [])
        globals_list = dep_info.get("globals", [])

        # Separate functions and global declarations
        functions = {s.name: s for s in ast_root.body if isinstance(s, FunctionDefNode)}
        global_stmts = [s for s in ast_root.body if not isinstance(s, FunctionDefNode)]

        # Step 3: Re-order functions by topological dependency
        ordered_funcs = []
        visited = set()
        for fname in topo_order:
            if fname in functions:
                ordered_funcs.append(functions[fname])
                visited.add(fname)
        for fname, fnode in functions.items():
            if fname not in visited:
                ordered_funcs.append(fnode)

        # Step 4: Assemble modular AST
        modular_ast = ProgramNode(body=global_stmts + ordered_funcs)

        # Step 5: Generate target code
        target_code = generate_target_code(target_lang, modular_ast)
        val_res = validate_target_code(target_lang, target_code)

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "success": val_res.get("valid", True),
            "transpiled_code": target_code,
            "dependency_info": dep_info,
            "chunks_processed": len(ordered_funcs) + len(global_stmts),
            "function_count": len(ordered_funcs),
            "global_count": len(global_stmts),
            "validation": val_res,
            "duration_ms": duration_ms
        }
