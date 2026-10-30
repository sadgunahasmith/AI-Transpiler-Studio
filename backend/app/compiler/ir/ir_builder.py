"""
IR Builder: Transforms normalized ASTNode into Language-Neutral IR and Three-Address Code.
Stage 4: Intermediate Representation
"""
from typing import List, Optional, Tuple
from ..parser.ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    ASTNode, ArrayAccessNode, MemberAccessNode, InputNode, StructDefNode, ClassDefNode,
    RangeForNode, TryCatchNode, CatchClauseNode, ThrowNode, LambdaExprNode, CastExprNode,
    NamespaceDefNode, EnumDefNode, TemplateDefNode, UsingDirectiveNode, TypeAliasNode,
    SwitchNode, CaseNode, ConditionalExprNode, UnsupportedASTNode, BreakNode, ContinueNode,
    ArrayLiteralNode
)
from .ir_nodes import (
    IRProgram, IRFunction, IRInstruction, IRAssign, IRBinaryOp, IRUnaryOp,
    IRJump, IRJumpIf, IRJumpIfNot, IRCall, IRPrint, IRReturn, IRLabel
)

class IRBuilder:
    """Translates normalized AST to language-neutral Three-Address Code IR."""

    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.current_instructions: List[IRInstruction] = []

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count - 1}"

    def new_label(self, prefix: str = "L") -> str:
        self.label_count += 1
        return f"{prefix}_{self.label_count}"

    def build_ir(self, ast_root: Optional[ProgramNode]) -> IRProgram:
        ir_prog = IRProgram()
        if not ast_root:
            return ir_prog

        global_stmts = []
        functions = []

        def collect_nodes(items, prefix=""):
            for stmt in items:
                if isinstance(stmt, FunctionDefNode):
                    functions.append(self._translate_function(stmt, prefix=prefix))
                elif isinstance(stmt, ClassDefNode):
                    c_prefix = f"{prefix}::{stmt.name}" if prefix else stmt.name
                    for m in stmt.methods:
                        if isinstance(m, FunctionDefNode):
                            functions.append(self._translate_function(m, prefix=c_prefix))
                    global_stmts.append(stmt)
                elif isinstance(stmt, NamespaceDefNode):
                    ns_prefix = f"{prefix}::{stmt.name}" if prefix else stmt.name
                    collect_nodes(stmt.body, prefix=ns_prefix)
                elif isinstance(stmt, TemplateDefNode):
                    if isinstance(stmt.declaration, FunctionDefNode):
                        functions.append(self._translate_function(stmt.declaration, prefix=prefix))
                    elif isinstance(stmt.declaration, ClassDefNode):
                        c_prefix = f"{prefix}::{stmt.declaration.name}" if prefix else stmt.declaration.name
                        for m in stmt.declaration.methods:
                            if isinstance(m, FunctionDefNode):
                                functions.append(self._translate_function(m, prefix=c_prefix))
                        global_stmts.append(stmt.declaration)
                else:
                    global_stmts.append(stmt)

        collect_nodes(ast_root.body)

        if global_stmts:
            self.current_instructions = []
            for s in global_stmts:
                self._translate_stmt(s)
            ir_prog.globals = list(self.current_instructions)

        ir_prog.functions = functions
        return ir_prog

    def _translate_function(self, fn_node: FunctionDefNode, prefix: str = "") -> IRFunction:
        self.current_instructions = []
        param_names = [p.name for p in fn_node.params]
        full_name = f"{prefix}::{fn_node.name}" if prefix else fn_node.name

        for stmt in fn_node.body:
            self._translate_stmt(stmt)

        return IRFunction(
            name=full_name,
            params=param_names,
            return_type=fn_node.return_type or "void",
            instructions=list(self.current_instructions)
        )

    def _translate_stmt(self, stmt: ASTNode):
        if isinstance(stmt, VarDeclNode):
            if stmt.init_val:
                src = self._translate_expr(stmt.init_val)
                self.current_instructions.append(IRAssign(target=stmt.name, source=src))
            else:
                self.current_instructions.append(IRAssign(target=stmt.name, source="0"))

        elif isinstance(stmt, AssignNode):
            src = self._translate_expr(stmt.value) if stmt.value else "0"
            if stmt.op == "=":
                self.current_instructions.append(IRAssign(target=stmt.target, source=src))
            else:
                bin_op = stmt.op.rstrip("=")
                tmp = self.new_temp()
                self.current_instructions.append(IRBinaryOp(target=tmp, left=stmt.target, op=bin_op, right=src))
                self.current_instructions.append(IRAssign(target=stmt.target, source=tmp))

        elif isinstance(stmt, IfNode):
            cond = self._translate_expr(stmt.test) if stmt.test else "1"
            else_lbl = self.new_label("L_else")
            end_lbl = self.new_label("L_endif")

            self.current_instructions.append(IRJumpIfNot(condition=cond, target_label=else_lbl))
            for s in stmt.body:
                self._translate_stmt(s)
            self.current_instructions.append(IRJump(target_label=end_lbl))

            self.current_instructions.append(IRLabel(name=else_lbl))
            if stmt.orelse:
                for s in stmt.orelse:
                    self._translate_stmt(s)

            self.current_instructions.append(IRLabel(name=end_lbl))

        elif isinstance(stmt, WhileNode):
            start_lbl = self.new_label("L_loop_start")
            end_lbl = self.new_label("L_loop_end")

            self.current_instructions.append(IRLabel(name=start_lbl))
            cond = self._translate_expr(stmt.test) if stmt.test else "1"
            self.current_instructions.append(IRJumpIfNot(condition=cond, target_label=end_lbl))

            for s in stmt.body:
                self._translate_stmt(s)

            self.current_instructions.append(IRJump(target_label=start_lbl))
            self.current_instructions.append(IRLabel(name=end_lbl))

        elif isinstance(stmt, ForNode):
            start_lbl = self.new_label("L_for_start")
            end_lbl = self.new_label("L_for_end")

            if stmt.init:
                self._translate_stmt(stmt.init)

            self.current_instructions.append(IRLabel(name=start_lbl))
            if stmt.test:
                cond = self._translate_expr(stmt.test)
                self.current_instructions.append(IRJumpIfNot(condition=cond, target_label=end_lbl))

            for s in stmt.body:
                self._translate_stmt(s)

            if stmt.step:
                self._translate_stmt(stmt.step)

            self.current_instructions.append(IRJump(target_label=start_lbl))
            self.current_instructions.append(IRLabel(name=end_lbl))

        elif isinstance(stmt, RangeForNode):
            iterable = self._translate_expr(stmt.iterable) if stmt.iterable else "[]"
            start_lbl = self.new_label("L_range_start")
            end_lbl = self.new_label("L_range_end")
            var_name = stmt.var.name if (stmt.var and hasattr(stmt.var, "name")) else "item"

            self.current_instructions.append(IRLabel(name=start_lbl))
            self.current_instructions.append(IRAssign(target=var_name, source=f"NEXT({iterable})"))
            for s in stmt.body:
                self._translate_stmt(s)
            self.current_instructions.append(IRJump(target_label=start_lbl))
            self.current_instructions.append(IRLabel(name=end_lbl))

        elif isinstance(stmt, TryCatchNode):
            try_lbl = self.new_label("L_try")
            end_try_lbl = self.new_label("L_end_try")
            self.current_instructions.append(IRLabel(name=try_lbl))
            for s in stmt.try_block:
                self._translate_stmt(s)
            self.current_instructions.append(IRJump(target_label=end_try_lbl))
            for c in stmt.catch_blocks:
                catch_lbl = self.new_label("L_catch")
                self.current_instructions.append(IRLabel(name=catch_lbl))
                if c.param:
                    self.current_instructions.append(IRAssign(target=c.param.name, source="EXCEPTION"))
                for s in c.body:
                    self._translate_stmt(s)
            self.current_instructions.append(IRLabel(name=end_try_lbl))

        elif isinstance(stmt, ThrowNode):
            val = self._translate_expr(stmt.expr) if stmt.expr else "0"
            self.current_instructions.append(IRCall(target=None, func_name="THROW", args=[val]))

        elif isinstance(stmt, SwitchNode):
            disc = self._translate_expr(stmt.discriminant) if stmt.discriminant else "0"
            end_switch = self.new_label("L_switch_end")
            for c in stmt.cases:
                c_lbl = self.new_label("L_case")
                if c.value:
                    val = self._translate_expr(c.value)
                    tmp_cond = self.new_temp()
                    self.current_instructions.append(IRBinaryOp(target=tmp_cond, left=disc, op="==", right=val))
                    self.current_instructions.append(IRJumpIf(condition=tmp_cond, target_label=c_lbl))
                else:
                    self.current_instructions.append(IRJump(target_label=c_lbl))
                self.current_instructions.append(IRLabel(name=c_lbl))
                for s in c.body:
                    self._translate_stmt(s)
            self.current_instructions.append(IRLabel(name=end_switch))

        elif isinstance(stmt, CaseNode):
            for s in stmt.body:
                self._translate_stmt(s)

        elif isinstance(stmt, BreakNode):
            self.current_instructions.append(IRJump(target_label="L_break"))

        elif isinstance(stmt, ContinueNode):
            self.current_instructions.append(IRJump(target_label="L_continue"))

        elif isinstance(stmt, PrintNode):
            arg_places = [self._translate_expr(a) for a in stmt.args]
            self.current_instructions.append(IRPrint(args=arg_places))

        elif isinstance(stmt, ReturnNode):
            ret_val = self._translate_expr(stmt.value) if stmt.value else None
            self.current_instructions.append(IRReturn(value=ret_val))

        elif isinstance(stmt, ExprStmtNode):
            self._translate_expr(stmt.expr)

        elif isinstance(stmt, InputNode):
            for target in stmt.targets:
                tgt_place = self._translate_expr(target)
                self.current_instructions.append(IRAssign(target=tgt_place, source="input()"))

        elif isinstance(stmt, (StructDefNode, ClassDefNode)):
            self.current_instructions.append(IRLabel(name=f"type_{stmt.name}"))

        elif isinstance(stmt, EnumDefNode):
            self.current_instructions.append(IRLabel(name=f"enum_{stmt.name}"))

        elif isinstance(stmt, TypeAliasNode):
            self.current_instructions.append(IRLabel(name=f"alias_{stmt.name}"))

        elif isinstance(stmt, (UsingDirectiveNode, UnsupportedASTNode)):
            raw = getattr(stmt, "raw_kind", "UNSUPPORTED")
            self.current_instructions.append(IRLabel(name=f"NOP_{raw}"))

    def _translate_expr(self, expr: Optional[ASTNode]) -> str:
        if not expr:
            return "0"

        if isinstance(expr, LiteralNode):
            if expr.lit_type == "string":
                return f'\"{expr.value}\"'
            return str(expr.value)

        elif isinstance(expr, IdentifierNode):
            return expr.name

        elif isinstance(expr, MemberAccessNode):
            obj = self._translate_expr(expr.object)
            return f"{obj}.{expr.member}"

        elif isinstance(expr, ArrayAccessNode):
            arr = self._translate_expr(expr.array)
            idx = self._translate_expr(expr.index)
            return f"{arr}[{idx}]"

        elif isinstance(expr, BinaryOpNode):
            left = self._translate_expr(expr.left)
            right = self._translate_expr(expr.right)
            tmp = self.new_temp()
            self.current_instructions.append(IRBinaryOp(target=tmp, left=left, op=expr.op, right=right))
            return tmp

        elif isinstance(expr, UnaryOpNode):
            opnd = self._translate_expr(expr.operand)
            tmp = self.new_temp()
            self.current_instructions.append(IRUnaryOp(target=tmp, op=expr.op, operand=opnd))
            return tmp

        elif isinstance(expr, CallNode):
            args_places = [self._translate_expr(a) for a in expr.args]
            tmp = self.new_temp()
            self.current_instructions.append(IRCall(target=tmp, func_name=expr.callee, args=args_places))
            return tmp

        elif isinstance(expr, ConditionalExprNode):
            cond = self._translate_expr(expr.test) if expr.test else "1"
            t_val = self._translate_expr(expr.true_expr) if expr.true_expr else "0"
            f_val = self._translate_expr(expr.false_expr) if expr.false_expr else "0"
            tmp = self.new_temp()
            self.current_instructions.append(IRAssign(target=tmp, source=f"{cond} ? {t_val} : {f_val}"))
            return tmp

        elif isinstance(expr, CastExprNode):
            inner = self._translate_expr(expr.expr) if expr.expr else "0"
            tmp = self.new_temp()
            self.current_instructions.append(IRAssign(target=tmp, source=f"({expr.target_type}){inner}"))
            return tmp

        elif isinstance(expr, ArrayLiteralNode):
            elems = [self._translate_expr(el) for el in expr.elements]
            tmp = self.new_temp()
            self.current_instructions.append(IRAssign(target=tmp, source=f"[{', '.join(elems)}]"))
            return tmp

        elif isinstance(expr, LambdaExprNode):
            tmp = self.new_temp()
            self.current_instructions.append(IRAssign(target=tmp, source="<lambda>"))
            return tmp

        return "0"
