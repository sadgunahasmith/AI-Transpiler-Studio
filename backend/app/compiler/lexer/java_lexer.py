"""
Java Lexer implementation for Stage 1: Lexical Analysis.
"""
from typing import List, Tuple
from .base import BaseLexer, Token, TokenType, LexicalError

JAVA_KEYWORDS = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
    "class", "const", "continue", "default", "do", "double", "else", "enum",
    "extends", "final", "finally", "float", "for", "goto", "if", "implements",
    "import", "instanceof", "int", "interface", "long", "native", "new",
    "package", "private", "protected", "public", "return", "short", "static",
    "strictfp", "super", "switch", "synchronized", "this", "throw", "throws",
    "transient", "try", "void", "volatile", "while", "String", "System", "out",
    "println", "print", "true", "false", "null"
}

JAVA_OPERATORS = [
    ">>>=", ">>>", "<<=", ">>=", "==", "!=", "<=", ">=", "&&", "||",
    "++", "--", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
    "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", "^", "~", "?", ":"
]

JAVA_DELIMITERS = {
    "(", ")", "{", "}", "[", "]", ";", ",", "."
}

class JavaLexer(BaseLexer):
    """Lexer for Java source code."""

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

            # Line comments: //
            if ch == '/' and i + 1 < n and self.code[i + 1] == '/':
                start_col = col
                val = ""
                while i < n and self.code[i] != '\n':
                    val += self.code[i]
                    i += 1
                self.tokens.append(Token(TokenType.COMMENT, val, line, start_col))
                continue

            # Block comments: /* ... */
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
                        message="Unclosed block comment in Java source",
                        token_value=val[:20] + "..."
                    ))
                else:
                    self.tokens.append(Token(TokenType.COMMENT, val, start_line, start_col))
                continue

            # Strings
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
                        message="Unclosed string literal in Java source",
                        token_value=val
                    ))
                else:
                    self.tokens.append(Token(TokenType.STRING, val, start_line, start_col))
                continue

            # Chars: '...'
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
                        message="Unclosed character literal in Java source",
                        token_value=val
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
            if ch.isalpha() or ch in ('_', '$'):
                start_col = col
                val = ""
                while i < n and (self.code[i].isalnum() or self.code[i] in ('_', '$')):
                    val += self.code[i]
                    i += 1
                    col += 1
                if val in JAVA_KEYWORDS:
                    if val in ("true", "false"):
                        self.tokens.append(Token(TokenType.BOOLEAN, val, line, start_col))
                    else:
                        self.tokens.append(Token(TokenType.KEYWORD, val, line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, val, line, start_col))
                continue

            # Multi-character operators
            matched_op = None
            for op in JAVA_OPERATORS:
                if self.code.startswith(op, i):
                    matched_op = op
                    break
            if matched_op:
                self.tokens.append(Token(TokenType.OPERATOR, matched_op, line, col))
                i += len(matched_op)
                col += len(matched_op)
                continue

            # Delimiters
            if ch in JAVA_DELIMITERS:
                self.tokens.append(Token(TokenType.DELIMITER, ch, line, col))
                i += 1
                col += 1
                continue

            self.errors.append(LexicalError(
                line=line,
                column=col,
                message=f"Illegal character in Java source: '{ch}'",
                token_value=ch
            ))
            i += 1
            col += 1

        self.tokens.append(Token(TokenType.EOF, "", line, col))
        return self.tokens, self.errors
