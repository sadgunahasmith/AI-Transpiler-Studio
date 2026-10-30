"""
C Code Generator for Stage 6: Code Generation.
Generates clean, compilable C source code from normalized AST.
"""
import re
from typing import List, Optional, Dict
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

class CCodeGen:
    """Emits clean, compilable C source code from normalized AST."""

    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.indent_level = 0
        self.lines: List[str] = []
        self.declared_functions: Dict[str, int] = {}

    def _clean_type(self, t: Optional[str]) -> str:
        if not t or t == "auto":
            return "int"
        t = t.strip()
        t = re.sub(r'\bconst\s+', '', t)
        t = t.replace("&", "*")
        t = t.replace("std::string", "const char*").replace("string", "const char*")
        t = re.sub(r'std::vector\s*<[^>]+>', 'void*', t)
        t = re.sub(r'vector\s*<[^>]+>', 'void*', t)
        t = re.sub(r'std::map\s*<[^>]+>', 'void*', t)
        t = re.sub(r'map\s*<[^>]+>', 'void*', t)
        t = re.sub(r'std::pair\s*<[^>]+>', 'void*', t)
        t = re.sub(r'decltype\([^)]+\)', 'int', t)
        if t in ("unsigned int", "uint32_t"):
            return "unsigned int"
        if t in ("unsigned long", "uint64_t", "size_t"):
            return "size_t"
        if t in ("long long", "int64_t"):
            return "long long"
        if t in ("float", "double", "char", "bool", "void", "int", "short"):
            return t
        return t

    def _set_var_type(self, name: str, ctype: str, is_array: bool) -> None:
        if not hasattr(self, "var_types"):
            self.var_types = {}
        t = (ctype or "int").replace("const ", "").strip()
        if t in ("char*", "string") or (t == "char" and is_array):
            kind = "string"
        elif t in ("float", "double"):
            kind = "double"
        elif t == "char":
            kind = "char"
        elif t in ("long", "long long", "size_t"):
            kind = "long"
        else:
            kind = "int"
        self.var_types[name] = kind

    def _expr_ctype(self, e) -> str:
        """Very small static type inference: int | long | double | char | string."""
        vt = getattr(self, "var_types", {})
        if isinstance(e, LiteralNode):
            if e.lit_type == "string":
                return "string"
            if e.lit_type == "number":
                return "double" if isinstance(e.value, float) else "int"
            return "int"
        if isinstance(e, IdentifierNode):
            return vt.get(e.name, "int")
        if isinstance(e, ArrayAccessNode):
            base = vt.get(getattr(e.array, "name", ""), "int")
            return "char" if base == "string" else base
        if isinstance(e, BinaryOpNode):
            if e.op in ("<", ">", "<=", ">=", "==", "!=", "&&", "||"):
                return "int"
            l, r = self._expr_ctype(e.left), self._expr_ctype(e.right)
            if "string" in (l, r):
                return "string"
            if "double" in (l, r):
                return "double"
            if "long" in (l, r):
                return "long"
            return "int"
        if isinstance(e, UnaryOpNode):
            return self._expr_ctype(e.operand) if e.op != "!" else "int"
        if isinstance(e, ConditionalExprNode):
            return self._expr_ctype(e.true_expr)
        if isinstance(e, CastExprNode):
            t = str(getattr(e, "target_type", "int"))
            return "double" if t in ("float", "double") else ("char" if t == "char" else "int")
        return "int"

    _C_FMT = {"int": "%d", "long": "%ld", "float": "%f", "double": "%lf", "char": " %c", "string": "%255s"}
    _C_TYPE = {"int": "int", "long": "long", "float": "float", "double": "double", "char": "char"}

    def _declare_input_target(self, t, kind: str) -> None:
        """Declares an input target that does not exist yet (e.g. Python-origin variables)."""
        if not isinstance(t, IdentifierNode):
            return
        if not hasattr(self, "declared_vars"):
            self.declared_vars = set()
        if t.name in self.declared_vars or self.indent_level == 0:
            return
        self.declared_vars.add(t.name)
        self._set_var_type(t.name, "char*" if kind in ("string", "line") else self._C_TYPE.get(kind, "int"), False)
        if kind in ("string", "line"):
            self.lines.append(f"{self._indent()}char {t.name}[256];")
        else:
            self.lines.append(f"{self._indent()}{self._C_TYPE.get(kind, 'int')} {t.name};")

    def _emit_input(self, stmt) -> None:
        ind = self._indent()
        mode = getattr(stmt, "mode", "token") or "token"
        targets = list(stmt.targets)
        kinds = [kind_of(stmt, i) for i in range(len(targets))]
        for t, k in zip(targets, kinds):
            self._declare_input_target(t, k)
        names = [self._emit_expr(t) for t in targets]

        if mode == "line" and len(targets) == 1 and kinds[0] in ("string", "line", "char", "int", "long", "float", "double"):
            k, n, t = kinds[0], names[0], targets[0]
            if k in ("string", "line"):
                is_ptr = isinstance(t, IdentifierNode) and t.name not in getattr(self, "declared_vars", set())
                self.lines.append(f"{ind}if (fgets({n}, 256, stdin)) {n}[strcspn({n}, \"\\r\\n\")] = 0; else {n}[0] = 0;")
            else:
                conv = {"int": "atoi", "long": "atol", "float": "atof", "double": "atof", "char": "(char)*"}[k]
                if k == "char":
                    self.lines.append(f"{ind}{{ char _ln[256] = \"\"; if (fgets(_ln, sizeof(_ln), stdin)) {n} = _ln[0]; }}")
                else:
                    self.lines.append(f"{ind}{{ char _ln[256] = \"\"; if (fgets(_ln, sizeof(_ln), stdin)) {n} = {conv}(_ln); }}")
            return

        if mode == "line" and kinds and kinds[0].endswith("_list"):
            n, k = names[0], kinds[0]
            elem = {"int_list": "int", "float_list": "double"}.get(k, "int")
            self.lines.append(f"{ind}/* line-of-values input: reads up to 1024 values into {n} and the count into {n}_len */")
            self.lines.append(f"{ind}{elem} {n}[1024]; int {n}_len = 0;")
            fn = "strtol" if elem == "int" else "strtod"
            self.lines.append(f"{ind}{{ char _ln[8192] = \"\"; if (fgets(_ln, sizeof(_ln), stdin)) {{ char *_p = _ln, *_e; while ({n}_len < 1024) {{ {elem} _v = ({elem}){fn}(_p, &_e{', 10' if elem == 'int' else ''}); if (_e == _p) break; {n}[{n}_len++] = _v; _p = _e; }} }} }}")
            return

        fmt = " ".join(self._C_FMT.get(k, "%d") if k != "line" else "%255[^\\n]" for k in kinds)
        addrs = []
        for t, k, n in zip(targets, kinds, names):
            is_buf = k in ("string", "line")
            addrs.append(n if is_buf else f"&{n}")
        self.lines.append(f'{ind}scanf("{fmt}", {", ".join(addrs)});')
        if mode == "line_tokens":
            self.lines.append(f'{ind}scanf("%*[^\\n]"); scanf("%*c");')

    def generate(self, ast_root: Optional[ProgramNode]) -> str:
        if not ast_root or not ast_root.body:
            return '#include <stdio.h>\n#include <stdlib.h>\n#include <stdbool.h>\n\nint main(void) {\n    return 0;\n}\n'

        self.lines = [
            '#include <stdio.h>',
            '#include <stdlib.h>',
            '#include <string.h>',
            '#include <stdbool.h>',
            ''
        ]
        self.indent_level = 0
        self.string_inputs = string_input_names(ast_root)

        main_fn = None
        for s in ast_root.body:
            if isinstance(s, FunctionDefNode) and s.name == "main":
                main_fn = s
                break

        DEF_TYPES = (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, TemplateDefNode, EnumDefNode, UsingDirectiveNode, TypeAliasNode, VarDeclNode)
        for s in ast_root.body:
            if s is not main_fn and isinstance(s, DEF_TYPES):
                self._emit_stmt(s)
                if isinstance(s, (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, EnumDefNode)):
                    self.lines.append("")

        if main_fn:
            self._emit_function(main_fn)
        else:
            has_exec = any(not isinstance(s, DEF_TYPES) for s in ast_root.body)
            if has_exec:
                self.lines.append("int main(void) {")
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
        fn_name = fn.name
        if fn_name != "main":
            if fn_name in self.declared_functions:
                count = self.declared_functions[fn_name] + 1
                self.declared_functions[fn_name] = count
                fn_name = f"{fn_name}_{count}"
            else:
                self.declared_functions[fn_name] = 1

        has_val_ret = any(isinstance(s, ReturnNode) and s.value is not None for s in fn.body)
        if fn.name == "main":
            ret_type = "int"
        elif fn.return_type and fn.return_type != "auto":
            ret_type = self._clean_type(fn.return_type)
        elif has_val_ret:
            ret_type = "int"
        else:
            ret_type = "void"

        params = []
        if fn.name == "main":
            if fn.params and any(p.name in ("argc", "argv") for p in fn.params):
                for p in fn.params:
                    p_type = self._clean_type(p.type_name) if p.type_name and p.type_name != "auto" else "int"
                    params.append(f"{p_type} {p.name}")
                params_str = ", ".join(params)
            else:
                params_str = "void"
        else:
            for p in fn.params:
                p_type = self._clean_type(p.type_name) if p.type_name and p.type_name != "auto" else "int"
                params.append(f"{p_type} {p.name}")
            params_str = ", ".join(params) if params else "void"

        self.lines.append(f"{ret_type} {fn_name}({params_str}) {{")
        self.indent_level += 1
        prev_vars = getattr(self, "declared_vars", set()).copy()
        self.declared_vars = {p.name for p in fn.params}
        self.var_types = {}
        for p in fn.params:
            self._set_var_type(p.name, self._clean_type(p.type_name) if p.type_name and p.type_name != "auto" else "int", False)
        has_ret = False
        for s in fn.body:
            if isinstance(s, ReturnNode):
                has_ret = True
            self._emit_stmt(s)
        if fn.name == "main" and not has_ret:
            self.lines.append(f"{self._indent()}return 0;")
        self.declared_vars = prev_vars
        self.indent_level -= 1
        self.lines.append("}")
        self.lines.append("")

    def _emit_c_method(self, struct_name: str, fn: FunctionDefNode):
        if fn.name.startswith("~"):
            self.lines.append(f"{self._indent()}/* destructor: ~{struct_name} */")
            return
        if fn.name == struct_name:
            fn_name = f"{struct_name}_init"
            ret_type = "void"
        elif fn.name.startswith("operator"):
            fn_name = f"{struct_name}_op_eq"
            ret_type = "bool"
        else:
            fn_name = f"{struct_name}_{fn.name}"
            ret_type = self._clean_type(fn.return_type) if fn.return_type and fn.return_type != "auto" else "void"

        params = [f"{struct_name}* this"]
        for p in fn.params:
            p_type = self._clean_type(p.type_name) if p.type_name and p.type_name != "auto" else "int"
            params.append(f"{p_type} {p.name}")
        params_str = ", ".join(params)

        self.lines.append(f"{ret_type} {fn_name}({params_str}) {{")
        self.indent_level += 1
        for s in fn.body:
            self._emit_stmt(s)
        self.indent_level -= 1
        self.lines.append("}")
        self.lines.append("")

    def _emit_stmt(self, stmt: ASTNode):
        if isinstance(stmt, NamespaceDefNode):
            self.lines.append(f"{self._indent()}/* Namespace: {stmt.name} */")
            for item in stmt.body:
                self._emit_stmt(item)

        elif isinstance(stmt, TemplateDefNode):
            if stmt.declaration:
                self._emit_stmt(stmt.declaration)

        elif isinstance(stmt, EnumDefNode):
            self.lines.append(f"{self._indent()}typedef enum {stmt.name} {{")
            self.indent_level += 1
            for name, val in stmt.enumerators:
                val_str = f" = {self._emit_expr(val)}" if val else ""
                self.lines.append(f"{self._indent()}{name}{val_str},")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}} {stmt.name};")

        elif isinstance(stmt, TypeAliasNode):
            tgt = self._clean_type(stmt.target_type)
            self.lines.append(f"{self._indent()}typedef {tgt} {stmt.name};")

        elif isinstance(stmt, UsingDirectiveNode):
            pass

        elif isinstance(stmt, FunctionDefNode):
            self._emit_function(stmt)

        elif isinstance(stmt, (StructDefNode, ClassDefNode)):
            self.lines.append(f"{self._indent()}typedef struct {stmt.name} {{")
            self.indent_level += 1
            for f in stmt.fields:
                if isinstance(f, VarDeclNode):
                    f_type = self._clean_type(f.type_name)
                    if getattr(f, "is_array", False):
                        size_str = self._emit_expr(f.array_size) if f.array_size else ""
                        self.lines.append(f"{self._indent()}{f_type} {f.name}[{size_str}];")
                    else:
                        self.lines.append(f"{self._indent()}{f_type} {f.name};")
                else:
                    self._emit_stmt(f)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}} {stmt.name};")
            for m in stmt.methods:
                if isinstance(m, FunctionDefNode):
                    self._emit_c_method(stmt.name, m)
                else:
                    self._emit_stmt(m)
            if isinstance(stmt, ClassDefNode) and stmt.body:
                for b in stmt.body:
                    if b not in stmt.fields and b not in stmt.methods:
                        self._emit_stmt(b)

        elif isinstance(stmt, RangeForNode):
            iter_str = self._emit_expr(stmt.iterable) if stmt.iterable else "0"
            self.lines.append(f"{self._indent()}/* range-for over {iter_str} */ {{")
            self.indent_level += 1
            if stmt.var:
                self._emit_stmt(stmt.var)
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, TryCatchNode):
            self.lines.append(f"{self._indent()}/* try */ {{")
            self.indent_level += 1
            for s in stmt.try_block:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, ThrowNode):
            val_str = f"/* throw {self._emit_expr(stmt.expr)} */ " if stmt.expr else ""
            self.lines.append(f"{self._indent()}{val_str}exit(1);")

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
            v_type = self._clean_type(stmt.type_name) if stmt.type_name and stmt.type_name != "auto" else "int"
            self._set_var_type(stmt.name, v_type, getattr(stmt, "is_array", False))
            if (stmt.name in getattr(self, "string_inputs", set()) and not getattr(stmt, "is_array", False)
                    and v_type in ("const char*", "char*")):
                init = f" = {self._emit_expr(stmt.init_val)}" if stmt.init_val else ""
                self.lines.append(f"{self._indent()}char {stmt.name}[256]{init};")
                return
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
                    var_type = "int"
                    inferred = self._expr_ctype(stmt.value)
                    if inferred == "string":
                        var_type = "const char*"
                    elif inferred == "double":
                        var_type = "double"
                    elif inferred == "char":
                        var_type = "char"
                    self._set_var_type(stmt.target, var_type, False)
                    self.lines.append(f"{self._indent()}{var_type} {target_str} = {val_str};")
                else:
                    self.lines.append(f"{self._indent()}{target_str} {stmt.op} {val_str};")

        elif isinstance(stmt, IfNode):
            test_str = self._emit_expr(stmt.test) if stmt.test else "1"
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
            test_str = self._emit_expr(stmt.test) if stmt.test else "1"
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
                v_type = self._clean_type(stmt.init.type_name) if stmt.init.type_name and stmt.init.type_name != "auto" else "int"
                init_str = f"{v_type} {stmt.init.name} = {self._emit_expr(stmt.init.init_val)}"
            elif isinstance(stmt.init, AssignNode):
                if stmt.init.target not in self.declared_vars:
                    self.declared_vars.add(stmt.init.target)
                    init_str = f"int {stmt.init.target} = {self._emit_expr(stmt.init.value)}"
                else:
                    init_str = f"{stmt.init.target} = {self._emit_expr(stmt.init.value)}"
            test_str = self._emit_expr(stmt.test) if stmt.test else "1"
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
            def flatten_add(node):
                if isinstance(node, BinaryOpNode) and node.op == "+" and (
                        self._expr_ctype(node.left) == "string" or self._expr_ctype(node.right) == "string"):
                    return flatten_add(node.left) + flatten_add(node.right)
                return [node]

            flat_args = []
            for a in stmt.args:
                flat_args.extend(flatten_add(a))

            fmts, vals = [], []
            for a in flat_args:
                t = self._expr_ctype(a)
                if isinstance(a, LiteralNode) and a.lit_type == "string":
                    fmts.append(str(a.value).replace("%", "%%"))
                    continue
                fmts.append({"string": "%s", "double": "%g", "char": "%c", "long": "%ld"}.get(t, "%d"))
                vals.append(self._emit_expr(a))
            fmt = "".join(fmts) + ("\\n" if stmt.end == "\n" else "")
            if not vals:
                self.lines.append(f'{self._indent()}printf("{fmt}");')
            else:
                self.lines.append(f'{self._indent()}printf("{fmt}", {", ".join(vals)});')

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
                return "1" if expr.value else "0"
            elif expr.lit_type == "null":
                return "NULL"
            return str(expr.value)

        elif isinstance(expr, IdentifierNode):
            return expr.name

        elif isinstance(expr, ArrayLiteralNode):
            elements_str = ", ".join(self._emit_expr(e) for e in expr.elements)
            return f"{{{elements_str}}}"

        elif isinstance(expr, ArrayAccessNode):
            arr_str = self._emit_expr(expr.array)
            idx_str = self._emit_expr(expr.index)
            return f"{arr_str}[{idx_str}]"

        elif isinstance(expr, MemberAccessNode):
            obj_str = self._emit_expr(expr.object)
            op = "->" if obj_str in ("this", "self") or getattr(expr.object, "is_pointer", False) else "."
            return f"{obj_str}{op}{expr.member}"

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

        elif isinstance(expr, ConditionalExprNode):
            return f"({self._emit_expr(expr.test)} ? {self._emit_expr(expr.true_expr)} : {self._emit_expr(expr.false_expr)})"

        elif isinstance(expr, CastExprNode):
            return f"(({expr.target_type})({self._emit_expr(expr.expr)}))"

        elif isinstance(expr, UnsupportedASTNode):
            return f"/* {expr.text or expr.details} */"

        return "0"
