"""
Parser module entry point for Stage 2: Syntax Analysis.
"""
from typing import Tuple, Optional, List
from .ast_nodes import ProgramNode, SyntaxErrorRecord, ASTNode
from .py_parser import PythonParser
from .c_parser import CParser
from .js_parser import JSParser
from .java_parser import JavaParser
from .clang_frontend import ClangFrontend

def parse_code(
    language: str,
    code: str,
    parser_mode: Optional[str] = "auto"
) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord]]:
    lang = language.strip().lower()
    if lang in ("python", "py"):
        parser = PythonParser(code)
        return parser.parse()
    elif lang in ("c",):
        parser = CParser(code, is_cpp=False)
        return parser.parse()
    elif lang in ("cpp", "c++"):
        mode = (parser_mode or "auto").lower()
        if mode == "educational":
            parser = CParser(code, is_cpp=True)
            return parser.parse()
        try:
            frontend = ClangFrontend(code)
            ast_root, errors = frontend.parse()
            # If clang parse succeeded (or produced an AST), return it
            if ast_root is not None:
                return ast_root, errors
            # Fall back to educational parser if Clang produced no AST
            parser = CParser(code, is_cpp=True)
            return parser.parse()
        except Exception:
            parser = CParser(code, is_cpp=True)
            return parser.parse()
    elif lang in ("javascript", "js"):
        parser = JSParser(code)
        return parser.parse()
    elif lang in ("java",):
        parser = JavaParser(code)
        return parser.parse()
    else:
        parser = CParser(code, is_cpp=False)
        return parser.parse()

__all__ = [
    "parse_code", "ProgramNode", "SyntaxErrorRecord", "ASTNode",
    "PythonParser", "CParser", "JSParser", "JavaParser", "ClangFrontend"
]
