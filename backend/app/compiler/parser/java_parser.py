"""
Java Parser and Syntax Error Detector for Stage 2: Syntax Analysis.
Parses Java into normalized ASTNode hierarchy.
"""
import re
from typing import List, Tuple, Optional, Any
from .ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    ClassDefNode, SyntaxErrorRecord, ASTNode, ArrayLiteralNode, ArrayAccessNode,
    StructDefNode, MemberAccessNode, InputNode, BreakNode, ContinueNode
)
from ..lexer.java_lexer import JavaLexer
from ..lexer.base import Token, TokenType

JAVA_PRIMITIVE_TYPES = {"int", "double", "float", "boolean", "char", "String", "void", "long", "short", "byte"}

class JavaParser:
    """Parses Java source code into normalized AST nodes and detects syntax errors."""

    def __init__(self, code: str):
        self.code = code
        self.errors: List[SyntaxErrorRecord] = []
        self.tokens: List[Token] = []
        self.pos = 0
        self.scanner_vars: set = set()   # Scanner sc = new Scanner(System.in)
        self.reader_vars: set = set()    # BufferedReader br = new BufferedReader(...)
        self._tmp_counter = 0

    def parse(self) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord]]:
        self._check_delimiters_and_semicolons()

        lexer = JavaLexer(self.code)
        tokens, lex_errors = lexer.tokenize()
        for le in lex_errors:
            self.errors.append(SyntaxErrorRecord(
                line=le.line, column=le.column, message=le.message,
                token_value=le.token_value, category="Lexical Error"
            ))

        self.tokens = [t for t in tokens if t.type not in (TokenType.COMMENT, TokenType.WHITESPACE, TokenType.NEWLINE)]
        self.pos = 0

        try:
            body = self._parse_program()
            program = ProgramNode(body=body, line=1, column=1)
            return program, self.errors
        except Exception as e:
            if not self.errors:
                self.errors.append(SyntaxErrorRecord(
                    line=1, column=1, message=f"Java parse error: {str(e)}",
                    category="Syntax Error"
                ))
            return None, self.errors

    def _check_delimiters_and_semicolons(self):
        lines = self.code.split('\n')
        brace_stack = []
        paren_stack = []

        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("import") or line.startswith("package"):
                continue

            for col, ch in enumerate(raw_line, 1):
                if ch == '{':
                    brace_stack.append((line_num, col))
                elif ch == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=col, message="Unmatched closing brace '}' in Java",
                            suggested_fix="Remove extra '}'"
                        ))
                elif ch == '(':
                    paren_stack.append((line_num, col))
                elif ch == ')':
                    if paren_stack:
                        paren_stack.pop()
                    else:
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=col, message="Unmatched closing parenthesis ')' in Java",
                            suggested_fix="Remove extra ')'"
                        ))

            # Missing semicolon check in Java
            first_word = line.split()[0] if line.split() else ""
            is_control_header = (
                re.match(r'^(public|private|protected|class|if|else|while|for|switch|interface)\b', line) or
                line.endswith('{') or line.endswith('}') or line.endswith(':')
            )
            if not is_control_header:
                if (first_word in JAVA_PRIMITIVE_TYPES or
                    line.startswith("return") or
                    line.startswith("System.out") or
                    "=" in line):
                    if not line.endswith(';') and not line.endswith('{') and not line.endswith('}'):
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=len(raw_line) + 1,
                            message=f"Missing semicolon ';' in Java statement: '{line}'",
                            token_value=line, suggested_fix=f"Add semicolon ';' after '{line}'"
                        ))

        for bl, bc in brace_stack:
            self.errors.append(SyntaxErrorRecord(
                line=bl, column=bc, message="Unclosed opening brace '{' in Java",
                suggested_fix="Add closing brace '}'"
            ))
        for pl, pc in paren_stack:
            self.errors.append(SyntaxErrorRecord(
                line=pl, column=pc, message="Unclosed opening parenthesis '(' in Java",
                suggested_fix="Add closing parenthesis ')'"
            ))

    def _current_token(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _peek_token(self, offset: int = 1) -> Optional[Token]:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def _match(self, *values) -> bool:
        tok = self._current_token()
        if not tok:
            return False
        for v in values:
            if isinstance(v, TokenType) and tok.type == v:
                return True
            if isinstance(v, str) and tok.value == v:
                return True
        return False

    def _consume(self, *expected) -> Optional[Token]:
        tok = self._current_token()
        if not tok:
            return None
        if expected:
            for exp in expected:
                if (isinstance(exp, TokenType) and tok.type == exp) or (isinstance(exp, str) and tok.value == exp):
                    self.pos += 1
                    return tok
            return None
        self.pos += 1
        return tok

    def _parse_program(self) -> List[ASTNode]:
        nodes = []
        while self.pos < len(self.tokens):
            tok = self._current_token()
            if not tok or tok.type == TokenType.EOF:
                break

            if tok.value in ("import", "package"):
                while self.pos < len(self.tokens) and not self._match(";"):
                    self.pos += 1
                if self._match(";"):
                    self.pos += 1
                continue

            # Class declaration
            if tok.value in ("public", "class", "interface") or (self._match("public", "private", "protected", "final", "abstract", "static") and any(self._peek_token(i) and self._peek_token(i).value in ("class", "interface") for i in (1, 2, 3))):
                cls = self._parse_class()
                if cls:
                    if isinstance(cls, ClassDefNode) and cls.name.lower() in ("main", "solution", "app"):
                        for item in cls.body:
                            nodes.append(item)
                    else:
                        nodes.append(cls)
                continue

            pos_before = self.pos
            stmt = self._parse_statement()
            if stmt:
                self._extend(nodes, stmt)
            elif self.pos == pos_before:
                self.pos += 1
        return nodes

    def _parse_class(self) -> Optional[ClassDefNode]:
        # Skip modifiers like public, static, etc.
        while self._match("public", "private", "protected", "final", "abstract", "static"):
            self._consume()
        if not self._match("class", "interface"):
            return None
        self._consume()
        name_tok = self._consume()
        class_name = name_tok.value if name_tok else "Main"

        # Handle extends and implements
        if self._match("extends"):
            self._consume("extends")
            self._consume() # base class
        if self._match("implements"):
            self._consume("implements")
            while not self._match("{") and not self._match(TokenType.EOF):
                self._consume()

        body = []
        if self._match("{"):
            self._consume("{")
            while not self._match("}") and not self._match(TokenType.EOF):
                tok = self._current_token()
                if not tok:
                    break
                # Modifiers
                while self._match("public", "private", "protected", "static", "final"):
                    self._consume()
                if self._match("class", "interface"):
                    c = self._parse_class()
                    if c:
                        body.append(c)
                    continue

                curr_tok = self._current_token()
                if not curr_tok:
                    break

                # Check if constructor: ClassName(...)
                if curr_tok.value == class_name and self._peek_token(1) and self._peek_token(1).value == "(":
                    m = self._parse_method(is_ctor=True)
                    if m:
                        body.append(m)
                    continue

                # Check if method: RetType methodName(...)
                if self._peek_token(1) and self._peek_token(2) and self._peek_token(2).value == "(":
                    m = self._parse_method()
                    if m:
                        body.append(m)
                    continue
                # Array return type: RetType[] methodName(...)
                if self._peek_token(1) and self._peek_token(1).value == "[" and self._peek_token(2) and self._peek_token(2).value == "]":
                    if self._peek_token(3) and self._peek_token(4) and self._peek_token(4).value == "(":
                        m = self._parse_method()
                        if m:
                            body.append(m)
                        continue

                # Field declaration or statement
                pos_before = self.pos
                if self._try_reader_decl():
                    continue
                if curr_tok.value in JAVA_PRIMITIVE_TYPES or (self._peek_token(1) and self._peek_token(1).type == TokenType.IDENTIFIER):
                    v = self._parse_var_decl()
                    if v:
                        body.append(v)
                    elif self.pos == pos_before:
                        s = self._parse_statement()
                        if s:
                            self._extend(body, s)
                        elif self.pos == pos_before:
                            self.pos += 1
                else:
                    s = self._parse_statement()
                    if s:
                        self._extend(body, s)
                    elif self.pos == pos_before:
                        self.pos += 1
            self._consume("}")
        fields = [s for s in body if isinstance(s, VarDeclNode)]
        methods = [s for s in body if isinstance(s, FunctionDefNode)]
        return ClassDefNode(name=class_name, body=body, fields=fields, methods=methods, line=name_tok.line if name_tok else 1)

    def _parse_method(self, is_ctor: bool = False) -> FunctionDefNode:
        if is_ctor:
            name_tok = self._consume()
            name = name_tok.value if name_tok else "constructor"
            ret_type = "void"
        else:
            ret_tok = self._consume()
            ret_type = ret_tok.value if ret_tok else "void"
            if self._match("["):
                self._consume("[")
                self._consume("]")
                ret_type += "[]"
            name_tok = self._consume()
            name = name_tok.value if name_tok else "main"

        self._consume("(")
        params = []
        while not self._match(")") and not self._match(TokenType.EOF):
            pos_before = self.pos
            p_type = self._consume()
            type_name = p_type.value if p_type else None
            if self._match("["):
                self._consume("[")
                self._consume("]")
                if type_name:
                    type_name += "[]"
            p_name = self._consume()
            if p_name and p_name.value != ")":
                params.append(ParamNode(name=p_name.value, type_name=type_name, line=name_tok.line if name_tok else 1))
            if self._match(","):
                self._consume(",")
            elif self.pos == pos_before:
                self.pos += 1

        if self._match(")"):
            self._consume(")")
        # Parse throws clause if present: throws Exception, IOException
        if self._match("throws"):
            self._consume("throws")
            while not self._match("{") and not self._match(";") and not self._match(TokenType.EOF):
                self._consume()

        body = []
        if self._match("{"):
            self._consume("{")
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                s = self._parse_statement()
                if s:
                    self._extend(body, s)
                elif self.pos == pos_before:
                    self.pos += 1
            self._consume("}")
        elif self._match(";"):
            self._consume(";")
        return FunctionDefNode(name=name, return_type=ret_type, params=params, body=body, line=name_tok.line if name_tok else 1)

    def _parse_var_decl(self) -> VarDeclNode:
        type_tok = self._consume()
        type_name = type_tok.value if type_tok else "int"
        is_array = False
        array_size = None
        
        # Java int[] arr or int arr[]
        if self._match("["):
            is_array = True
            self._consume("[")
            if not self._match("]"):
                array_size = self._parse_expression()
            if self._match("]"):
                self._consume("]")

        name_tok = self._consume()
        name = name_tok.value if name_tok else "x"

        if self._match("["):
            is_array = True
            self._consume("[")
            if not self._match("]"):
                array_size = self._parse_expression()
            if self._match("]"):
                self._consume("]")

        init_val = None
        if self._match("="):
            self._consume("=")
            if self._match("{"):
                self._consume("{")
                elements = []
                while not self._match("}") and not self._match(TokenType.EOF):
                    elem = self._parse_expression()
                    if elem:
                        elements.append(elem)
                    if self._match(","):
                        self._consume(",")
                if self._match("}"):
                    self._consume("}")
                init_val = ArrayLiteralNode(elements=elements, line=name_tok.line if name_tok else 1)
            elif self._match("new"):
                self._consume("new")
                # e.g. new int[5] or new int[]{1, 2, 3}
                if self._current_token() and self._current_token().value in JAVA_PRIMITIVE_TYPES:
                    self._consume()
                if self._match("["):
                    self._consume("[")
                    if not self._match("]"):
                        array_size = self._parse_expression()
                    if self._match("]"):
                        self._consume("]")
                if self._match("{"):
                    self._consume("{")
                    elements = []
                    while not self._match("}") and not self._match(TokenType.EOF):
                        elem = self._parse_expression()
                        if elem:
                            elements.append(elem)
                        if self._match(","):
                            self._consume(",")
                    if self._match("}"):
                        self._consume("}")
                    init_val = ArrayLiteralNode(elements=elements, line=name_tok.line if name_tok else 1)
            else:
                init_val = self._parse_expression()

        if self._match(";"):
            self._consume(";")
        return VarDeclNode(name=name, type_name=type_name, init_val=init_val, is_array=is_array, array_size=array_size, line=type_tok.line if type_tok else 1)

    # ------------------------------------------------------------------
    # Standard-input support: Scanner / BufferedReader
    # ------------------------------------------------------------------
    _SCAN_METHODS = {"nextInt": "int", "nextLong": "long", "nextShort": "int", "nextByte": "int",
                     "nextDouble": "double", "nextFloat": "float", "next": "string",
                     "nextLine": "line", "nextBoolean": "string"}
    _PARSE_WRAPPERS = {"Integer.parseInt": "int", "Integer.valueOf": "int", "Long.parseLong": "long",
                       "Long.valueOf": "long", "Double.parseDouble": "double", "Double.valueOf": "double",
                       "Float.parseFloat": "float", "Float.valueOf": "float"}

    def _try_reader_decl(self) -> bool:
        """Consumes `Scanner sc = new Scanner(System.in);` / `BufferedReader br = new BufferedReader(...);`"""
        t0, t1, t2 = self._current_token(), self._peek_token(1), self._peek_token(2)
        if not (t0 and t1 and t2 and t0.value in ("Scanner", "BufferedReader") and t1.type == TokenType.IDENTIFIER and t2.value == "="):
            return False
        # Only treat it as a stdin reader when System.in appears before the ';'
        i, is_stdin = self.pos, False
        while i < len(self.tokens) and self.tokens[i].value != ";":
            if self.tokens[i].value == "System" and i + 2 < len(self.tokens) and self.tokens[i + 2].value == "in":
                is_stdin = True
            i += 1
        if not is_stdin:
            return False
        (self.scanner_vars if t0.value == "Scanner" else self.reader_vars).add(t1.value)
        self.pos = i + 1
        return True

    def _strip_text_calls(self, node):
        while (isinstance(node, CallNode) and getattr(node, "receiver", None) is not None
               and node.callee.split(".")[-1] in ("trim", "strip") and not node.args):
            node = node.receiver
        return node

    def _read_kind(self, node):
        """If `node` reads stdin returns (kind, mode); otherwise None."""
        node = self._strip_text_calls(node)
        if not isinstance(node, CallNode):
            return None
        callee = node.callee
        if callee in self._PARSE_WRAPPERS and len(node.args) == 1:
            inner = self._read_kind(node.args[0])
            if inner:
                return self._PARSE_WRAPPERS[callee], inner[1]
        if callee.endswith(".charAt") and getattr(node, "receiver", None) is not None:
            inner = self._read_kind(node.receiver)
            if inner:
                return "char", inner[1]
        if "." in callee and not node.args:
            obj, meth = callee.rsplit(".", 1)
            if obj in self.scanner_vars and meth in self._SCAN_METHODS:
                kind = self._SCAN_METHODS[meth]
                return kind, ("line" if kind == "line" else "token")
            if obj in self.reader_vars and meth == "readLine":
                return "line", "line"
        return None

    def _hoist_reads(self, node, pre):
        r = self._read_kind(node)
        if r:
            self._tmp_counter += 1
            name = f"_in{self._tmp_counter}"
            kind, mode = r
            vtype = {"int": "int", "long": "long", "float": "float", "double": "double", "char": "char"}.get(kind, "String")
            line = getattr(node, "line", 1)
            pre.append(VarDeclNode(name=name, type_name=vtype, init_val=None, line=line))
            pre.append(InputNode(targets=[IdentifierNode(name=name, line=line)], kinds=[kind], mode=mode, line=line))
            return IdentifierNode(name=name, line=line)
        if isinstance(node, ASTNode):
            for k, v in list(node.__dict__.items()):
                if isinstance(v, ASTNode):
                    setattr(node, k, self._hoist_reads(v, pre))
                elif isinstance(v, list):
                    setattr(node, k, [self._hoist_reads(x, pre) if isinstance(x, ASTNode) else x for x in v])
        return node

    def _convert_reads(self, stmt):
        """Rewrites a parsed statement so that stdin reads become InputNodes."""
        if stmt is None or not (self.scanner_vars or self.reader_vars):
            return stmt
        pre: List[ASTNode] = []
        if isinstance(stmt, VarDeclNode) and stmt.init_val is not None:
            r = self._read_kind(stmt.init_val)
            if r:
                kind, mode = r
                ident = IdentifierNode(name=stmt.name, line=stmt.line)
                stmt.init_val = None
                return [stmt, InputNode(targets=[ident], kinds=[kind], mode=mode, line=stmt.line)]
            stmt.init_val = self._hoist_reads(stmt.init_val, pre)
        elif isinstance(stmt, AssignNode) and stmt.value is not None:
            r = self._read_kind(stmt.value) if stmt.op == "=" else None
            if r:
                kind, mode = r
                tgt = stmt.target_node or IdentifierNode(name=stmt.target, line=stmt.line)
                return InputNode(targets=[tgt], kinds=[kind], mode=mode, line=stmt.line)
            stmt.value = self._hoist_reads(stmt.value, pre)
        elif isinstance(stmt, ExprStmtNode) and stmt.expr is not None:
            r = self._read_kind(stmt.expr)
            if r:   # bare sc.nextLine(); -> read and discard
                kind, mode = r
                return [VarDeclNode(name="_discard", type_name="String" if kind in ("string", "line") else "int", line=stmt.line),
                        InputNode(targets=[IdentifierNode(name="_discard", line=stmt.line)], kinds=[kind], mode=mode, line=stmt.line)] if False else \
                       InputNode(targets=[IdentifierNode(name="_discard", line=stmt.line)], kinds=[kind], mode=mode, line=stmt.line)
            stmt.expr = self._hoist_reads(stmt.expr, pre)
        elif isinstance(stmt, PrintNode):
            stmt.args = [self._hoist_reads(a, pre) if isinstance(a, ASTNode) else a for a in stmt.args]
        elif isinstance(stmt, ReturnNode) and stmt.value is not None:
            stmt.value = self._hoist_reads(stmt.value, pre)
        elif isinstance(stmt, IfNode) and stmt.test is not None:
            stmt.test = self._hoist_reads(stmt.test, pre)
        if pre:
            return pre + [stmt]
        return stmt

    def _parse_statement(self):
        """Parses one statement; may return a list when stdin reads were expanded."""
        if self._try_reader_decl():
            return None
        return self._convert_reads(self._parse_statement_raw())

    @staticmethod
    def _extend(target: list, s) -> None:
        if isinstance(s, list):
            target.extend(x for x in s if x)
        elif s:
            target.append(s)

    def _parse_statement_raw(self) -> Optional[ASTNode]:
        tok = self._current_token()
        if not tok:
            return None

        # System.out.println(...)
        if tok.value == "System" and self._peek_token() and self._peek_token().value == ".":
            return self._parse_println()

        # Variable declaration
        if tok.value in JAVA_PRIMITIVE_TYPES:
            return self._parse_var_decl()

        # Return
        if tok.value == "return":
            line = tok.line
            self._consume("return")
            val = None
            if not self._match(";"):
                val = self._parse_expression()
            if self._match(";"):
                self._consume(";")
            return ReturnNode(value=val, line=line)

        # If
        if tok.value == "if":
            self._consume("if")
            self._consume("(")
            test = self._parse_expression()
            self._consume(")")
            body = self._parse_block_or_single()
            orelse = []
            if self._match("else"):
                self._consume("else")
                orelse = self._parse_block_or_single()
            return IfNode(test=test, body=body, orelse=orelse, line=tok.line)

        # While
        if tok.value == "while":
            self._consume("while")
            self._consume("(")
            test = self._parse_expression()
            self._consume(")")
            body = self._parse_block_or_single()
            return WhileNode(test=test, body=body, line=tok.line)

        # For
        if tok.value == "for":
            self._consume("for")
            self._consume("(")
            init = self._parse_statement()
            if isinstance(init, list):
                init = init[0] if init else None
            test = self._parse_expression()
            if self._match(";"):
                self._consume(";")
            step = None
            if not self._match(")"):
                curr = self._current_token()
                peek = self._peek_token()
                if curr and curr.type == TokenType.IDENTIFIER and peek and peek.value in ("++", "--"):
                    id_n = self._consume().value
                    op_v = self._consume().value
                    step = ExprStmtNode(
                        expr=UnaryOpNode(op=op_v, operand=IdentifierNode(name=id_n, line=curr.line), is_postfix=True, line=curr.line),
                        line=curr.line
                    )
                elif curr and curr.value in ("++", "--") and peek and peek.type == TokenType.IDENTIFIER:
                    op_v = self._consume().value
                    id_n = self._consume().value
                    step = ExprStmtNode(
                        expr=UnaryOpNode(op=op_v, operand=IdentifierNode(name=id_n, line=curr.line), is_postfix=False, line=curr.line),
                        line=curr.line
                    )
                else:
                    step = self._parse_statement()
                    if isinstance(step, list):
                        step = step[0] if step else None
            if self._match(")"):
                self._consume(")")
            body = self._parse_block_or_single()
            return ForNode(init=init, test=test, step=step, body=body, line=tok.line)

        # Break
        if tok.value == "break":
            self._consume("break")
            if self._match(";"):
                self._consume(";")
            return BreakNode(line=tok.line)

        # Continue
        if tok.value == "continue":
            self._consume("continue")
            if self._match(";"):
                self._consume(";")
            return ContinueNode(line=tok.line)

        # Expression, Assignment, Member Assignment, or Postfix
        lhs = self._parse_primary_expr()
        if lhs:
            line = lhs.line
            if self._match("=", "+=", "-=", "*=", "/=", "%="):
                op = self._consume().value
                val = self._parse_expression()
                if self._match(";"):
                    self._consume(";")
                target_str = self._node_to_str(lhs)
                return AssignNode(target=target_str, target_node=lhs, value=val, op=op, line=line)
            elif self._match("++", "--"):
                op = self._consume().value
                if self._match(";"):
                    self._consume(";")
                return ExprStmtNode(expr=UnaryOpNode(op=op, operand=lhs, is_postfix=True, line=line), line=line)
            else:
                full_expr = self._parse_binary_expr(0, left=lhs)
                if self._match(";"):
                    self._consume(";")
                return ExprStmtNode(expr=full_expr, line=line)

        if tok.value == ";":
            self._consume(";")
            return None

        return None

    def _parse_println(self) -> PrintNode:
        line = self._current_token().line
        self._consume("System")
        self._consume(".")
        self._consume("out")
        self._consume(".")
        method_tok = self._consume() # println or print
        is_newline = method_tok.value == "println" if method_tok else True

        self._consume("(")
        args = []
        while not self._match(")") and not self._match(TokenType.EOF):
            a = self._parse_expression()
            if a:
                args.append(a)
            if self._match(","):
                self._consume(",")
        self._consume(")")
        if self._match(";"):
            self._consume(";")
        return PrintNode(args=args, end="\n" if is_newline else "", line=line)

    def _parse_block_or_single(self) -> List[ASTNode]:
        if self._match("{"):
            self._consume("{")
            stmts = []
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                s = self._parse_statement()
                if s:
                    self._extend(stmts, s)
                elif self.pos == pos_before:
                    self.pos += 1
            self._consume("}")
            return stmts
        else:
            s = self._parse_statement()
            return list(s) if isinstance(s, list) else ([s] if s else [])

    def _parse_expression(self) -> Optional[ASTNode]:
        return self._parse_binary_expr(0)

    def _parse_binary_expr(self, min_prec: int, left: Optional[ASTNode] = None) -> Optional[ASTNode]:
        prec_map = {
            "||": 1, "&&": 2,
            "==": 3, "!=": 3,
            "<": 4, "<=": 4, ">": 4, ">=": 4,
            "+": 5, "-": 5,
            "*": 6, "/": 6, "%": 6
        }
        if left is None:
            left = self._parse_primary_expr()
        while True:
            tok = self._current_token()
            if not tok or tok.value not in prec_map or prec_map[tok.value] < min_prec:
                break
            op = self._consume().value
            right = self._parse_binary_expr(prec_map[op] + 1)
            left = BinaryOpNode(left=left, op=op, right=right, line=tok.line)
        return left

    def _parse_primary_expr(self) -> Optional[ASTNode]:
        tok = self._current_token()
        if not tok:
            return None

        if tok.type == TokenType.NUMBER:
            self._consume()
            num_val = float(tok.value) if '.' in tok.value else int(tok.value)
            expr = LiteralNode(value=num_val, lit_type="number", raw=tok.value, line=tok.line)

        elif tok.type == TokenType.STRING:
            self._consume()
            clean_str = tok.value.strip('"').strip("'")
            expr = LiteralNode(value=clean_str, lit_type="string", raw=tok.value, line=tok.line)

        elif tok.type == TokenType.BOOLEAN:
            self._consume()
            expr = LiteralNode(value=tok.value == "true", lit_type="boolean", raw=tok.value, line=tok.line)

        elif tok.value == "(":
            self._consume("(")
            inner = self._parse_expression()
            self._consume(")")
            expr = inner

        # Array literal: {1, 2, 3}
        elif tok.value == "{":
            self._consume("{")
            elements = []
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                elem = self._parse_expression()
                if elem:
                    elements.append(elem)
                if self._match(","):
                    self._consume(",")
                elif not elem and self.pos == pos_before:
                    self.pos += 1
            if self._match("}"):
                self._consume("}")
            expr = ArrayLiteralNode(elements=elements, line=tok.line)

        elif tok.type == TokenType.IDENTIFIER:
            id_tok = self._consume()
            expr = IdentifierNode(name=id_tok.value, line=id_tok.line)

        else:
            return None

        # Postfix chaining: array indexing [x], member access .x, call (x)
        while True:
            if self._match("("):
                self._consume("(")
                args = []
                while not self._match(")") and not self._match(TokenType.EOF):
                    pos_before = self.pos
                    a = self._parse_expression()
                    if a:
                        args.append(a)
                    if self._match(","):
                        self._consume(",")
                    elif not a and self.pos == pos_before:
                        self.pos += 1
                if self._match(")"):
                    self._consume(")")
                callee_name = self._node_to_str(expr)
                receiver = expr.object if isinstance(expr, MemberAccessNode) else None
                expr = CallNode(callee=callee_name, args=args, line=expr.line if expr else 1)
                if receiver is not None:
                    expr.receiver = receiver

            elif self._match("["):
                self._consume("[")
                idx_expr = self._parse_expression()
                if self._match("]"):
                    self._consume("]")
                expr = ArrayAccessNode(array=expr, index=idx_expr, line=expr.line if expr else 1)

            elif self._match("."):
                self._consume(".")
                if self._match(TokenType.IDENTIFIER):
                    member_tok = self._consume()
                    expr = MemberAccessNode(object=expr, member=member_tok.value, line=member_tok.line)
                else:
                    break
            else:
                break

        return expr

    def _node_to_str(self, node: Optional[ASTNode]) -> str:
        if not node:
            return ""
        if isinstance(node, IdentifierNode):
            return node.name
        elif isinstance(node, MemberAccessNode):
            return f"{self._node_to_str(node.object)}.{node.member}"
        elif isinstance(node, ArrayAccessNode):
            return f"{self._node_to_str(node.array)}[{self._node_to_str(node.index)}]"
        elif isinstance(node, LiteralNode):
            return str(node.value)
        elif isinstance(node, CallNode):
            return "expr"
        return "expr"
