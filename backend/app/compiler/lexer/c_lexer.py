"""
C and C++ Lexer implementation for Stage 1: Lexical Analysis.
"""
import re
from typing import List, Tuple
from .base import BaseLexer, Token, TokenType, LexicalError

C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "int", "long", "register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
    # C++ extensions
    "bool", "catch", "class", "cin", "cout", "delete", "dynamic_cast", "endl", "false",
    "friend", "inline", "namespace", "new", "nullptr", "operator", "private",
    "protected", "public", "reinterpret_cast", "static_cast", "std", "string",
    "template", "this", "throw", "true", "try", "typeid", "typename", "using",
    "virtual", "include", "define"
}

C_OPERATORS = [
    "::", "++", "--", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "->",
    "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", "^", "~", "?", ":"
]

C_DELIMITERS = {
    "(", ")", "{", "}", "[", "]", ";", ",", "."
}

class CLexer(BaseLexer):
    """Lexer for C and C++ source code."""

    def __init__(self, code: str, is_cpp: bool = False):
        super().__init__(code)
        self.is_cpp = is_cpp

    def tokenize(self) -> Tuple[List[Token], List[LexicalError]]:
        i = 0
        n = len(self.code)
        line = 1
        col = 1

        while i < n:
            ch = self.code[i]

            # Newlines
            if ch == '\n':
                line += 1
                col = 1
                i += 1
                continue

            # Whitespace
            if ch in ' \t\r':
                col += 1
                i += 1
                continue

            # Comments: // or /* ... */
            if ch == '/' and i + 1 < n and self.code[i + 1] == '/':
                start_col = col
                val = ""
                while i < n and self.code[i] != '\n':
                    val += self.code[i]
                    i += 1
                self.tokens.append(Token(TokenType.COMMENT, val, line, start_col))
                continue

            if ch == '/' and i + 1 < n and self.code[i + 1] == '*':
                start_line = line
                start_col = col
                val = "/*"
                i += 2
                col += 2
                closed = False
                while i + 1 < n:
                    if self.code[i] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                    if self.code[i] == '*' and self.code[i + 1] == '/':
                        val += "*/"
                        i += 2
                        col += 1
                        closed = True
                        break
                    val += self.code[i]
                    i += 1
                if not closed:
                    self.errors.append(LexicalError(
                        line=start_line,
                        column=start_col,
                        message="Unclosed multi-line comment",
                        token_value=val[:20] + "..."
                    ))
                else:
                    self.tokens.append(Token(TokenType.COMMENT, val, start_line, start_col))
                continue

            # Preprocessor directives (#include, #define, etc.)
            if ch == '#':
                start_col = col
                val = ""
                while i < n and self.code[i] != '\n':
                    val += self.code[i]
                    i += 1
                    col += 1
                self.tokens.append(Token(TokenType.PREPROCESSOR, val.strip(), line, start_col))
                continue

            # String literals: "..."
            if ch == '"':
                start_line = line
                start_col = col
                val = '"'
                i += 1
                col += 1
                closed = False
                while i < n:
                    curr = self.code[i]
                    val += curr
                    if curr == '\n':
                        break
                    if curr == '\\' and i + 1 < n:
                        i += 1
                        val += self.code[i]
                        col += 2
                        i += 1
                        continue
                    if curr == '"':
                        closed = True
                        i += 1
                        col += 1
                        break
                    i += 1
                    col += 1

                if not closed:
                    self.errors.append(LexicalError(
                        line=start_line,
                        column=start_col,
                        message="Unterminated string literal",
                        token_value=val
                    ))
                else:
                    self.tokens.append(Token(TokenType.STRING, val, start_line, start_col))
                continue

            # Character literals: '...'
            if ch == "'":
                start_line = line
                start_col = col
                val = "'"
                i += 1
                col += 1
                closed = False
                while i < n:
                    curr = self.code[i]
                    val += curr
                    if curr == '\n':
                        break
                    if curr == '\\' and i + 1 < n:
                        i += 1
                        val += self.code[i]
                        col += 2
                        i += 1
                        continue
                    if curr == "'":
                        closed = True
                        i += 1
                        col += 1
                        break
                    i += 1
                    col += 1
                if not closed:
                    self.errors.append(LexicalError(
                        line=start_line,
                        column=start_col,
                        message="Unterminated character literal",
                        token_value=val
                    ))
                else:
                    self.tokens.append(Token(TokenType.STRING, val, start_line, start_col))
                continue

            # Numbers: decimal or hex or float
            if ch.isdigit():
                start_col = col
                val = ""
                has_dot = False
                while i < n and (self.code[i].isalnum() or self.code[i] == '.'):
                    if self.code[i] == '.':
                        if has_dot:
                            break
                        has_dot = True
                    val += self.code[i]
                    i += 1
                    col += 1
                self.tokens.append(Token(TokenType.NUMBER, val, line, start_col))
                continue

            # Identifiers or Keywords
            if ch.isalpha() or ch == '_':
                start_col = col
                val = ""
                while i < n and (self.code[i].isalnum() or self.code[i] == '_'):
                    val += self.code[i]
                    i += 1
                    col += 1
                if val in C_KEYWORDS:
                    if val in ("true", "false"):
                        self.tokens.append(Token(TokenType.BOOLEAN, val, line, start_col))
                    else:
                        self.tokens.append(Token(TokenType.KEYWORD, val, line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, val, line, start_col))
                continue

            # Multi-char operators
            matched_op = None
            for op in C_OPERATORS:
                if self.code.startswith(op, i):
                    matched_op = op
                    break
            if matched_op:
                self.tokens.append(Token(TokenType.OPERATOR, matched_op, line, col))
                i += len(matched_op)
                col += len(matched_op)
                continue

            # Delimiters
            if ch in C_DELIMITERS:
                self.tokens.append(Token(TokenType.DELIMITER, ch, line, col))
                i += 1
                col += 1
                continue

            # Unknown or illegal character
            self.errors.append(LexicalError(
                line=line,
                column=col,
                message=f"Illegal character: '{ch}'",
                token_value=ch
            ))
            i += 1
            col += 1

        self.tokens.append(Token(TokenType.EOF, "", line, col))
        return self.tokens, self.errors
