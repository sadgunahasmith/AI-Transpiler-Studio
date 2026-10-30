"""
Python Lexer implementation for Stage 1: Lexical Analysis.
"""
from typing import List, Tuple
from .base import BaseLexer, Token, TokenType, LexicalError

PY_KEYWORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield", "print", "range", "len"
}

PY_OPERATORS = [
    "**=", "//=", "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "%=",
    "//", "**", "+", "-", "*", "/", "%", "=", "<", ">", "&", "|", "^", "~"
]

PY_DELIMITERS = {
    "(", ")", "[", "]", "{", "}", ":", ",", ".", ";", "@"
}

class PythonLexer(BaseLexer):
    """Lexer for Python source code."""

    def tokenize(self) -> Tuple[List[Token], List[LexicalError]]:
        i = 0
        n = len(self.code)
        line = 1
        col = 1

        while i < n:
            ch = self.code[i]

            if ch == '\n':
                line += 1
                col = 1
                i += 1
                continue

            if ch in ' \t\r':
                col += 1
                i += 1
                continue

            # Python comment: # ...
            if ch == '#':
                start_col = col
                val = ""
                while i < n and self.code[i] != '\n':
                    val += self.code[i]
                    i += 1
                self.tokens.append(Token(TokenType.COMMENT, val, line, start_col))
                continue

            # Triple quotes or standard quotes
            if ch in ('"', "'"):
                quote_char = ch
                start_line = line
                start_col = col
                is_triple = False
                if i + 2 < n and self.code[i:i+3] == quote_char * 3:
                    is_triple = True
                    i += 3
                    col += 3
                    val = quote_char * 3
                else:
                    i += 1
                    col += 1
                    val = quote_char

                closed = False
                while i < n:
                    if is_triple:
                        if i + 2 < n and self.code[i:i+3] == quote_char * 3:
                            val += quote_char * 3
                            i += 3
                            col += 3
                            closed = True
                            break
                        if self.code[i] == '\n':
                            val += '\n'
                            line += 1
                            col = 1
                            i += 1
                        else:
                            val += self.code[i]
                            i += 1
                            col += 1
                    else:
                        if self.code[i] == '\n':
                            break
                        if self.code[i] == '\\' and i + 1 < n:
                            val += self.code[i:i+2]
                            i += 2
                            col += 2
                            continue
                        if self.code[i] == quote_char:
                            val += quote_char
                            i += 1
                            col += 1
                            closed = True
                            break
                        val += self.code[i]
                        i += 1
                        col += 1

                if not closed:
                    self.errors.append(LexicalError(
                        line=start_line,
                        column=start_col,
                        message=f"Unterminated string literal starting with {quote_char}",
                        token_value=val[:25]
                    ))
                else:
                    self.tokens.append(Token(TokenType.STRING, val, start_line, start_col))
                continue

            # Numbers
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
                if val in PY_KEYWORDS:
                    if val in ("True", "False"):
                        self.tokens.append(Token(TokenType.BOOLEAN, val, line, start_col))
                    else:
                        self.tokens.append(Token(TokenType.KEYWORD, val, line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, val, line, start_col))
                continue

            # Multi-character operators
            matched_op = None
            for op in PY_OPERATORS:
                if self.code.startswith(op, i):
                    matched_op = op
                    break
            if matched_op:
                self.tokens.append(Token(TokenType.OPERATOR, matched_op, line, col))
                i += len(matched_op)
                col += len(matched_op)
                continue

            # Delimiters
            if ch in PY_DELIMITERS:
                self.tokens.append(Token(TokenType.DELIMITER, ch, line, col))
                i += 1
                col += 1
                continue

            self.errors.append(LexicalError(
                line=line,
                column=col,
                message=f"Invalid character in Python source: '{ch}'",
                token_value=ch
            ))
            i += 1
            col += 1

        self.tokens.append(Token(TokenType.EOF, "", line, col))
        return self.tokens, self.errors
