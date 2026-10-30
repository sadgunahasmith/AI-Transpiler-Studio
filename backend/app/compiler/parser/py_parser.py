"""
Python AST Parser and Syntax Error Detector for Stage 2: Syntax Analysis.
Converts Python code / AST into normalized ASTNode hierarchy.
"""
import ast
from typing import List, Tuple, Optional, Any
from .ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    SyntaxErrorRecord, ASTNode, ArrayLiteralNode, ArrayAccessNode,
    StructDefNode, MemberAccessNode, InputNode, ClassDefNode, BreakNode, ContinueNode
)


class PythonParser:
    """Parses Python source code into normalized AST nodes and captures syntax errors."""

    def __init__(self, code: str):
        self.code = code
        self.errors: List[SyntaxErrorRecord] = []

    def parse(self) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord]]:
        # First, attempt to parse using python's native AST engine
        try:
            py_tree = ast.parse(self.code)
            program = self._convert_program(py_tree)
            return program, self.errors
        except SyntaxError as e:
            fix = None
            if "expected ':'" in str(e).lower() or ":" in (e.text or ""):
                fix = "Add missing colon ':' at end of header line"
            elif "unmatched" in str(e).lower() or "was never closed" in str(e).lower():
                fix = "Close opening parenthesis, bracket, or quote"
            elif "indentation" in str(e).lower() or "unexpected indent" in str(e).lower():
                fix = "Fix indentation to 4 spaces"
            
            self.errors.append(SyntaxErrorRecord(
                line=e.lineno or 1,
                column=e.offset or 1,
                message=str(e.msg),
                token_value=e.text.strip() if e.text else None,
                severity="error",
                source="compiler",
                category="Syntax Error",
                suggested_fix=fix
            ))
            return None, self.errors
        except Exception as e:
            self.errors.append(SyntaxErrorRecord(
                line=1,
                column=1,
                message=f"Parse failure: {str(e)}",
                severity="error",
                source="compiler",
                category="Syntax Error"
            ))
            return None, self.errors

    # ------------------------------------------------------------------
    # Standard-input support: input(), int(input()), map(int, input().split()) ...
    # ------------------------------------------------------------------
    _TMP_COUNTER = 0

    def _convert_body(self, stmts) -> List[ASTNode]:
        out: List[ASTNode] = []
        for s in stmts:
            c = self._convert_stmt(s)
            if not c:
                continue
            if isinstance(c, list):
                out.extend(x for x in c if x)
            else:
                out.append(c)
        return out

    @staticmethod
    def _strip_str_calls(n):
        while (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr in ("strip", "rstrip", "lstrip") and not n.args):
            n = n.func.value
        return n

    def _input_call(self, n):
        """Returns (True, prompt) if `n` is input(...) / sys.stdin.readline() (optionally .strip()ed)."""
        n = self._strip_str_calls(n)
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name) and n.func.id == "input":
                prompt = None
                if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    prompt = n.args[0].value
                return True, prompt
            f = n.func
            if (isinstance(f, ast.Attribute) and f.attr == "readline" and isinstance(f.value, ast.Attribute)
                    and f.value.attr == "stdin"):
                return True, None
        return False, None

    def _split_of_input(self, n):
        """input().split() -> (True, prompt)"""
        n = self._strip_str_calls(n)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "split":
            return self._input_call(n.func.value)
        return False, None

    _CONV_KIND = {"int": "int", "float": "double", "str": "string"}

    def _match_input(self, n):
        """Classifies an expression that reads stdin.
        Returns (kind, prompt) with kind in int|double|string|int_list|float_list|string_list, or None."""
        ok, prompt = self._input_call(n)
        if ok:
            return "string", prompt
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            name = n.func.id
            if name in ("int", "float", "str") and len(n.args) == 1:
                ok, prompt = self._input_call(n.args[0])
                if ok:
                    return self._CONV_KIND[name], prompt
            if name in ("list", "tuple") and len(n.args) == 1:
                ok, prompt = self._split_of_input(n.args[0])
                if ok:
                    return "string_list", prompt
                inner = self._match_input(n.args[0])
                if inner and inner[0].endswith("_list"):
                    return inner
            if name == "map" and len(n.args) == 2 and isinstance(n.args[0], ast.Name):
                ok, prompt = self._split_of_input(n.args[1])
                if ok:
                    conv = n.args[0].id
                    return {"int": "int_list", "float": "float_list"}.get(conv, "string_list"), prompt
        ok, prompt = self._split_of_input(n)
        if ok:
            return "string_list", prompt
        if isinstance(n, ast.ListComp) and len(n.generators) == 1 and not n.generators[0].ifs:
            ok, prompt = self._split_of_input(n.generators[0].iter)
            if ok:
                elt = n.elt
                if isinstance(elt, ast.Call) and isinstance(elt.func, ast.Name) and elt.func.id in ("int", "float"):
                    return {"int": "int_list", "float": "float_list"}[elt.func.id], prompt
                return "string_list", prompt
        return None

    def _input_stmts(self, targets, kind, prompt, line):
        """Builds [PrintNode(prompt)?, InputNode] for reading `kind` into `targets`."""
        out: List[ASTNode] = []
        if prompt:
            out.append(PrintNode(args=[LiteralNode(value=prompt, lit_type="string", raw=repr(prompt), line=line)],
                                 end="", line=line))
        if len(targets) > 1:
            base = {"int_list": "int", "float_list": "double", "string_list": "string"}.get(kind, kind)
            out.append(InputNode(targets=targets, kinds=[base] * len(targets), mode="line_tokens", line=line))
        else:
            out.append(InputNode(targets=targets, kinds=[kind], mode="line", line=line))
        return out

    def _hoist_inputs(self, expr, line):
        """Replaces nested input expressions by temporaries. Returns (new_expr, [stmts to run first])."""
        pre: List[ASTNode] = []
        parser = self

        class _T(ast.NodeTransformer):
            def _try(self, node):
                m = parser._match_input(node)
                if not m:
                    return None
                kind, prompt = m
                PythonParser._TMP_COUNTER += 1
                name = f"_in{PythonParser._TMP_COUNTER}"
                pre.extend(parser._input_stmts([IdentifierNode(name=name, line=line)], kind, prompt, line))
                return ast.copy_location(ast.Name(id=name, ctx=ast.Load()), node)

            def visit_Call(self, node):
                r = self._try(node)
                return r if r is not None else self.generic_visit(node)

            def visit_ListComp(self, node):
                r = self._try(node)
                return r if r is not None else self.generic_visit(node)

        if expr is None:
            return None, pre
        new = _T().visit(expr)
        ast.fix_missing_locations(new)
        return new, pre

    def _convert_program(self, py_ast: ast.Module) -> ProgramNode:
        body: List[ASTNode] = []
        for stmt in py_ast.body:
            converted = self._convert_stmt(stmt)
            if converted:
                if isinstance(converted, list):
                    body.extend(converted)
                else:
                    body.append(converted)
        return ProgramNode(body=body, line=1, column=1)

    def _convert_stmt(self, stmt: ast.stmt) -> Optional[Any]:
        line = getattr(stmt, "lineno", 1)
        col = getattr(stmt, "col_offset", 1)

        if isinstance(stmt, ast.FunctionDef):
            params = [ParamNode(name=arg.arg, line=line, column=col) for arg in stmt.args.args]
            body = self._convert_body(stmt.body)
            return FunctionDefNode(name=stmt.name, return_type="auto", params=params, body=body, line=line, column=col)

        elif isinstance(stmt, ast.Assign):
            # --- stdin: x = int(input()), a, b = map(int, input().split()), ... ---
            m = self._match_input(stmt.value)
            if m and stmt.targets:
                kind, prompt = m
                tgt = stmt.targets[0]
                if isinstance(tgt, (ast.Tuple, ast.List)):
                    tnodes = [self._convert_expr(e) for e in tgt.elts]
                    return self._input_stmts(tnodes, kind, prompt, line)
                return self._input_stmts([self._convert_expr(tgt)], kind, prompt, line)
            new_val, pre = self._hoist_inputs(stmt.value, line)
            if pre:
                stmt = ast.Assign(targets=stmt.targets, value=new_val, lineno=line)
                rest = self._convert_stmt(stmt)
                return pre + (rest if isinstance(rest, list) else [rest])
            target_str = ""
            target_node = None
            if stmt.targets:
                target_node = self._convert_expr(stmt.targets[0])
                if isinstance(stmt.targets[0], ast.Name):
                    target_str = stmt.targets[0].id
                elif isinstance(stmt.targets[0], ast.Attribute):
                    obj_name = getattr(self._convert_expr(stmt.targets[0].value), "name", "obj")
                    target_str = f"{obj_name}.{stmt.targets[0].attr}"
                elif isinstance(stmt.targets[0], ast.Subscript):
                    target_str = "elem"
            val = self._convert_expr(stmt.value)
            return AssignNode(target=target_str, target_node=target_node, value=val, op="=", line=line, column=col)

        elif isinstance(stmt, ast.AugAssign):
            new_val, pre = self._hoist_inputs(stmt.value, line)
            if pre:
                stmt = ast.AugAssign(target=stmt.target, op=stmt.op, value=new_val, lineno=line)
                rest = self._convert_stmt(stmt)
                return pre + [rest]
            target_str = stmt.target.id if isinstance(stmt.target, ast.Name) else "var"
            target_node = self._convert_expr(stmt.target)
            val = self._convert_expr(stmt.value)
            op_map = {ast.Add: "+=", ast.Sub: "-=", ast.Mult: "*=", ast.Div: "/=", ast.Mod: "%="}
            op_sym = op_map.get(type(stmt.op), "=")
            return AssignNode(target=target_str, target_node=target_node, value=val, op=op_sym, line=line, column=col)

        elif isinstance(stmt, ast.If):
            # If Python entry guard: if __name__ == "__main__": ...
            if (isinstance(stmt.test, ast.Compare) and
                isinstance(stmt.test.left, ast.Name) and stmt.test.left.id == "__name__"):
                # Python entry idiom: skip because target generators emit target-idiomatic entry calls
                return None
            new_test, pre = self._hoist_inputs(stmt.test, line)
            test = self._convert_expr(new_test)
            body = self._convert_body(stmt.body)
            orelse = self._convert_body(stmt.orelse)
            if pre:
                return pre + [IfNode(test=test, body=body, orelse=orelse, line=line, column=col)]
            return IfNode(test=test, body=body, orelse=orelse, line=line, column=col)

        elif isinstance(stmt, ast.While):
            test = self._convert_expr(stmt.test)
            body = self._convert_body(stmt.body)
            return WhileNode(test=test, body=body, line=line, column=col)

        elif isinstance(stmt, ast.For):
            new_iter, pre = self._hoist_inputs(stmt.iter, line)
            if pre:
                stmt = ast.For(target=stmt.target, iter=new_iter, body=stmt.body, orelse=stmt.orelse, lineno=line)
                rest = self._convert_stmt(stmt)
                return pre + ([rest] if rest and not isinstance(rest, list) else (rest or []))
            # Target loop var
            target_var = stmt.target.id if isinstance(stmt.target, ast.Name) else "i"
            # Iter
            body = self._convert_body(stmt.body)
            # If iter is range(...)
            if isinstance(stmt.iter, ast.Call) and isinstance(stmt.iter.func, ast.Name) and stmt.iter.func.id == "range":
                range_args = [self._convert_expr(a) for a in stmt.iter.args]
                if len(range_args) == 1:
                    init = AssignNode(target=target_var, value=LiteralNode(value=0, lit_type="number", raw="0", line=line), line=line)
                    test = BinaryOpNode(left=IdentifierNode(name=target_var, line=line), op="<", right=range_args[0], line=line)
                    step = AssignNode(target=target_var, value=LiteralNode(value=1, lit_type="number", raw="1", line=line), op="+=", line=line)
                elif len(range_args) >= 2:
                    init = AssignNode(target=target_var, value=range_args[0], line=line)
                    test = BinaryOpNode(left=IdentifierNode(name=target_var, line=line), op="<", right=range_args[1], line=line)
                    step_val = range_args[2] if len(range_args) > 2 else LiteralNode(value=1, lit_type="number", raw="1", line=line)
                    step = AssignNode(target=target_var, value=step_val, op="+=", line=line)
                return ForNode(init=init, test=test, step=step, body=body, line=line, column=col)
            else:
                # for item in collection -> lowered to indexed loop:
                iter_expr = self._convert_expr(stmt.iter)
                idx_var = f"_i_{target_var}"
                init = AssignNode(target=idx_var, value=LiteralNode(value=0, lit_type="number", raw="0", line=line), line=line)
                test = BinaryOpNode(left=IdentifierNode(name=idx_var, line=line), op="<", right=CallNode(callee="len", args=[iter_expr], line=line), line=line)
                step = AssignNode(target=idx_var, value=LiteralNode(value=1, lit_type="number", raw="1", line=line), op="+=", line=line)
                item_bind = AssignNode(target=target_var, value=ArrayAccessNode(array=iter_expr, index=IdentifierNode(name=idx_var, line=line), line=line), op="=", line=line)
                full_body = [item_bind] + body
                return ForNode(init=init, test=test, step=step, body=full_body, line=line, column=col)

        elif isinstance(stmt, ast.Return):
            new_val, pre = self._hoist_inputs(stmt.value, line)
            if pre:
                return pre + [ReturnNode(value=self._convert_expr(new_val), line=line, column=col)]
            val = self._convert_expr(stmt.value) if stmt.value else None
            return ReturnNode(value=val, line=line, column=col)

        elif isinstance(stmt, ast.Expr):
            m = self._match_input(stmt.value)
            if m:  # bare input(): read and discard
                kind, prompt = m
                return self._input_stmts([IdentifierNode(name="_discard", line=line)], "string" if kind.endswith("_list") else kind, prompt, line)
            new_val, pre = self._hoist_inputs(stmt.value, line)
            if pre:
                rest = self._convert_stmt(ast.Expr(value=new_val, lineno=line))
                return pre + ([rest] if rest and not isinstance(rest, list) else (rest or []))
            # Check if print(...)
            if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "print":
                args = [self._convert_expr(a) for a in stmt.value.args]
                end_str = "\n"
                sep_str = " "
                for kw in stmt.value.keywords:
                    if kw.arg == "end" and isinstance(kw.value, ast.Constant):
                        end_str = kw.value.value
                    elif kw.arg == "sep" and isinstance(kw.value, ast.Constant):
                        sep_str = kw.value.value
                # PrintNode arguments are concatenated, so make Python's separator explicit
                if len(args) > 1 and sep_str != "":
                    spaced = []
                    for i, a in enumerate(args):
                        if i:
                            spaced.append(LiteralNode(value=sep_str, lit_type="string", raw=repr(sep_str), line=line))
                        spaced.append(a)
                    args = spaced
                return PrintNode(args=args, end=end_str, line=line, column=col)
            else:
                expr = self._convert_expr(stmt.value)
                return ExprStmtNode(expr=expr, line=line, column=col)

        elif isinstance(stmt, ast.ClassDef):
            fields = []
            methods = []
            for b in stmt.body:
                cb = self._convert_stmt(b)
                if isinstance(cb, FunctionDefNode):
                    methods.append(cb)
                elif isinstance(cb, AssignNode):
                    fields.append(VarDeclNode(name=cb.target, type_name="auto", init_val=cb.value, line=cb.line, column=cb.column))
            return ClassDefNode(name=stmt.name, fields=fields, methods=methods, line=line, column=col)

        elif isinstance(stmt, ast.Break):
            return BreakNode(line=line, column=col)

        elif isinstance(stmt, ast.Continue):
            return ContinueNode(line=line, column=col)

        return None

    def _convert_expr(self, expr: Optional[ast.expr]) -> Optional[ASTNode]:
        if expr is None:
            return None
        line = getattr(expr, "lineno", 1)
        col = getattr(expr, "col_offset", 1)

        if isinstance(expr, ast.Constant):
            val = expr.value
            lit_type = "string" if isinstance(val, str) else ("boolean" if isinstance(val, bool) else ("null" if val is None else "number"))
            return LiteralNode(value=val, lit_type=lit_type, raw=str(val), line=line, column=col)

        elif isinstance(expr, ast.Name):
            return IdentifierNode(name=expr.id, line=line, column=col)

        elif isinstance(expr, ast.Attribute):
            obj = self._convert_expr(expr.value)
            return MemberAccessNode(object=obj, member=expr.attr, line=line, column=col)

        elif isinstance(expr, ast.BinOp):
            left = self._convert_expr(expr.left)
            right = self._convert_expr(expr.right)
            op_map = {
                ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
                ast.Mod: "%", ast.FloorDiv: "//", ast.Pow: "**"
            }
            op_sym = op_map.get(type(expr.op), "+")
            return BinaryOpNode(left=left, op=op_sym, right=right, line=line, column=col)

        elif isinstance(expr, ast.Compare):
            left = self._convert_expr(expr.left)
            cmp_map = {
                ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
                ast.Gt: ">", ast.GtE: ">=", ast.Is: "==", ast.IsNot: "!="
            }
            op_sym = cmp_map.get(type(expr.ops[0]), "==")
            right = self._convert_expr(expr.comparators[0])
            return BinaryOpNode(left=left, op=op_sym, right=right, line=line, column=col)

        elif isinstance(expr, ast.BoolOp):
            op_sym = "&&" if isinstance(expr.op, ast.And) else "||"
            res = self._convert_expr(expr.values[0])
            for next_v in expr.values[1:]:
                res = BinaryOpNode(left=res, op=op_sym, right=self._convert_expr(next_v), line=line, column=col)
            return res

        elif isinstance(expr, ast.UnaryOp):
            op_sym = "!" if isinstance(expr.op, ast.Not) else ("-" if isinstance(expr.op, ast.USub) else "+")
            return UnaryOpNode(op=op_sym, operand=self._convert_expr(expr.operand), line=line, column=col)

        elif isinstance(expr, ast.List):
            elements = [self._convert_expr(e) for e in expr.elts]
            return ArrayLiteralNode(elements=elements, line=line, column=col)

        elif isinstance(expr, ast.Subscript):
            target_arr = self._convert_expr(expr.value)
            idx_expr = self._convert_expr(expr.slice)
            return ArrayAccessNode(array=target_arr, index=idx_expr, line=line, column=col)

        elif isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                callee_name = expr.func.id
            elif isinstance(expr.func, ast.Attribute):
                obj_node = self._convert_expr(expr.func.value)
                obj_name = obj_node.name if isinstance(obj_node, IdentifierNode) else "obj"
                callee_name = f"{obj_name}.{expr.func.attr}"
            else:
                callee_name = "func"
            args = [self._convert_expr(a) for a in expr.args]
            return CallNode(callee=callee_name, args=args, line=line, column=col)

        return LiteralNode(value=0, lit_type="number", raw="0", line=line, column=col)
