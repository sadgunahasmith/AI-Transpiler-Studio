"""
Code Generation module entry point for Stage 6: Code Generation.
"""
from typing import Optional, Dict, Any
import ast
from .python_codegen import PythonCodeGen
from .js_codegen import JSCodeGen
from .c_codegen import CCodeGen
from .cpp_codegen import CPPCodeGen
from .java_codegen import JavaCodeGen
from ..parser.ast_nodes import ProgramNode

def generate_target_code(target_language: str, ast_root: Optional[ProgramNode]) -> str:
    lang = target_language.strip().lower()
    if lang in ("python", "py"):
        generator = PythonCodeGen()
    elif lang in ("javascript", "js"):
        generator = JSCodeGen()
    elif lang in ("c",):
        generator = CCodeGen()
    elif lang in ("cpp", "c++"):
        generator = CPPCodeGen()
    elif lang in ("java",):
        generator = JavaCodeGen()
    else:
        generator = PythonCodeGen()

    return generator.generate(ast_root)

def validate_target_code(target_language: str, code: str) -> Dict[str, Any]:
    """Validates the syntax of the generated target code."""
    lang = target_language.strip().lower()

    if lang in ("python", "py"):
        try:
            ast.parse(code)
            return {"valid": True, "message": "Python syntax validation passed."}
        except SyntaxError as e:
            return {"valid": False, "message": f"Python syntax error at line {e.lineno}: {e.msg}"}

    # For JS, C, C++, Java, verify bracket/parenthesis balancing
    brace_count = 0
    paren_count = 0
    for ch in code:
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
        elif ch == '(':
            paren_count += 1
        elif ch == ')':
            paren_count -= 1

    if brace_count != 0 or paren_count != 0:
        return {"valid": False, "message": f"Mismatched delimiters detected in generated {target_language} code."}

    return {"valid": True, "message": f"{target_language.capitalize()} code generated with structural delimiter verification passed."}

__all__ = ["generate_target_code", "validate_target_code", "PythonCodeGen", "JSCodeGen", "CCodeGen", "CPPCodeGen", "JavaCodeGen"]
