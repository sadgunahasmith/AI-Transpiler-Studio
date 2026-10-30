"""
JavaScript Parser and Syntax Error Detector for Stage 2: Syntax Analysis.
Parses JavaScript into normalized ASTNode hierarchy.
"""
import re
from typing import List, Tuple, Optional, Any
from .ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    SyntaxErrorRecord, ASTNode, ArrayLiteralNode, ArrayAccessNode,
    StructDefNode, MemberAccessNode, InputNode, ClassDefNode, BreakNode, ContinueNode
)
from ..lexer.js_lexer import JSLexer
from ..lexer.base import Token, TokenType

class JSParser:
    """Parses JavaScript code into normalized AST nodes and detects syntax errors."""

    def __init__(self, code: str):
        self.code = code
        self.errors: List[SyntaxErrorRecord] = []
        self.tokens: List[Token] = []
        self.pos = 0

    def parse(self) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord]]:
        self._check_delimiters()

        lexer = JSLexer(self.code)
        tokens, lex_errors = lexer.tokenize()
        for le in lex_errors:
            self.errors.append(SyntaxErrorRecord(
                line=le.line, column=le.column, message=le.message,
                token_value=le.token_value, category="Lexical Error"
            ))

        self.tokens = [t for t in tokens if t.type not in (TokenType.COMMENT, TokenType.WHITESPACE, TokenType.NEWLINE)]
        self.pos = 0

        try:
            body = self._parse_statements()
            program = ProgramNode(body=body, line=1, column=1)
            return program, self.errors
        except Exception as e:
            if not self.errors:
                self.errors.append(SyntaxErrorRecord(
                    line=1, column=1, message=f"JavaScript parse error: {str(e)}",
                    category="Syntax Error"
                ))
            return None, self.errors

    def _check_delimiters(self):
        lines = self.code.split('\n')
        brace_stack = []
        paren_stack = []
        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("/*"):
                continue
            for col, ch in enumerate(raw_line, 1):
                if ch == '{':
                    brace_stack.append((line_num, col))
                elif ch == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=col, message="Unmatched closing brace '}' in JavaScript",
                            suggested_fix="Remove extra '}'"
                        ))
                elif ch == '(':
                    paren_stack.append((line_num, col))
                elif ch == ')':
                    if paren_stack:
                        paren_stack.pop()
                    else:
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=col, message="Unmatched closing parenthesis ')' in JavaScript",
                            suggested_fix="Remove extra ')'"
                        ))

        for bl, bc in brace_stack:
            self.errors.append(SyntaxErrorRecord(
                line=bl, column=bc, message="Unclosed opening brace '{' in JavaScript",
                suggested_fix="Add closing brace '}'"
            ))
        for pl, pc in paren_stack:
            self.errors.append(SyntaxErrorRecord(
                line=pl, column=pc, message="Unclosed opening parenthesis '(' in JavaScript",
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

    def _parse_statements(self) -> List[ASTNode]:
        stmts = []
        while self.pos < len(self.tokens):
            tok = self._current_token()
            if not tok or tok.type == TokenType.EOF:
                break
            pos_before = self.pos
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
            elif self.pos == pos_before:
                self.pos += 1
        return stmts

    def _parse_statement(self) -> Optional[ASTNode]:
        tok = self._current_token()
        if not tok:
            return None

        # function foo(...) { ... }
        if tok.value == "function":
            return self._parse_function()

        # class Bar { ... }
        if tok.value == "class":
            return self._parse_class()

        # let / const / var
        if tok.value in ("let", "const", "var"):
            return self._parse_var_decl()

        # console.log(...)
        if tok.value == "console" and self._peek_token() and self._peek_token().value == ".":
            return self._parse_console_log()

        # return
        if tok.value == "return":
            line = tok.line
            self._consume("return")
            val = None
            if not self._match(";"):
                val = self._parse_expression()
            if self._match(";"):
                self._consume(";")
            return ReturnNode(value=val, line=line)

        # break
        if tok.value == "break":
            line = tok.line
            self._consume("break")
            if self._match(";"):
                self._consume(";")
            return BreakNode(line=line)

        # continue
        if tok.value == "continue":
            line = tok.line
            self._consume("continue")
            if self._match(";"):
                self._consume(";")
            return ContinueNode(line=line)

        # if
        if tok.value == "if":
            return self._parse_if()

        # while
        if tok.value == "while":
            return self._parse_while()

        # for
        if tok.value == "for":
            return self._parse_for()

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

    def _parse_function(self) -> FunctionDefNode:
        fn_tok = self._consume("function")
        name_tok = self._consume()
        func_name = name_tok.value if name_tok else "anonymous"

        self._consume("(")
        params = []
        while not self._match(")") and not self._match(TokenType.EOF):
            p = self._consume()
            if p and p.value != ")":
                params.append(ParamNode(name=p.value, line=fn_tok.line))
            if self._match(","):
                self._consume(",")
        self._consume(")")

        body = []
        if self._match("{"):
            self._consume("{")
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                s = self._parse_statement()
                if s:
                    body.append(s)
                elif self.pos == pos_before:
                    self.pos += 1
            self._consume("}")
        return FunctionDefNode(name=func_name, return_type="auto", params=params, body=body, line=fn_tok.line)

    def _parse_class(self) -> ClassDefNode:
        cls_tok = self._consume("class")
        name_tok = self._consume()
        class_name = name_tok.value if name_tok else "AnonymousClass"
        fields = []
        methods = []
        body = []
        if self._match("{"):
            self._consume("{")
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                if self._match("constructor") or (self._current_token() and self._current_token().type == TokenType.IDENTIFIER and self._peek_token() and self._peek_token().value == "("):
                    m = self._parse_class_method()
                    if m:
                        methods.append(m)
                else:
                    s = self._parse_statement()
                    if s:
                        body.append(s)
                    elif self.pos == pos_before:
                        self.pos += 1
            self._consume("}")
        return ClassDefNode(name=class_name, fields=fields, methods=methods, body=body, line=cls_tok.line)

    def _parse_class_method(self) -> Optional[FunctionDefNode]:
        name_tok = self._consume()
        m_name = name_tok.value if name_tok else "method"
        self._consume("(")
        params = []
        while not self._match(")") and not self._match(TokenType.EOF):
            p = self._consume()
            if p and p.value != ")":
                params.append(ParamNode(name=p.value, line=name_tok.line if name_tok else 1))
            if self._match(","):
                self._consume(",")
        if self._match(")"):
            self._consume(")")
        body = self._parse_block_or_single()
        return FunctionDefNode(name=m_name, return_type="auto", params=params, body=body, line=name_tok.line if name_tok else 1)

    def _parse_var_decl(self) -> VarDeclNode:
        kw = self._consume()
        is_const = (kw.value == "const") if kw else False
        name_tok = self._consume()
        name = name_tok.value if name_tok else "x"
        
        init_val = None
        if self._match("="):
            self._consume("=")
            init_val = self._parse_expression()
        if self._match(";"):
            self._consume(";")
        return VarDeclNode(name=name, type_name="auto", init_val=init_val, is_const=is_const, line=kw.line)

    def _parse_console_log(self) -> PrintNode:
        tok = self._consume("console")
        self._consume(".")
        self._consume("log")
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
        return PrintNode(args=args, line=tok.line)

    def _parse_if(self) -> IfNode:
        tok = self._consume("if")
        self._consume("(")
        test = self._parse_expression()
        self._consume(")")
        body = self._parse_block_or_single()
        orelse = []
        if self._match("else"):
            self._consume("else")
            orelse = self._parse_block_or_single()
        return IfNode(test=test, body=body, orelse=orelse, line=tok.line)

    def _parse_while(self) -> WhileNode:
        tok = self._consume("while")
        self._consume("(")
        test = self._parse_expression()
        self._consume(")")
        body = self._parse_block_or_single()
        return WhileNode(test=test, body=body, line=tok.line)

    def _parse_for(self) -> ForNode:
        tok = self._consume("for")
        self._consume("(")
        init = self._parse_statement()
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
        if self._match(")"):
            self._consume(")")
        body = self._parse_block_or_single()
        return ForNode(init=init, test=test, step=step, body=body, line=tok.line)

    def _parse_block_or_single(self) -> List[ASTNode]:
        if self._match("{"):
            self._consume("{")
            stmts = []
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                s = self._parse_statement()
                if s:
                    stmts.append(s)
                elif self.pos == pos_before:
                    self.pos += 1
            self._consume("}")
            return stmts
        else:
            s = self._parse_statement()
            return [s] if s else []

    def _parse_expression(self) -> Optional[ASTNode]:
        return self._parse_binary_expr(0)

    def _parse_binary_expr(self, min_prec: int, left: Optional[ASTNode] = None) -> Optional[ASTNode]:
        prec_map = {
            "||": 1, "&&": 2,
            "===": 3, "==": 3, "!==": 3, "!=": 3,
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
            if op == "===":
                op = "=="
            elif op == "!==":
                op = "!="
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
            clean_str = tok.value.strip('"').strip("'").strip('`')
            expr = LiteralNode(value=clean_str, lit_type="string", raw=tok.value, line=tok.line)

        elif tok.type == TokenType.BOOLEAN:
            self._consume()
            expr = LiteralNode(value=tok.value == "true", lit_type="boolean", raw=tok.value, line=tok.line)

        elif tok.value == "(":
            self._consume("(")
            inner = self._parse_expression()
            self._consume(")")
            expr = inner

        # Array literal: [1, 2, 3]
        elif tok.value == "[":
            self._consume("[")
            elements = []
            while not self._match("]") and not self._match(TokenType.EOF):
                elem = self._parse_expression()
                if elem:
                    elements.append(elem)
                if self._match(","):
                    self._consume(",")
            if self._match("]"):
                self._consume("]")
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
                    a = self._parse_expression()
                    if a:
                        args.append(a)
                    if self._match(","):
                        self._consume(",")
                if self._match(")"):
                    self._consume(")")
                callee_name = self._node_to_str(expr)
                expr = CallNode(callee=callee_name, args=args, line=expr.line if expr else 1)

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
        return "expr"
