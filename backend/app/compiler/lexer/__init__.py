"""
Lexer module entry point for Stage 1: Lexical Analysis.
"""
from typing import List, Tuple, Dict, Any
from .base import Token, TokenType, LexicalError, BaseLexer
from .c_lexer import CLexer
from .py_lexer import PythonLexer
from .js_lexer import JSLexer
from .java_lexer import JavaLexer

def get_lexer(language: str, code: str) -> BaseLexer:
    lang = language.strip().lower()
    if lang in ("c",):
        return CLexer(code, is_cpp=False)
    elif lang in ("cpp", "c++"):
        return CLexer(code, is_cpp=True)
    elif lang in ("python", "py"):
        return PythonLexer(code)
    elif lang in ("javascript", "js"):
        return JSLexer(code)
    elif lang in ("java",):
        return JavaLexer(code)
    else:
        # Default fallback to C-like lexer
        return CLexer(code, is_cpp=False)

def tokenize_code(language: str, code: str) -> Tuple[List[Token], List[LexicalError]]:
    lexer = get_lexer(language, code)
    return lexer.tokenize()

__all__ = ["Token", "TokenType", "LexicalError", "BaseLexer", "CLexer", "PythonLexer", "JSLexer", "JavaLexer", "get_lexer", "tokenize_code"]
