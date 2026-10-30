"""
C and C++ Parser and Syntax Error Detector for Stage 2: Syntax Analysis.
Parses C / C++ into normalized ASTNode hierarchy and detects missing semicolons,
unmatched braces, and malformed constructs.
"""
import re
from typing import List, Tuple, Optional, Any, Dict
from .ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    IncludeNode, SyntaxErrorRecord, ASTNode, ArrayLiteralNode, ArrayAccessNode,
    StructDefNode, MemberAccessNode, InputNode, BreakNode, ContinueNode, ClassDefNode
)
from ..lexer.c_lexer import CLexer
from ..lexer.base import Token, TokenType

C_PRIMITIVE_TYPES = {"int", "float", "double", "char", "void", "long", "short", "bool", "string", "auto", "unsigned", "signed"}

_SCANF_SPEC = re.compile(r"%(\*?)(\d*)(hh|h|ll|l|L|z)?(\[[^\]]*\]|[diouxXfFeEgGcs])")

def kind_for_type(type_name: Optional[str]) -> str:
    """Maps a declared C/C++/Java type name to a stdin value kind."""
    t = (type_name or "int").replace("std::", "").replace("const", "").replace("unsigned", "").replace("signed", "").strip().lower()
    if t in ("string", "str"):
        return "string"
    if t in ("char", "byte"):
        return "char"
    if t in ("float",):
        return "float"
    if t in ("double", "long double"):
        return "double"
    if t in ("long", "long long", "long int", "size_t"):
        return "long"
    return "int"

def kinds_from_scanf_format(fmt: str) -> List[str]:
    kinds: List[str] = []
    for m in _SCANF_SPEC.finditer(fmt or ""):
        if m.group(1) == "*":
            continue
        length, conv = m.group(3) or "", m.group(4)
        if conv.startswith("["):
            kinds.append("line" if "\\n" in conv or "\n" in conv else "string")
        elif conv in "diouxX":
            kinds.append("long" if length in ("l", "ll", "z") else "int")
        elif conv in "fFeEgG":
            kinds.append("double" if length in ("l", "L") else "float")
        elif conv == "c":
            kinds.append("char")
        else:
            kinds.append("string")
    return kinds

RE_CONTROL_HEADER = re.compile(r'^(if|else|while|for|switch|class|struct|namespace)\b')
RE_FUNC_HEADER = re.compile(r'^(int|void|float|double|char|bool|long|short|unsigned|signed|auto|[A-Z][a-zA-Z0-9_]*)\s+[a-zA-Z_][a-zA-Z0-9_* ]*\s*\([^)]*\)\s*\{?$')
RE_IDENT_CALL = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*')

