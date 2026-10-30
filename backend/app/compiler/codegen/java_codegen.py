"""
Java Code Generator for Stage 6: Code Generation.
Generates clean, compilable Java source code from normalized AST.
"""
import re
from typing import List, Optional
from .input_utils import string_input_names, kind_of, sanitize_printf_format, has_input as _ast_has_input
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

class JavaCodeGen:
    """Emits clean, compilable Java source code from normalized AST."""

    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.indent_level = 0
        self.lines: List[str] = []
        self.current_class: Optional[str] = None

    def _clean_type(self, t: Optional[str]) -> str:
        if not t or t == "auto":
            return "var"
        t = t.strip()
        t = re.sub(r'\bconst\s+', '', t)
        t = re.sub(r'[\&\*]', '', t).strip()
        t = t.replace("std::string", "String").replace("string", "String")
        t = t.replace("bool", "boolean")
        t = re.sub(r'std::vector\s*<([^>]+)>', r'List<\1>', t)
        t = re.sub(r'vector\s*<([^>]+)>', r'List<\1>', t)
        t = re.sub(r'std::map\s*<([^,]+),\s*([^>]+)>', r'Map<\1, \2>', t)
        t = re.sub(r'map\s*<([^,]+),\s*([^>]+)>', r'Map<\1, \2>', t)
        t = re.sub(r'std::pair\s*<([^,]+),\s*([^>]+)>', r'Map.Entry<\1, \2>', t)
        t = re.sub(r'decltype\([^)]+\)', 'int', t)
        t = t.replace("std::runtime_error", "RuntimeException").replace("runtime_error", "RuntimeException")
        t = t.replace("std::invalid_argument", "IllegalArgumentException").replace("invalid_argument", "IllegalArgumentException")
        t = t.replace("std::out_of_range", "IndexOutOfBoundsException").replace("out_of_range", "IndexOutOfBoundsException")
        t = t.replace("std::exception", "Exception")
        if t in ("unsigned int", "unsigned long", "size_t", "uint64_t", "int64_t"):
            return "long"
        if t in ("uint32_t", "int32_t", "short", "unsigned short", "int8_t", "uint8_t"):
            return "int"
        if t in ("float", "double", "char", "boolean", "void", "String"):
            return t
        return t

    _JAVA_TYPE = {"int": "int", "long": "long", "float": "float", "double": "double", "char": "char",
                  "string": "String", "line": "String", "int_list": "int[]", "float_list": "double[]",
                  "string_list": "String[]"}

    def _java_read_expr(self, kind: str, mode: str) -> str:
        if mode in ("line", "line_tokens"):
            line = "scanner.nextLine()"
            return {
                "int": f"Integer.parseInt({line}.trim())",
                "long": f"Long.parseLong({line}.trim())",
                "float": f"Float.parseFloat({line}.trim())",
                "double": f"Double.parseDouble({line}.trim())",
                "char": f"{line}.charAt(0)",
                "int_list": f'Arrays.stream({line}.trim().split("\\\\s+")).mapToInt(Integer::parseInt).toArray()',
                "float_list": f'Arrays.stream({line}.trim().split("\\\\s+")).mapToDouble(Double::parseDouble).toArray()',
                "string_list": f'{line}.trim().split("\\\\s+")',
            }.get(kind, line)
        return {
            "int": "scanner.nextInt()", "long": "scanner.nextLong()", "float": "scanner.nextFloat()",
            "double": "scanner.nextDouble()", "char": "scanner.next().charAt(0)",
            "string": "scanner.next()", "line": "scanner.nextLine()",
        }.get(kind, "scanner.nextInt()")

    def _print_piece(self, a) -> str:
        """String-concatenation operand: a leading "" keeps `+` as string concatenation."""
        e = self._emit_expr(a)
        if isinstance(a, LiteralNode) and a.lit_type == "string":
            return e
        return f"({e})"

    def _emit_input(self, stmt) -> None:
        ind = self._indent()
        mode = getattr(stmt, "mode", "token") or "token"
        if not hasattr(self, "declared_vars"):
            self.declared_vars = set()
        for i, t in enumerate(stmt.targets):
            kind = kind_of(stmt, i)
            read = self._java_read_expr(kind, "line" if mode == "line_tokens" and len(stmt.targets) == 1 else mode)
            if mode == "line_tokens" and len(stmt.targets) > 1:
                if i == 0:
                    self.lines.append(f"{ind}String[] _vals = scanner.nextLine().trim().split(\"\\\\s+\");")
                    self.declared_vars.discard("_vals")
                conv = {"int": "Integer.parseInt(_vals[%d])", "long": "Long.parseLong(_vals[%d])",
                        "float": "Float.parseFloat(_vals[%d])", "double": "Double.parseDouble(_vals[%d])",
                        "char": "_vals[%d].charAt(0)"}.get(kind, "_vals[%d]") % i
                read = conv
            is_simple = isinstance(t, IdentifierNode)
            if is_simple and t.name not in self.declared_vars and self.indent_level > 1:
                self.declared_vars.add(t.name)
                self.lines.append(f"{ind}{self._JAVA_TYPE.get(kind, 'int')} {self._emit_expr(t)} = {read};")
            else:
                self.lines.append(f"{ind}{self._emit_expr(t)} = {read};")
        if mode == "token" and False:
            pass
        if mode == "line_tokens" and len(stmt.targets) > 1:
            pass

    def generate(self, ast_root: Optional[ProgramNode]) -> str:
        if not ast_root or not ast_root.body:
            return 'public class Main {\n    public static void main(String[] args) {\n    }\n}\n'

        self.lines = [
            "import java.util.*;",
            "import java.io.*;",
            "",
            "public class Main {"
        ]
        self.indent_level = 1
        self.declared_vars = set()
        self.string_inputs = string_input_names(ast_root)
        if _ast_has_input(ast_root):
            self.lines.append(f"{self._indent()}static Scanner scanner = new Scanner(System.in).useLocale(Locale.US);")
            self.lines.append("")

        main_fn = None
        for s in ast_root.body:
            if isinstance(s, FunctionDefNode) and s.name == "main":
                main_fn = s
                break

        for s in ast_root.body:
            if s is not main_fn:
                if main_fn is not None and isinstance(s, ExprStmtNode) and isinstance(s.expr, CallNode) and s.expr.callee == "main":
                    continue
                self._emit_stmt(s)
                if isinstance(s, (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, EnumDefNode)):
                    self.lines.append("")

        if main_fn:
            self._emit_main_function(main_fn)
        else:
            has_exec = any(not isinstance(s, (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, TemplateDefNode, EnumDefNode, UsingDirectiveNode, TypeAliasNode, VarDeclNode)) for s in ast_root.body)
            if has_exec:
                self.lines.append(f"{self._indent()}public static void main(String[] args) {{")
                self.indent_level += 1
                for s in ast_root.body:
                    if not isinstance(s, (StructDefNode, ClassDefNode, FunctionDefNode, NamespaceDefNode, TemplateDefNode, EnumDefNode, UsingDirectiveNode, TypeAliasNode)):
                        self._emit_stmt(s)
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")

        self.lines.append("}")
        return "\n".join(self.lines).strip() + "\n"

    def _indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)

    def _emit_main_function(self, fn: FunctionDefNode, has_input: bool = False):
        self.lines.append(f"{self._indent()}public static void main(String[] args) {{")
        self.indent_level += 1
        self.declared_vars = {"args"}
        if has_input:
            self.lines.append(f"{self._indent()}Scanner scanner = new Scanner(System.in);")
        for s in fn.body:
            if isinstance(s, ReturnNode):
                continue  # skip return 0 in java void main
            self._emit_stmt(s)
        self.indent_level -= 1
        self.lines.append(f"{self._indent()}}}")
        self.lines.append("")

    def _emit_function(self, fn: FunctionDefNode, is_method: bool = False):
        if fn.name.startswith("~"):
            self.lines.append(f"{self._indent()}/* destructor: ~{self.current_class or ''} */")
            return

        if self.current_class and fn.name == self.current_class:
            params = []
            for p in fn.params:
                p_type = self._clean_type(p.type_name)
                params.append(f"{p_type} {p.name}")
            params_str = ", ".join(params)
            self.lines.append(f"{self._indent()}public {fn.name}({params_str}) {{")
            self.indent_level += 1
            for s in fn.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")
            self.lines.append("")
            return

        if fn.name.startswith("operator"):
            op_name = fn.name.replace("operator", "op_")
            if fn.name == "operator==":
                op_name = "op_equals"
            elif fn.name == "operator!=":
                op_name = "op_notEquals"
            elif fn.name == "operator<":
                op_name = "op_lessThan"
            fn_name = op_name
        else:
            fn_name = fn.name

        ret_type = self._clean_type(fn.return_type) if fn.return_type and fn.return_type != "auto" else "void"
        params = []
        for p in fn.params:
            p_type = self._clean_type(p.type_name)
            params.append(f"{p_type} {p.name}")
        params_str = ", ".join(params) if params else ""

        modifiers = "public"
        if not is_method or getattr(fn, "is_static", False):
            modifiers += " static"

        self.lines.append(f"{self._indent()}{modifiers} {ret_type} {fn_name}({params_str}) {{")
        self.indent_level += 1
        for s in fn.body:
            self._emit_stmt(s)
        self.indent_level -= 1
        self.lines.append(f"{self._indent()}}}")
        self.lines.append("")

    def _emit_stmt(self, stmt: ASTNode):
        if isinstance(stmt, NamespaceDefNode):
            self.lines.append(f"{self._indent()}public static class {stmt.name} {{")
            self.indent_level += 1
            for item in stmt.body:
                self._emit_stmt(item)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, TemplateDefNode):
            if stmt.declaration:
                self._emit_stmt(stmt.declaration)

        elif isinstance(stmt, EnumDefNode):
            self.lines.append(f"{self._indent()}public enum {stmt.name} {{")
            self.indent_level += 1
            enum_consts = ", ".join(name for name, _ in stmt.enumerators)
            self.lines.append(f"{self._indent()}{enum_consts};")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, UsingDirectiveNode):
            pass

        elif isinstance(stmt, TypeAliasNode):
            pass

        elif isinstance(stmt, FunctionDefNode):
            self._emit_function(stmt)

        elif isinstance(stmt, (StructDefNode, ClassDefNode)):
            old_class = self.current_class
            self.current_class = stmt.name
            extends_str = ""
            if stmt.base_classes:
                base_name = self._clean_type(stmt.base_classes[0][0])
                extends_str = " extends " + base_name
            self.lines.append(f"{self._indent()}public static class {stmt.name}{extends_str} {{")
            self.indent_level += 1
            for f in stmt.fields:
                f_type = self._clean_type(f.type_name)
                if getattr(f, "is_array", False):
                    self.lines.append(f"{self._indent()}public {f_type}[] {f.name};")
                else:
                    self.lines.append(f"{self._indent()}public {f_type} {f.name};")
            for m in stmt.methods:
                if isinstance(m, FunctionDefNode):
                    self._emit_function(m, is_method=True)
                else:
                    self._emit_stmt(m)
            if isinstance(stmt, ClassDefNode) and stmt.body:
                for b in stmt.body:
                    if b not in stmt.fields and b not in stmt.methods:
                        self._emit_stmt(b)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")
            self.current_class = old_class

        elif isinstance(stmt, RangeForNode):
            v_name = stmt.var.name if stmt.var else "item"
            v_type = self._clean_type(stmt.var.type_name) if (stmt.var and stmt.var.type_name and stmt.var.type_name != "auto") else "var"
            iter_str = self._emit_expr(stmt.iterable) if stmt.iterable else "new ArrayList<>()"
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
                param_str = f"{cb.param.type_name or 'Exception'} {cb.param.name}" if cb.param else "Exception e"
                self.lines.append(f"{self._indent()}}} catch ({param_str}) {{")
                self.indent_level += 1
                for s in cb.body:
                    self._emit_stmt(s)
                self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, ThrowNode):
            val_str = f" {self._emit_expr(stmt.expr)}" if stmt.expr else " new RuntimeException()"
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
            if stmt.name in getattr(self, "string_inputs", set()) and (getattr(stmt, "is_array", False) or self._clean_type(stmt.type_name) == "String"):
                init = f" = {self._emit_expr(stmt.init_val)}" if stmt.init_val and not getattr(stmt, "is_array", False) else ' = ""'
                self.lines.append(f"{self._indent()}String {stmt.name}{init};")
                return
            v_type = self._clean_type(stmt.type_name)
            is_const = getattr(stmt, "is_const", False) or getattr(stmt, "is_constexpr", False)
            const_pfx = "final " if is_const else ""
            pub_static = "public static " if self.indent_level == 1 else ""
            if getattr(stmt, "is_array", False):
                val_str = f" = {self._emit_expr(stmt.init_val)}" if stmt.init_val else ""
                self.lines.append(f"{self._indent()}{pub_static}{const_pfx}{v_type}[] {stmt.name}{val_str};")
            else:
                val_str = f" = {self._emit_expr(stmt.init_val)}" if stmt.init_val else ""
                self.lines.append(f"{self._indent()}{pub_static}{const_pfx}{v_type} {stmt.name}{val_str};")

        elif isinstance(stmt, AssignNode):
            val_str = self._emit_expr(stmt.value) if stmt.value else "0"
            target_str = self._emit_expr(stmt.target_node) if getattr(stmt, "target_node", None) else stmt.target
            if self.indent_level == 1:
                self.lines.append(f"{self._indent()}/* alias: {target_str} {stmt.op} {val_str}; */")
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
            init_str = "int i = 0"
            if isinstance(stmt.init, VarDeclNode):
                init_str = f"{self._clean_type(stmt.init.type_name)} {stmt.init.name} = {self._emit_expr(stmt.init.init_val)}"
            elif isinstance(stmt.init, AssignNode):
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
            fmt = sanitize_printf_format(stmt.format_str, "java")
            args_t = "".join(", " + self._emit_expr(a) for a in stmt.args)
            self.lines.append(f'{self._indent()}System.out.printf(Locale.US, "{fmt}"{args_t});')

        elif isinstance(stmt, PrintNode):
            args_str = " + ".join(self._print_piece(a) for a in stmt.args) if stmt.args else '""'
            if len(stmt.args) > 1 and not (isinstance(stmt.args[0], LiteralNode) and stmt.args[0].lit_type == "string"):
                args_str = '"" + ' + args_str
            if stmt.end == "":
                self.lines.append(f"{self._indent()}System.out.print({args_str});")
            else:
                self.lines.append(f"{self._indent()}System.out.println({args_str});")

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
                return "null"
            return str(expr.value)

        elif isinstance(expr, IdentifierNode):
            name = expr.name
            if name == "nullptr":
                return "null"
            if name == "PI" or name == "M_PI":
                return "Math.PI"
            if name.startswith("std.") or name.startswith("std::"):
                return name.replace("std::", "").replace("std.", "")
            return name

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
            callee = expr.callee.replace("std::", "").replace("std.", "")
            if callee == "move" and expr.args:
                return self._emit_expr(expr.args[0])
            if callee == "to_string" and expr.args:
                return f"String.valueOf({self._emit_expr(expr.args[0])})"
            args_str = ", ".join(self._emit_expr(a) for a in expr.args)
            return f"{callee}({args_str})"

        elif isinstance(expr, ArrayAccessNode):
            return f"{self._emit_expr(expr.array)}[{self._emit_expr(expr.index)}]"

        elif isinstance(expr, MemberAccessNode):
            return f"{self._emit_expr(expr.object)}.{expr.member}"

        elif isinstance(expr, ArrayLiteralNode):
            elems = ", ".join(self._emit_expr(e) for e in expr.elements)
            return f"new Object[]{{{elems}}}"

        elif isinstance(expr, ConditionalExprNode):
            return f"({self._emit_expr(expr.test)} ? {self._emit_expr(expr.true_expr)} : {self._emit_expr(expr.false_expr)})"

        elif isinstance(expr, CastExprNode):
            target = self._clean_type(expr.target_type)
            return f"(({target})({self._emit_expr(expr.expr)}))"

        elif isinstance(expr, UnsupportedASTNode):
            return f"/* {expr.text or expr.details} */"

        return "0"
