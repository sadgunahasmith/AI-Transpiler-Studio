"""
Base Lexer definitions and Token models for Compiler Lexical Analysis.
Stage 1: Lexical Analysis
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

class TokenType(str, Enum):
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    PREPROCESSOR = "PREPROCESSOR"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    UNKNOWN = "UNKNOWN"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    raw: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value if hasattr(self.type, "value") else str(self.type),
            "value": self.value,
            "line": self.line,
            "column": self.column
        }

@dataclass
class LexicalError:
    line: int
    column: int
    message: str
    token_value: str
    severity: str = "error"
    source: str = "compiler"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "token_value": self.token_value,
            "severity": self.severity,
            "source": self.source,
            "category": "Lexical Error"
        }

class BaseLexer:
    """Base class for language-specific lexers."""
    
    def __init__(self, code: str):
        self.code = code
        self.length = len(code)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[LexicalError] = []

    def tokenize(self) -> Tuple[List[Token], List[LexicalError]]:
        raise NotImplementedError