class CParser:
    """Parses C and C++ code into normalized AST nodes and detects syntax errors."""

    def __init__(self, code: str, is_cpp: bool = False):
        self.code = code
        self.is_cpp = is_cpp
        self.errors: List[SyntaxErrorRecord] = []
        self.tokens: List[Token] = []
        self.pos = 0
        self.type_names = set(C_PRIMITIVE_TYPES)
        self.var_types: Dict[str, str] = {}

    def parse(self) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord]]:
        # Check lexical/syntax integrity first
        self._check_delimiters_and_semicolons()
        
        # Tokenize
        lexer = CLexer(self.code, is_cpp=self.is_cpp)
        tokens, lex_errors = lexer.tokenize()
        for le in lex_errors:
            self.errors.append(SyntaxErrorRecord(
                line=le.line, column=le.column, message=le.message,
                token_value=le.token_value, category="Lexical Error"
            ))

        # Filter out comments and whitespace
        self.tokens = [t for t in tokens if t.type not in (TokenType.COMMENT, TokenType.WHITESPACE, TokenType.NEWLINE)]
        self.pos = 0

        # Build AST
        try:
            body = self._parse_program_body()
            program = ProgramNode(body=body, line=1, column=1)
            return program, self.errors
        except Exception as e:
            if not self.errors:
                self.errors.append(SyntaxErrorRecord(
                    line=1, column=1, message=f"Parsing error: {str(e)}",
                    category="Syntax Error"
                ))
            return None, self.errors

    def _check_delimiters_and_semicolons(self):
        """Line-by-line validation to detect missing semicolons and unmatched brackets."""
        lines = self.code.split('\n')
        brace_stack = []
        paren_stack = []

        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.strip()

            # Ignore empty lines, preprocessor directives, or comments
            if not line or line.startswith('#') or line.startswith('//') or line.startswith('/*') or line.endswith('*/'):
                continue

            # Track braces and parens
            for col, ch in enumerate(raw_line, 1):
                if ch == '{':
                    brace_stack.append((line_num, col))
                elif ch == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=col,
                            message="Unmatched closing brace '}'",
                            suggested_fix="Remove extra '}' or add opening '{'"
                        ))
                elif ch == '(':
                    paren_stack.append((line_num, col))
                elif ch == ')':
                    if paren_stack:
                        paren_stack.pop()
                    else:
                        self.errors.append(SyntaxErrorRecord(
                            line=line_num, column=col,
                            message="Unmatched closing parenthesis ')'",
                            suggested_fix="Remove extra ')' or add opening '('"
                        ))

            # Missing semicolon check:
            # Lines that are statements and do not end in ';' or '{' or '}' or ':' or '\'
            # Should have a semicolon.
            # E.g.: `int a = 10`, `printf("%d", a + b)`, `return 0`
            needs_semicolon = False
            first_word = line.split()[0] if line.split() else ""
            
            # If line is header of function, if, while, for, do, switch, class, namespace -> doesn't need ';'
            is_control_header = (
                bool(RE_CONTROL_HEADER.match(line)) or
                bool(RE_FUNC_HEADER.match(line)) or
                line.endswith('{') or line.endswith('}') or line.endswith(':')
            )

            if not is_control_header:
                # Statements that need semicolons: variable declarations, return, expressions, printf, cout, assignments
                if (first_word in C_PRIMITIVE_TYPES or
                    first_word in self.type_names or
                    line.startswith("return") or
                    line.startswith("printf") or
                    line.startswith("scanf") or
                    line.startswith("cout") or
                    line.startswith("cin") or
                    line.startswith("std::") or
                    "=" in line or
                    bool(RE_IDENT_CALL.match(line))):
                    
                    if not line.endswith(';') and not line.endswith('{') and not line.endswith('}'):
                        needs_semicolon = True

            if needs_semicolon:
                self.errors.append(SyntaxErrorRecord(
                    line=line_num,
                    column=len(raw_line) + 1,
                    message=f"Missing semicolon ';' at end of statement: '{line}'",
                    token_value=line,
                    severity="error",
                    source="compiler",
                    category="Syntax Error",
                    suggested_fix=f"Add semicolon ';' after '{line}'"
                ))

        for b_line, b_col in brace_stack:
            self.errors.append(SyntaxErrorRecord(
                line=b_line, column=b_col,
                message="Unclosed opening brace '{'",
                suggested_fix="Add closing brace '}'"
            ))

        for p_line, p_col in paren_stack:
            self.errors.append(SyntaxErrorRecord(
                line=p_line, column=p_col,
                message="Unclosed opening parenthesis '('",
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

    def _match(self, *types_or_values) -> bool:
        tok = self._current_token()
        if not tok:
            return False
        for item in types_or_values:
            if isinstance(item, TokenType) and tok.type == item:
                return True
            if isinstance(item, str) and tok.value == item:
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

    def _parse_program_body(self) -> List[ASTNode]:
        nodes = []
        while self.pos < len(self.tokens):
            tok = self._current_token()
            if not tok or tok.type == TokenType.EOF:
                break

            # Preprocessor #include
            if tok.type == TokenType.PREPROCESSOR:
                self._consume()
                header_match = re.search(r'include\s*[<"]([^>"]+)[>"]', tok.value)
                header = header_match.group(1) if header_match else "stdio.h"
                nodes.append(IncludeNode(header=header, is_system='<' in tok.value, line=tok.line, column=tok.column))
                continue

            # "using namespace std;" in C++
            if tok.value == "using":
                self._skip_until(";")
                continue

            pos_before = self.pos
            stmt = self._parse_top_level()
            if isinstance(stmt, list):
                nodes.extend(stmt)
            elif stmt:
                nodes.append(stmt)
            elif self.pos == pos_before:
                self.pos += 1
        return nodes

    def _node_to_str(self, node: Optional[ASTNode]) -> str:
        if not node:
            return ""
        if isinstance(node, IdentifierNode):
            return node.name
        elif isinstance(node, ArrayAccessNode):
            return f"{self._node_to_str(node.array)}[{self._node_to_str(node.index)}]"
        elif isinstance(node, MemberAccessNode):
            return f"{self._node_to_str(node.object)}.{node.member}"
        elif isinstance(node, LiteralNode):
            return str(node.value)
        return ""

    def _parse_top_level(self) -> Optional[ASTNode]:
        tok = self._current_token()
        if not tok:
            return None

        # Struct or Class definition
        if tok.value in ("struct", "class"):
            p1 = self._peek_token(1)
            p2 = self._peek_token(2)
            if p1 and p1.type == TokenType.IDENTIFIER and p2 and p2.value == "{":
                return self._parse_struct_def()
            elif p1 and p1.type == TokenType.IDENTIFIER:
                self._consume() # consume 'struct'
                return self._parse_declaration_or_assignment()

        # Check function: type name(params) { ... }
        CONTROL_KEYWORDS = {"if", "while", "for", "switch", "return", "else", "do", "break", "continue", "struct", "class"}
        if (tok.value in self.type_names or (tok.type == TokenType.IDENTIFIER and tok.value not in CONTROL_KEYWORDS)):
            p1 = self._peek_token(1)
            p2 = self._peek_token(2)
            if p1 and p1.type == TokenType.IDENTIFIER and p2 and p2.value == "(":
                return self._parse_function()
            elif tok.value in self.type_names:
                return self._parse_declaration_or_assignment()

        return self._parse_statement()

    def _parse_struct_def(self) -> Optional[StructDefNode]:
        kw_tok = self._consume() # 'struct' or 'class'
        name_tok = self._consume()
        struct_name = name_tok.value if name_tok else "Anonymous"
        self.type_names.add(struct_name)
        self.type_names.add(f"struct {struct_name}")

        fields = []
        methods = []
        if self._match("{"):
            self._consume("{")
            while not self._match("}") and not self._match(TokenType.EOF):
                tok = self._current_token()
                if not tok:
                    break
                if tok.value in ("public", "private", "protected"):
                    self._consume()
                    if self._match(":"):
                        self._consume(":")
                    continue
                if tok.value == ";":
                    self._consume(";")
                    continue
                p1 = self._peek_token(1)
                p2 = self._peek_token(2)
                if p1 and p1.type == TokenType.IDENTIFIER and p2 and p2.value == "(":
                    method = self._parse_function()
                    if method:
                        methods.append(method)
                else:
                    field_decl = self._parse_declaration_or_assignment()
                    if field_decl:
                        fields.append(field_decl)
                    else:
                        self.pos += 1
            if self._match("}"):
                self._consume("}")

        if self._match(TokenType.IDENTIFIER):
            alias_tok = self._consume()
            self.type_names.add(alias_tok.value)
        if self._match(";"):
            self._consume(";")

        return StructDefNode(name=struct_name, fields=fields, methods=methods, line=kw_tok.line if kw_tok else 1)

    def _parse_function(self) -> Optional[FunctionDefNode]:
        ret_type_tok = self._consume()
        ret_type = ret_type_tok.value if ret_type_tok else "void"
        
        name_tok = self._consume()
        func_name = name_tok.value if name_tok else "main"

        self._consume("(")
        params = []
        while not self._match(")") and not self._match(TokenType.EOF):
            if self._match("const"):
                self._consume("const")
            p_type_tok = self._consume()
            p_type = p_type_tok.value if p_type_tok else "auto"
            while self._match("*", "&"):
                self._consume()
            p_name_tok = self._consume()
            p_name = p_name_tok.value if p_name_tok else "p"
            if self._match("["):
                self._consume("[")
                if not self._match("]"):
                    self._parse_expression()
                if self._match("]"):
                    self._consume("]")
            def_val = None
            if self._match("="):
                self._consume("=")
                def_val = self._parse_expression()
            if p_name and p_name != ")":
                params.append(ParamNode(name=p_name, type_name=p_type, default_val=def_val, line=p_type_tok.line if p_type_tok else 1))
            if self._match(","):
                self._consume(",")
        if self._match(")"):
            self._consume(")")

        # Parse body enclosed in { ... }
        body = []
        if self._match("{"):
            self._consume("{")
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                stmt = self._parse_statement()
                if isinstance(stmt, list):
                    body.extend(stmt)
                elif stmt:
                    body.append(stmt)
                elif self.pos == pos_before:
                    tok = self._current_token()
                    if tok and tok.value == "}":
                        break
                    self.pos += 1
            if self._match("}"):
                self._consume("}")
        return FunctionDefNode(name=func_name, return_type=ret_type, params=params, body=body, line=ret_type_tok.line if ret_type_tok else 1)

    def _parse_statement(self) -> Optional[ASTNode]:
        tok = self._current_token()
        if not tok:
            return None

        # Semicolon skip
        if tok.value == ";":
            self._consume(";")
            return None

        # Struct or Class definition
        if tok.value in ("struct", "class"):
            p1 = self._peek_token(1)
            p2 = self._peek_token(2)
            if p1 and p1.type == TokenType.IDENTIFIER and p2 and p2.value == "{":
                return self._parse_struct_def()
            elif p1 and p1.type == TokenType.IDENTIFIER:
                self._consume() # consume 'struct'
                return self._parse_declaration_or_assignment()

        # Variable declaration: `int a = 10;` or `Employee emp[10];`
        if tok.value in self.type_names:
            return self._parse_declaration_or_assignment()

        # printf(...)
        if tok.value == "printf":
            return self._parse_printf()

        # scanf(...)
        if tok.value == "scanf":
            return self._parse_scanf()

        # getline(cin, s) / std::getline(cin, s) / fgets(buf, n, stdin) / gets(buf) / getchar()
        if tok.value in ("getline", "fgets", "gets", "getchar") or (
            tok.value == "std" and self._peek_token(2) and self._peek_token(2).value == "getline"
        ):
            node = self._parse_line_input()
            if node is not None:
                return node

        # cin.ignore(); cin.get(); cin.clear(); cin.sync_with_stdio(...)
        if tok.value == "cin" and self._peek_token() and self._peek_token().value == ".":
            self._skip_until(";")
            return None
        if tok.value == "ios" or (tok.value == "ios_base"):
            self._skip_until(";")
            return None

        # C++ cin >> ...
        if tok.value in ("cin", "std::cin") or (tok.value == "std" and self._peek_token() and self._peek_token().value == "::" and self._peek_token(2) and self._peek_token(2).value == "cin"):
            return self._parse_cin()

        # C++ cout << ...
        if tok.value in ("cout", "std::cout") or (tok.value == "std" and self._peek_token() and self._peek_token().value == "::" and self._peek_token(2) and self._peek_token(2).value == "cout"):
            return self._parse_cout()

        # return ...
        if tok.value == "return":
            line = tok.line
            self._consume("return")
            val = None
            if not self._match(";"):
                val = self._parse_expression()
            if self._match(";"):
                self._consume(";")
            return ReturnNode(value=val, line=line)

        # break / continue
        if tok.value == "break":
            line = tok.line
            self._consume("break")
            if self._match(";"):
                self._consume(";")
            return BreakNode(line=line)
        if tok.value == "continue":
            line = tok.line
            self._consume("continue")
            if self._match(";"):
                self._consume(";")
            return ContinueNode(line=line)

        # if / else
        if tok.value == "if":
            return self._parse_if()

        # while
        if tok.value == "while":
            return self._parse_while()

        # for
        if tok.value == "for":
            return self._parse_for()

        # Expression or Assignment or Postfix
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

        self.pos += 1
        return None

    def _parse_declaration_or_assignment(self):
        """Parses `int a = 1, b, c[3];` -> VarDeclNode (or a list when several declarators)."""
        type_tok = self._consume()
        type_name = type_tok.value if type_tok else "int"
        if type_name == "struct" and self._match(TokenType.IDENTIFIER):
            struct_tok = self._consume()
            type_name = struct_tok.value if struct_tok else "struct"
        # Collapse modifiers: unsigned int / long long / long double ...
        while self._match("int", "long", "short", "double", "char") and type_name in ("unsigned", "signed", "long", "short"):
            nxt = self._consume().value
            if type_name in ("unsigned", "signed"):
                type_name = nxt if nxt != "int" else "int"
            elif type_name == "long" and nxt == "double":
                type_name = "double"
            else:
                type_name = "long" if "long" in (type_name, nxt) else type_name
        if type_name in ("unsigned", "signed"):
            type_name = "int"

        decls = []
        while True:
            while self._match("*", "&"):
                self._consume()
            name_tok = self._consume()
            name = name_tok.value if name_tok else "x"

            is_array = False
            array_size = None
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
                    init_val = ArrayLiteralNode(elements=elements, line=name_tok.line if name_tok else type_tok.line)
                else:
                    init_val = self._parse_expression()

            self.var_types[name] = type_name
            decls.append(VarDeclNode(name=name, type_name=type_name, init_val=init_val, is_array=is_array, array_size=array_size, line=type_tok.line))
            if self._match(","):
                self._consume(",")
                continue
            break

        if self._match(";"):
            self._consume(";")

        return decls[0] if len(decls) == 1 else decls

    def _parse_printf(self) -> PrintNode:
        tok = self._consume("printf")
        line = tok.line
        self._consume("(")
        
        args = []
        while not self._match(")") and not self._match(TokenType.EOF) and not self._match(";"):
            before = self.pos
            arg_expr = self._parse_expression()
            if arg_expr:
                args.append(arg_expr)
            if self._match(","):
                self._consume(",")
            elif self.pos == before:
                self.pos += 1
        self._consume(")")
        if self._match(";"):
            self._consume(";")

        fmt = None
        if args and isinstance(args[0], LiteralNode) and args[0].lit_type == "string":
            fmt = str(args[0].value)

        # printf("literal\n") -> print literal
        if fmt is not None and len(args) == 1 and "%" not in fmt:
            end_str = ""
            if fmt.endswith("\\n"):
                fmt, end_str = fmt[:-2], "\n"
            elif fmt.endswith("\n"):
                fmt, end_str = fmt[:-1], "\n"
            return PrintNode(args=[LiteralNode(value=fmt, lit_type="string", raw='"' + fmt + '"', line=line)],
                             format_str=fmt, end=end_str, line=line)

        if fmt is None:
            return PrintNode(args=list(args), end="", line=line)

        spec_re = re.compile(r"%(%|[-+ #0]*(\d+|\*)?(?:\.(\d+|\*))?(hh|h|ll|l|L|z|j|t)?([diouxXeEfFgGcspn]))")
        specs = list(spec_re.finditer(fmt))
        real = [m for m in specs if m.group(1) != "%"]
        simple = len(real) == len(args) - 1 and all(
            m.group(0)[1:-1] in ("", "l", "ll", "h", "hh", "z") and m.group(5) in "diucs" for m in real
        )
        if simple:
            out_args: List[ASTNode] = []
            pos, ai = 0, 1
            def add_text(txt):
                if txt:
                    out_args.append(LiteralNode(value=txt.replace("%%", "%"), lit_type="string", raw='"' + txt + '"', line=line))
            for m in specs:
                add_text(fmt[pos:m.start()])
                if m.group(1) == "%":
                    add_text("%")
                else:
                    out_args.append(args[ai]); ai += 1
                pos = m.end()
            tail = fmt[pos:]
            end_str = ""
            if tail.endswith("\\n"):
                tail, end_str = tail[:-2], "\n"
            elif tail.endswith("\n"):
                tail, end_str = tail[:-1], "\n"
            add_text(tail)
            if not out_args:
                out_args.append(LiteralNode(value="", lit_type="string", raw='""', line=line))
            return PrintNode(args=out_args, format_str=fmt, end=end_str, line=line)

        # Complex conversion specs (%.2f, %5d, %x ...) -> keep a faithful printf
        return PrintNode(args=list(args[1:]), format_str=fmt, end="", raw_printf=True, line=line)

    def _strip_input_target(self, a: ASTNode) -> ASTNode:
        if isinstance(a, UnaryOpNode) and a.op == "&" and a.operand is not None:
            return a.operand
        return a

    def _parse_scanf(self) -> InputNode:
        tok = self._consume("scanf")
        line = tok.line
        self._consume("(")
        args = []
        while not self._match(")") and not self._match(TokenType.EOF) and not self._match(";"):
            before = self.pos
            arg = self._parse_expression()
            if arg:
                args.append(arg)
            if self._match(","):
                self._consume(",")
            elif self.pos == before:
                self.pos += 1
        if self._match(")"):
            self._consume(")")
        if self._match(";"):
            self._consume(";")

        fmt = ""
        if args and isinstance(args[0], LiteralNode) and args[0].lit_type == "string":
            fmt = str(args[0].raw if args[0].raw else args[0].value)
        targets = [self._strip_input_target(a) for a in args[1:]]
        kinds = kinds_from_scanf_format(fmt)
        # Fall back to declared types when the format string could not be decoded
        for i, t in enumerate(targets):
            if i >= len(kinds):
                kinds.append(kind_for_type(self.var_types.get(self._node_to_str(t).split("[")[0])))
        kinds = kinds[:len(targets)]
        # %s into a char array and %c into a char are fine; a %d into an array element is too
        return InputNode(targets=targets, kinds=kinds, mode="token", line=line)

    def _parse_cin(self) -> InputNode:
        tok = self._consume()
        if tok.value == "std":
            self._consume("::")
            self._consume("cin")
        line = tok.line

        targets = []
        while self._match(">>"):
            self._consume(">>")
            before = self.pos
            t = self._parse_primary_expr()
            if t:
                targets.append(t)
            elif self.pos == before:
                break
        if self._match(";"):
            self._consume(";")
        kinds = []
        for t in targets:
            base = self._node_to_str(t).split("[")[0]
            kinds.append(kind_for_type(self.var_types.get(base)))
        return InputNode(targets=targets, kinds=kinds, mode="token", line=line)

    def _parse_line_input(self) -> Optional[InputNode]:
        """getline(cin, s); fgets(buf, n, stdin); gets(buf); getchar()."""
        start = self.pos
        tok = self._consume()
        if tok.value == "std":
            self._consume("::")
            tok = self._consume()
        line = tok.line
        if not self._match("("):
            self.pos = start
            return None
        self._consume("(")
        args = []
        while not self._match(")") and not self._match(TokenType.EOF) and not self._match(";"):
            before = self.pos
            a = self._parse_expression()
            if a:
                args.append(a)
            if self._match(","):
                self._consume(",")
            elif self.pos == before:
                self.pos += 1
        if self._match(")"):
            self._consume(")")
        if self._match(";"):
            self._consume(";")
        if tok.value == "getline" and len(args) >= 2:
            return InputNode(targets=[args[1]], kinds=["line"], mode="line", line=line)
        if tok.value in ("fgets", "gets") and args:
            return InputNode(targets=[self._strip_input_target(args[0])], kinds=["line"], mode="line", line=line)
        # bare getchar(); -> discard one character
        return None

    def _parse_cout(self) -> Optional[ASTNode]:
        tok = self._consume()
        if tok.value == "std":
            self._consume("::")
            self._consume("cout")
        line = tok.line

        args = []
        has_endl = False
        while self._match("<<"):
            self._consume("<<")
            before = self.pos
            expr = self._parse_expression()
            if expr:
                if isinstance(expr, IdentifierNode) and expr.name in ("endl", "std::endl"):
                    has_endl = True
                    continue
                if isinstance(expr, IdentifierNode) and expr.name in ("fixed", "std::fixed"):
                    continue
                if isinstance(expr, CallNode) and expr.callee in ("setprecision", "std::setprecision", "setw", "std::setw"):
                    continue
                args.append(expr)
            elif self.pos == before:
                break
        if self._match(";"):
            self._consume(";")
        # a trailing "\n" string literal behaves like endl
        if args and isinstance(args[-1], LiteralNode) and args[-1].lit_type == "string":
            v = str(args[-1].value)
            if v.endswith("\\n") or v.endswith("\n"):
                has_endl = True
                v = v[:-2] if v.endswith("\\n") else v[:-1]
                if v:
                    args[-1] = LiteralNode(value=v, lit_type="string", raw='"' + v + '"', line=line)
                else:
                    args.pop()
        if not args and not has_endl:
            return None
        return PrintNode(args=args, end="\n" if has_endl else "", line=line)

    def _parse_if(self) -> IfNode:
        tok = self._consume("if")
        line = tok.line
        self._consume("(")
        test = self._parse_expression()
        self._consume(")")

        body = self._parse_block_or_single()
        orelse = []
        if self._match("else"):
            self._consume("else")
            orelse = self._parse_block_or_single()

        return IfNode(test=test, body=body, orelse=orelse, line=line)

    def _parse_while(self) -> WhileNode:
        tok = self._consume("while")
        line = tok.line
        self._consume("(")
        test = self._parse_expression()
        self._consume(")")
        body = self._parse_block_or_single()
        return WhileNode(test=test, body=body, line=line)

    def _parse_for(self) -> ForNode:
        tok = self._consume("for")
        line = tok.line
        self._consume("(")
        init = self._parse_statement()
        if isinstance(init, list):
            init = init[0] if init else None
        test = self._parse_expression()
        if self._match(";"):
            self._consume(";")
        step = None
        if not self._match(")"):
            # Check for i++ / i--
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
        return ForNode(init=init, test=test, step=step, body=body, line=line)

    def _parse_block_or_single(self) -> List[ASTNode]:
        if self._match("{"):
            self._consume("{")
            stmts = []
            while not self._match("}") and not self._match(TokenType.EOF):
                pos_before = self.pos
                s = self._parse_statement()
                if isinstance(s, list):
                    stmts.extend(s)
                elif s:
                    stmts.append(s)
                elif self.pos == pos_before:
                    self.pos += 1
            if self._match("}"):
                self._consume("}")
            return stmts
        else:
            s = self._parse_statement()
            if isinstance(s, list):
                return s
            return [s] if s else []

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
            next_min_prec = prec_map[op] + 1
            right = self._parse_binary_expr(next_min_prec)
            left = BinaryOpNode(left=left, op=op, right=right, line=tok.line if tok else 1)
        return left

    def _parse_primary_expr(self) -> Optional[ASTNode]:
        tok = self._current_token()
        if not tok:
            return None

        # Prefix unary operators: &x  -x  !x  *p  ~x  +x  ++x  --x
        if tok.type == TokenType.OPERATOR and tok.value in ("&", "-", "!", "*", "~", "+", "++", "--"):
            op_tok = self._consume()
            operand = self._parse_primary_expr()
            return UnaryOpNode(op=op_tok.value, operand=operand, is_postfix=False, line=op_tok.line)
        if tok.value in ("&", "-", "!", "*", "~", "+", "++", "--") and tok.type != TokenType.STRING:
            op_tok = self._consume()
            operand = self._parse_primary_expr()
            return UnaryOpNode(op=op_tok.value, operand=operand, is_postfix=False, line=op_tok.line)

        # Number
        if tok.type == TokenType.NUMBER:
            self._consume()
            num_val = float(tok.value) if '.' in tok.value else int(tok.value)
            expr = LiteralNode(value=num_val, lit_type="number", raw=tok.value, line=tok.line)

        # String
        elif tok.type == TokenType.STRING:
            self._consume()
            clean_str = tok.value.strip('"').strip("'")
            expr = LiteralNode(value=clean_str, lit_type="string", raw=tok.value, line=tok.line)

        # Boolean
        elif tok.type == TokenType.BOOLEAN or tok.value in ("true", "false"):
            self._consume()
            expr = LiteralNode(value=tok.value.lower() == "true", lit_type="boolean", raw=tok.value, line=tok.line)

        # Parenthesized expression: ( expr )
        elif tok.value == "(":
            self._consume("(")
            inner = self._parse_expression()
            if self._match(")"):
                self._consume(")")
            expr = inner

        # Identifier or non-control keyword (e.g. endl, string, cin, cout)
        elif tok.type == TokenType.IDENTIFIER or (tok.type == TokenType.KEYWORD and tok.value not in {"if", "while", "for", "switch", "return", "else", "do", "break", "continue", "struct", "class"}):
            id_tok = self._consume()
            expr = IdentifierNode(name=id_tok.value, line=id_tok.line)

        else:
            return None

        # Postfix chaining: array indexing [x], member access .x or ->x, call (x)
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
                callee_name = expr.name if isinstance(expr, IdentifierNode) else self._node_to_str(expr)
                expr = CallNode(callee=callee_name, args=args, line=expr.line)
            elif self._match("["):
                self._consume("[")
                idx_expr = self._parse_expression()
                if self._match("]"):
                    self._consume("]")
                expr = ArrayAccessNode(array=expr, index=idx_expr, line=expr.line)
            elif self._match(".", "->"):
                self._consume()
                member_tok = self._consume()
                member_name = member_tok.value if member_tok else ""
                expr = MemberAccessNode(object=expr, member=member_name, line=expr.line)
            else:
                break

        return expr

    def _skip_until(self, target_val: str):
        while self.pos < len(self.tokens):
            if self.tokens[self.pos].value == target_val:
                self.pos += 1
                break
            self.pos += 1
