"""
C++ Code Generator for Stage 6: Code Generation.
Generates clean, compilable C++ source code from normalized AST.
"""
from typing import List, Optional
from .input_utils import string_input_names, kind_of, sanitize_printf_format
from ..parser.ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, RangeForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    ASTNode, ArrayLiteralNode, ArrayAccessNode, StructDefNode, MemberAccessNode,
    InputNode, ClassDefNode, BreakNode, ContinueNode,
    TryCatchNode, CatchClauseNode, ThrowNode, LambdaExprNode, CastExprNode,
    NamespaceDefNode, EnumDefNode, TemplateDefNode, UsingDirectiveNode, TypeAliasNode,
    SwitchNode, CaseNode, ConditionalExprNode, UnsupportedASTNode
)

class CPPCodeGen:
    """Emits clean, compilable C++ source code from normalized AST."""

    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.indent_level = 0
        self.lines: List[str] = []

    _CPP_TYPE = {"int": "int", "long": "long long", "float": "float", "double": "double", "char": "char",
                 "string": "string", "line": "string", "int_list": "vector<int>",
                 "float_list": "vector<double>", "string_list": "vector<string>"}

    def _emit_input(self, stmt) -> None:
        ind = self._indent()
        mode = getattr(stmt, "mode", "token") or "token"
        targets = list(stmt.targets)
        kinds = [kind_of(stmt, i) for i in range(len(targets))]
        if not hasattr(self, "declared_vars"):
            self.declared_vars = set()
        for t, k in zip(targets, kinds):
            if isinstance(t, IdentifierNode) and t.name not in self.declared_vars and self.indent_level > 0:
                self.declared_vars.add(t.name)
                self.lines.append(f"{ind}{self._CPP_TYPE.get(k, 'int')} {t.name};")
        names = [self._emit_expr(t) for t in targets]

        if mode == "line" and targets:
            for n, k in zip(names, kinds):
                if k in ("string", "line"):
                    self.lines.append(f"{ind}getline(cin, {n}); if (!{n}.empty() && {n}.back() == '\\r') {n}.pop_back();")
                elif k in ("int", "long", "float", "double", "char"):
                    conv = {"int": f"{n} = stoi(_ln);", "long": f"{n} = stoll(_ln);", "float": f"{n} = stof(_ln);",
                            "double": f"{n} = stod(_ln);", "char": f"{n} = _ln.empty() ? ' ' : _ln[0];"}[k]
                    self.lines.append(f"{ind}{{ string _ln; getline(cin, _ln); {conv} }}")
                else:
                    elem = {"int_list": "int", "float_list": "double", "string_list": "string"}.get(k, "int")
                    self.lines.append(f"{ind}{{ string _ln; getline(cin, _ln); istringstream _ss(_ln); {elem} _v; while (_ss >> _v) {n}.push_back(_v); }}")
            return

        simple = [(n, k) for n, k in zip(names, kinds)]
        chunk = []
        def flush():
            if chunk:
                self.lines.append(f"{ind}cin >> " + " >> ".join(chunk) + ";")
                chunk.clear()
        for n, k in simple:
            if k == "line":
                flush()
                self.lines.append(f"{ind}getline(cin, {n});")
            else:
                chunk.append(n)
        flush()
        if mode == "line_tokens":
            self.lines.append(f"{ind}{{ string _rest; getline(cin, _rest); }}")

    def generate(self, ast_root: Optional[ProgramNode]) -> str:
        if not ast_root or not ast_root.body:
            return '#include <iostream>\n\nint main() {\n    return 0;\n}\n'

        self.lines = [
            '#include <iostream>',
            '#include <cstdio>',
            '#include <string>',
            '#include <vector>',
            '#include <map>',
            '#include <memory>',
            '#include <algorithm>',
            '#include <numeric>',
            '#include <sstream>',
            '#include <fstream>',
            '#include <stdexcept>',
            'using namespace std;',
            ''
        ]
        self.indent_level = 0

        main_fn = None
        for s in ast_root.body:
            if isinstance(s, FunctionDefNode) and s.name == "main":
                main_fn = s
                break

        DEF_TYPES = (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, TemplateDefNode, EnumDefNode, UsingDirectiveNode, TypeAliasNode, VarDeclNode)
        for s in ast_root.body:
            if s is not main_fn and isinstance(s, DEF_TYPES):
                self._emit_stmt(s)
                if isinstance(s, (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, TemplateDefNode, EnumDefNode)):
                    self.lines.append("")

        if main_fn:
            self._emit_function(main_fn)
        else:
            has_exec = any(not isinstance(s, DEF_TYPES) for s in ast_root.body)
            if has_exec:
                self.lines.append("int main() {")
                self.indent_level += 1
                prev_vars = getattr(self, "declared_vars", set()).copy()
                self.declared_vars = set()
                for s in ast_root.body:
                    if not isinstance(s, (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, TemplateDefNode, EnumDefNode, UsingDirectiveNode, TypeAliasNode)):
                        self._emit_stmt(s)
                self.lines.append(f"{self._indent()}return 0;")
                self.declared_vars = prev_vars
                self.indent_level -= 1
                self.lines.append("}")

        return "\n".join(self.lines).strip() + "\n"

    def _indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)

    def _emit_function(self, fn: FunctionDefNode):
        prefixes = []
        if getattr(fn, "is_constexpr", False):
            prefixes.append("constexpr")
        if getattr(fn, "is_static", False):
            prefixes.append("static")
        if getattr(fn, "is_virtual", False):
            prefixes.append("virtual")

        has_val_ret = any(isinstance(s, ReturnNode) and s.value is not None for s in fn.body)
        if fn.name == "main":
            ret_type = "int"
        elif fn.return_type and fn.return_type != "auto":
            ret_type = fn.return_type
        elif has_val_ret:
            ret_type = "int"
        else:
            ret_type = "void"

        pfx_str = (" ".join(prefixes) + " ") if prefixes else ""

        params = []
        if fn.name == "main":
            if fn.params and any(p.name in ("argc", "argv") for p in fn.params):
                for p in fn.params:
                    p_type = p.type_name if p.type_name and p.type_name != "auto" else "int"
                    default_str = f" = {self._emit_expr(p.default_val)}" if getattr(p, "default_val", None) else ""
                    params.append(f"{p_type} {p.name}{default_str}")
                params_str = ", ".join(params)
            else:
                params_str = ""
        else:
            for p in fn.params:
                p_type = p.type_name if p.type_name and p.type_name != "auto" else "int"
                default_str = f" = {self._emit_expr(p.default_val)}" if getattr(p, "default_val", None) else ""
                params.append(f"{p_type} {p.name}{default_str}")
            params_str = ", ".join(params) if params else ""

        suffixes = []
        if getattr(fn, "is_const", False):
            suffixes.append("const")
        if getattr(fn, "is_noexcept", False):
            suffixes.append("noexcept")
        if getattr(fn, "is_override", False):
            suffixes.append("override")
        if getattr(fn, "is_pure_virtual", False):
            suffixes.append("= 0")

        sfx_str = (" " + " ".join(suffixes)) if suffixes else ""

        if getattr(fn, "is_pure_virtual", False):
            self.lines.append(f"{self._indent()}{pfx_str}{ret_type} {fn.name}({params_str}){sfx_str};")
            return

        self.lines.append(f"{self._indent()}{pfx_str}{ret_type} {fn.name}({params_str}){sfx_str} {{")
        self.indent_level += 1
        prev_vars = getattr(self, "declared_vars", set()).copy()
        self.declared_vars = {p.name for p in fn.params}
        has_ret = False
        for s in fn.body:
            if isinstance(s, ReturnNode):
                has_ret = True
            self._emit_stmt(s)
        if fn.name == "main" and not has_ret:
            self.lines.append(f"{self._indent()}return 0;")
        self.declared_vars = prev_vars
        self.indent_level -= 1
        self.lines.append(f"{self._indent()}}}")
        self.lines.append("")

    def _emit_stmt(self, stmt: ASTNode):
        if isinstance(stmt, NamespaceDefNode):
            self.lines.append(f"{self._indent()}namespace {stmt.name} {{")
            self.indent_level += 1
            for item in stmt.body:
                self._emit_stmt(item)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, TemplateDefNode):
            t_params = ", ".join(stmt.params) if stmt.params else "typename T"
            self.lines.append(f"{self._indent()}template <{t_params}>")
            if stmt.declaration:
                self._emit_stmt(stmt.declaration)

        elif isinstance(stmt, EnumDefNode):
            scoped = "class " if stmt.is_scoped else ""
            base = f" : {stmt.base_type}" if stmt.base_type else ""
            self.lines.append(f"{self._indent()}enum {scoped}{stmt.name}{base} {{")
            self.indent_level += 1
            for name, val in stmt.enumerators:
                val_str = f" = {self._emit_expr(val)}" if val else ""
                self.lines.append(f"{self._indent()}{name}{val_str},")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}};")

        elif isinstance(stmt, UsingDirectiveNode):
            if stmt.target:
                self.lines.append(f"{self._indent()}using namespace {stmt.target};")

        elif isinstance(stmt, TypeAliasNode):
            self.lines.append(f"{self._indent()}using {stmt.name} = {stmt.target_type};")

        elif isinstance(stmt, FunctionDefNode):
            self._emit_function(stmt)

        elif isinstance(stmt, StructDefNode):
            bases = ""
            if stmt.base_classes:
                bases = " : " + ", ".join(f"{acc} {bname}" for bname, acc, _ in stmt.base_classes)
            self.lines.append(f"{self._indent()}struct {stmt.name}{bases} {{")
            self.indent_level += 1
            for f in stmt.fields:
                self._emit_stmt(f)
            for m in stmt.methods:
                if isinstance(m, FunctionDefNode):
                    self._emit_function(m)
                else:
                    self._emit_stmt(m)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}};")

        elif isinstance(stmt, ClassDefNode):
            bases = ""
            if stmt.base_classes:
                bases = " : " + ", ".join(f"{acc} {bname}" for bname, acc, _ in stmt.base_classes)
            is_struct = getattr(stmt, "is_struct", False)
            tag = "struct" if is_struct else "class"
            self.lines.append(f"{self._indent()}{tag} {stmt.name}{bases} {{")
            self.indent_level += 1
            if not is_struct:
                self.lines.append(f"{self._indent()}public:")
            for f in stmt.fields:
                self._emit_stmt(f)
            for m in stmt.methods:
                if isinstance(m, FunctionDefNode):
                    self._emit_function(m)
                else:
                    self._emit_stmt(m)
            if stmt.body:
                for b in stmt.body:
                    if b not in stmt.fields and b not in stmt.methods:
                        self._emit_stmt(b)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}};")

        elif isinstance(stmt, RangeForNode):
            v_name = stmt.var.name if stmt.var else "item"
            v_type = stmt.var.type_name if (stmt.var and stmt.var.type_name and stmt.var.type_name != "auto") else "auto&"
            iter_str = self._emit_expr(stmt.iterable) if stmt.iterable else ""
            self.lines.append(f"{self._indent()}for ({v_type} {v_name} : {iter_str}) {{")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, TryCatchNode):
            self.lines.append(f"{self._indent()}try {{")
            self.indent_level += 1
            for s in stmt.try_block:
                self._emit_stmt(s)
            self.indent_level -= 1
            for cb in stmt.catch_blocks:
                param_str = f"{cb.param.type_name or 'const std::exception&'} {cb.param.name}" if cb.param else "..."
                self.lines.append(f"{self._indent()}}} catch ({param_str}) {{")
                self.indent_level += 1
                for s in cb.body:
                    self._emit_stmt(s)
                self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, ThrowNode):
            val_str = f" {self._emit_expr(stmt.expr)}" if stmt.expr else ""
            self.lines.append(f"{self._indent()}throw{val_str};")

        elif isinstance(stmt, SwitchNode):
            disc_str = self._emit_expr(stmt.discriminant) if stmt.discriminant else "0"
            self.lines.append(f"{self._indent()}switch ({disc_str}) {{")
            self.indent_level += 1
            for c in stmt.cases:
                self._emit_stmt(c)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, CaseNode):
            if stmt.value:
                self.lines.append(f"{self._indent()}case {self._emit_expr(stmt.value)}:")
            else:
                self.lines.append(f"{self._indent()}default:")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1

        elif isinstance(stmt, InputNode):
            self._emit_input(stmt)

        elif isinstance(stmt, VarDeclNode):
            if not hasattr(self, "declared_vars"):
                self.declared_vars = set()
            self.declared_vars.add(stmt.name)
            v_type = stmt.type_name if stmt.type_name and stmt.type_name != "auto" else "auto"
            if getattr(stmt, "is_array", False):
                size_str = self._emit_expr(stmt.array_size) if stmt.array_size else ""
                val_str = f" = {self._emit_expr(stmt.init_val)}" if stmt.init_val else ""
                self.lines.append(f"{self._indent()}{v_type} {stmt.name}[{size_str}]{val_str};")
            else:
                val_str = f" = {self._emit_expr(stmt.init_val)}" if stmt.init_val else ""
                self.lines.append(f"{self._indent()}{v_type} {stmt.name}{val_str};")

        elif isinstance(stmt, AssignNode):
            val_str = self._emit_expr(stmt.value) if stmt.value else "0"
            target_str = self._emit_expr(stmt.target_node) if getattr(stmt, "target_node", None) else stmt.target
            if self.indent_level == 0:
                self.lines.append(f"{self._indent()}/* alias: {target_str} {stmt.op} {val_str}; */")
            else:
                if not hasattr(self, "declared_vars"):
                    self.declared_vars = set()
                is_simple_id = (not getattr(stmt, "target_node", None)) or isinstance(stmt.target_node, IdentifierNode)
                if stmt.op == "=" and is_simple_id and stmt.target not in self.declared_vars:
                    self.declared_vars.add(stmt.target)
                    self.lines.append(f"{self._indent()}auto {target_str} = {val_str};")
                else:
                    self.lines.append(f"{self._indent()}{target_str} {stmt.op} {val_str};")

        elif isinstance(stmt, IfNode):
            test_str = self._emit_expr(stmt.test) if stmt.test else "true"
            self.lines.append(f"{self._indent()}if ({test_str}) {{")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            if stmt.orelse:
                self.lines.append(f"{self._indent()}}} else {{")
                self.indent_level += 1
                for s in stmt.orelse:
                    self._emit_stmt(s)
                self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, WhileNode):
            test_str = self._emit_expr(stmt.test) if stmt.test else "true"
            self.lines.append(f"{self._indent()}while ({test_str}) {{")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, ForNode):
            if not hasattr(self, "declared_vars"):
                self.declared_vars = set()
            init_str = "int i = 0"
            if isinstance(stmt.init, VarDeclNode):
                self.declared_vars.add(stmt.init.name)
                init_str = f"{stmt.init.type_name or 'auto'} {stmt.init.name} = {self._emit_expr(stmt.init.init_val)}"
            elif isinstance(stmt.init, AssignNode):
                if stmt.init.target not in self.declared_vars:
                    self.declared_vars.add(stmt.init.target)
                    init_str = f"auto {stmt.init.target} = {self._emit_expr(stmt.init.value)}"
                else:
                    init_str = f"{stmt.init.target} = {self._emit_expr(stmt.init.value)}"
            test_str = self._emit_expr(stmt.test) if stmt.test else "true"
            step_str = "i++"
            if isinstance(stmt.step, AssignNode):
                step_str = f"{stmt.step.target} {stmt.step.op} {self._emit_expr(stmt.step.value)}"
            elif isinstance(stmt.step, UnaryOpNode):
                step_str = self._emit_expr(stmt.step)
            self.lines.append(f"{self._indent()}for ({init_str}; {test_str}; {step_str}) {{")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, PrintNode) and getattr(stmt, "raw_printf", False) and stmt.format_str is not None:
            args_t = "".join(", " + self._emit_expr(a) for a in stmt.args)
            self.lines.append(f'{self._indent()}printf("{stmt.format_str}"{args_t});')

        elif isinstance(stmt, PrintNode):
            def _has_string_leaf(node):
                if isinstance(node, BinaryOpNode) and node.op == "+":
                    return _has_string_leaf(node.left) or _has_string_leaf(node.right)
                return isinstance(node, LiteralNode) and node.lit_type == "string"

            def flatten_add(node):
                # Only string concatenation ("a" + x) is split into << chains; arithmetic is kept intact.
                if isinstance(node, BinaryOpNode) and node.op == "+" and _has_string_leaf(node):
                    return flatten_add(node.left) + flatten_add(node.right)
                return [node]

            flat_args = []
            for a in stmt.args:
                flat_args.extend(flatten_add(a))

            out_chain = " << ".join(self._emit_expr(a) for a in flat_args)
            end_val = " << endl;" if stmt.end == "\n" else ";"
            self.lines.append(f"{self._indent()}cout << {out_chain}{end_val}")

        elif isinstance(stmt, ReturnNode):
            if stmt.value:
                self.lines.append(f"{self._indent()}return {self._emit_expr(stmt.value)};")
            else:
                self.lines.append(f"{self._indent()}return;")

        elif isinstance(stmt, ExprStmtNode):
            if stmt.expr:
                self.lines.append(f"{self._indent()}{self._emit_expr(stmt.expr)};")

        elif isinstance(stmt, BreakNode):
            self.lines.append(f"{self._indent()}break;")

        elif isinstance(stmt, ContinueNode):
            self.lines.append(f"{self._indent()}continue;")

        elif isinstance(stmt, UnsupportedASTNode):
            self.lines.append(f"{self._indent()}/* {stmt.text or stmt.details} */")

    def _emit_expr(self, expr: Optional[ASTNode]) -> str:
        if not expr:
            return "0"

        if isinstance(expr, LiteralNode):
            if expr.lit_type == "string":
                return f'"{expr.value}"'
            elif expr.lit_type == "boolean":
                return "true" if expr.value else "false"
            elif expr.lit_type == "null":
                return "nullptr"
            return str(expr.value)

        elif isinstance(expr, IdentifierNode):
            return expr.name

        elif isinstance(expr, BinaryOpNode):
            left_str = self._emit_expr(expr.left)
            right_str = self._emit_expr(expr.right)
            return f"({left_str} {expr.op} {right_str})"

        elif isinstance(expr, UnaryOpNode):
            opnd_str = self._emit_expr(expr.operand)
            if getattr(expr, "is_postfix", False):
                return f"{opnd_str}{expr.op}"
            return f"{expr.op}{opnd_str}"

        elif isinstance(expr, CallNode):
            args_str = ", ".join(self._emit_expr(a) for a in expr.args)
            return f"{expr.callee}({args_str})"

        elif isinstance(expr, ArrayAccessNode):
            return f"{self._emit_expr(expr.array)}[{self._emit_expr(expr.index)}]"

        elif isinstance(expr, ArrayLiteralNode):
            elems = ", ".join(self._emit_expr(e) for e in expr.elements)
            return f"{{{elems}}}"

        elif isinstance(expr, MemberAccessNode):
            return f"{self._emit_expr(expr.object)}.{expr.member}"

        elif isinstance(expr, ConditionalExprNode):
            return f"({self._emit_expr(expr.test)} ? {self._emit_expr(expr.true_expr)} : {self._emit_expr(expr.false_expr)})"

        elif isinstance(expr, CastExprNode):
            cast_name = f"{expr.cast_kind}_cast" if expr.cast_kind in ("static", "dynamic", "reinterpret", "const") else ""
            if cast_name:
                return f"{cast_name}<{expr.target_type}>({self._emit_expr(expr.expr)})"
            return f"(({expr.target_type})({self._emit_expr(expr.expr)}))"

        elif isinstance(expr, LambdaExprNode):
            caps = ", ".join(expr.captures) if expr.captures else "&"
            params = ", ".join(f"{p.type_name or 'auto'} {p.name}" for p in expr.params)
            return f"[{caps}]({params}) {{ /* lambda */ }}"

        elif isinstance(expr, UnsupportedASTNode):
            return f"/* {expr.text or expr.details} */"

        return "0"
