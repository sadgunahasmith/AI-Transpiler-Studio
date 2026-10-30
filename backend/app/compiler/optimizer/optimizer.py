"""
Optimization passes for Stage 5: Optimization.
Implements Constant Folding, Constant Propagation, Dead Code Elimination, and Expression Simplification.
"""
import copy
from typing import Tuple, Dict, Any, List, Optional
from ..parser.ast_nodes import (
    ProgramNode, FunctionDefNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    ASTNode
)
from ..ir.ir_nodes import (
    IRProgram, IRFunction, IRInstruction, IRAssign, IRBinaryOp, IRUnaryOp,
    IRReturn, IRPrint, IRLabel, IRJump, IRJumpIf, IRJumpIfNot
)

class ASTOptimizer:
    """Performs semantics-preserving optimizations directly on AST."""

    def __init__(self):
        self.stats = {
            "constants_folded": 0,
            "constants_propagated": 0,
            "expressions_simplified": 0,
            "dead_code_eliminated": 0,
            "details": []
        }
        self.const_env: Dict[str, Any] = {}

    def _find_mutated_vars(self, stmts: List[ASTNode]) -> set:
        mutated = set()
        for s in stmts:
            if not s:
                continue
            if isinstance(s, AssignNode):
                mutated.add(s.target.split('[')[0].split('.')[0])
            elif isinstance(s, VarDeclNode):
                mutated.add(s.name)
            elif isinstance(s, ExprStmtNode) and isinstance(s.expr, UnaryOpNode):
                if isinstance(s.expr.operand, IdentifierNode):
                    mutated.add(s.expr.operand.name)
            elif isinstance(s, PrintNode):
                for a in getattr(s, "args", []):
                    if isinstance(a, UnaryOpNode) and isinstance(a.operand, IdentifierNode):
                        mutated.add(a.operand.name)
            elif hasattr(s, "targets"):  # InputNode
                for tgt in getattr(s, "targets", []):
                    if isinstance(tgt, IdentifierNode):
                        mutated.add(tgt.name)
                    elif hasattr(tgt, "object") and isinstance(tgt.object, IdentifierNode):
                        mutated.add(tgt.object.name)
                    elif hasattr(tgt, "array") and isinstance(tgt.array, IdentifierNode):
                        mutated.add(tgt.array.name)
            elif isinstance(s, IfNode):
                mutated.update(self._find_mutated_vars(s.body))
                mutated.update(self._find_mutated_vars(s.orelse))
            elif isinstance(s, WhileNode):
                mutated.update(self._find_mutated_vars(s.body))
            elif isinstance(s, ForNode):
                if s.init:
                    mutated.update(self._find_mutated_vars([s.init]))
                if s.step:
                    mutated.update(self._find_mutated_vars([s.step]))
                mutated.update(self._find_mutated_vars(s.body))
        return mutated

    def optimize(self, ast_root: Optional[ProgramNode]) -> Tuple[Optional[ProgramNode], Dict[str, Any]]:
        if not ast_root:
            return None, self.stats

        optimized_tree = copy.deepcopy(ast_root)
        optimized_tree.body = self._optimize_stmt_list(optimized_tree.body)
        return optimized_tree, self.stats

    def _optimize_stmt_list(self, stmts: List[ASTNode]) -> List[ASTNode]:
        new_stmts = []
        has_returned = False

        for stmt in stmts:
            if has_returned:
                self.stats["dead_code_eliminated"] += 1
                self.stats["details"].append(f"Eliminated unreachable dead code at line {stmt.line}")
                continue

            opt_stmt = self._optimize_stmt(stmt)
            if opt_stmt:
                new_stmts.append(opt_stmt)
                if isinstance(opt_stmt, ReturnNode):
                    has_returned = True

        return new_stmts

    def _optimize_stmt(self, stmt: ASTNode) -> Optional[ASTNode]:
        if isinstance(stmt, FunctionDefNode):
            prev_env = self.const_env.copy()
            self.const_env.clear()
            stmt.body = self._optimize_stmt_list(stmt.body)
            self.const_env = prev_env
            return stmt

        elif isinstance(stmt, VarDeclNode):
            if stmt.init_val:
                stmt.init_val = self._optimize_expr(stmt.init_val)
                if isinstance(stmt.init_val, LiteralNode) and stmt.init_val.lit_type == "number":
                    self.const_env[stmt.name] = stmt.init_val.value
            return stmt

        elif isinstance(stmt, AssignNode):
            if stmt.value:
                stmt.value = self._optimize_expr(stmt.value)
                if stmt.op == "=" and isinstance(stmt.value, LiteralNode) and stmt.value.lit_type == "number":
                    self.const_env[stmt.target] = stmt.value.value
                elif stmt.target in self.const_env:
                    # Invalidation if modified
                    del self.const_env[stmt.target]
            return stmt

        elif isinstance(stmt, IfNode):
            if stmt.test:
                stmt.test = self._optimize_expr(stmt.test)
                # Static test condition elimination
                if isinstance(stmt.test, LiteralNode):
                    if stmt.test.value is True or (isinstance(stmt.test.value, (int, float)) and stmt.test.value != 0):
                        # Always true: keep body, eliminate else
                        self.stats["dead_code_eliminated"] += len(stmt.orelse)
                        if stmt.orelse:
                            self.stats["details"].append("Eliminated dead 'else' branch in constant condition")
                        stmt.orelse = []
                    elif stmt.test.value is False or stmt.test.value == 0:
                        # Always false: eliminate body, keep else
                        self.stats["dead_code_eliminated"] += len(stmt.body)
                        self.stats["details"].append("Eliminated dead 'if' branch in constant condition")
                        stmt.body = []
            stmt.body = self._optimize_stmt_list(stmt.body)
            stmt.orelse = self._optimize_stmt_list(stmt.orelse)
            return stmt

        elif isinstance(stmt, WhileNode):
            # Invalidate any variables mutated inside loop body
            mutated = self._find_mutated_vars(stmt.body)
            for v in mutated:
                self.const_env.pop(v, None)
            if stmt.test:
                stmt.test = self._optimize_expr(stmt.test)
            stmt.body = self._optimize_stmt_list(stmt.body)
            # After loop finishes, loop variables are no longer initial constants
            for v in mutated:
                self.const_env.pop(v, None)
            return stmt

        elif isinstance(stmt, ForNode):
            mutated = self._find_mutated_vars([stmt])
            for v in mutated:
                self.const_env.pop(v, None)
            if stmt.init:
                stmt.init = self._optimize_stmt(stmt.init)
            for v in mutated:
                self.const_env.pop(v, None)
            if stmt.test:
                stmt.test = self._optimize_expr(stmt.test)
            if stmt.step:
                stmt.step = self._optimize_stmt(stmt.step)
            stmt.body = self._optimize_stmt_list(stmt.body)
            for v in mutated:
                self.const_env.pop(v, None)
            return stmt

        elif isinstance(stmt, ReturnNode):
            if stmt.value:
                stmt.value = self._optimize_expr(stmt.value)
            return stmt

        elif isinstance(stmt, PrintNode):
            stmt.args = [self._optimize_expr(a) for a in stmt.args if a]
            return stmt

        elif isinstance(stmt, ExprStmtNode):
            if stmt.expr:
                stmt.expr = self._optimize_expr(stmt.expr)
            return stmt

        return stmt

    def _optimize_expr(self, expr: Optional[ASTNode]) -> Optional[ASTNode]:
        if not expr:
            return None

        # Preserve variable references in emitted source code. Replacing an identifier
        # with its current value can change the program's observable structure
        # (e.g. `c = a + b` becoming `c = 15`) and is unsafe across mutation/control flow.
        # Constant folding below still folds expressions made only from literal operands.

        # Binary Operation: Fold or Simplify
        if isinstance(expr, BinaryOpNode):
            expr.left = self._optimize_expr(expr.left)
            expr.right = self._optimize_expr(expr.right)

            # Constant Folding: both operands are number literals
            if isinstance(expr.left, LiteralNode) and isinstance(expr.right, LiteralNode):
                if expr.left.lit_type == "number" and expr.right.lit_type == "number":
                    l_val = expr.left.value
                    r_val = expr.right.value
                    folded = None
                    try:
                        if expr.op == "+":
                            folded = l_val + r_val
                        elif expr.op == "-":
                            folded = l_val - r_val
                        elif expr.op == "*":
                            folded = l_val * r_val
                        elif expr.op == "/" and r_val != 0:
                            folded = l_val / r_val if isinstance(l_val, float) or isinstance(r_val, float) else l_val // r_val
                        elif expr.op == "%" and r_val != 0:
                            folded = l_val % r_val
                        elif expr.op == "==":
                            folded = (l_val == r_val)
                        elif expr.op == "!=":
                            folded = (l_val != r_val)
                        elif expr.op == "<":
                            folded = (l_val < r_val)
                        elif expr.op == "<=":
                            folded = (l_val <= r_val)
                        elif expr.op == ">":
                            folded = (l_val > r_val)
                        elif expr.op == ">=":
                            folded = (l_val >= r_val)
                    except Exception:
                        folded = None

                    if folded is not None:
                        self.stats["constants_folded"] += 1
                        lit_type = "boolean" if isinstance(folded, bool) else "number"
                        self.stats["details"].append(f"Folded constant expression '{l_val} {expr.op} {r_val}' -> '{folded}'")
                        return LiteralNode(value=folded, lit_type=lit_type, raw=str(folded), line=expr.line, column=expr.column)

            # Algebraic Simplification:
            # x + 0 -> x
            if expr.op == "+" and isinstance(expr.right, LiteralNode) and expr.right.value == 0:
                self.stats["expressions_simplified"] += 1
                self.stats["details"].append("Simplified identity 'x + 0' -> 'x'")
                return expr.left
            # 0 + x -> x
            if expr.op == "+" and isinstance(expr.left, LiteralNode) and expr.left.value == 0:
                self.stats["expressions_simplified"] += 1
                self.stats["details"].append("Simplified identity '0 + x' -> 'x'")
                return expr.right
            # x * 1 -> x
            if expr.op == "*" and isinstance(expr.right, LiteralNode) and expr.right.value == 1:
                self.stats["expressions_simplified"] += 1
                self.stats["details"].append("Simplified identity 'x * 1' -> 'x'")
                return expr.left
            # 1 * x -> x
            if expr.op == "*" and isinstance(expr.left, LiteralNode) and expr.left.value == 1:
                self.stats["expressions_simplified"] += 1
                self.stats["details"].append("Simplified identity '1 * x' -> 'x'")
                return expr.right
            # x * 0 -> 0
            if expr.op == "*" and (
                (isinstance(expr.right, LiteralNode) and expr.right.value == 0) or
                (isinstance(expr.left, LiteralNode) and expr.left.value == 0)
            ):
                self.stats["expressions_simplified"] += 1
                self.stats["details"].append("Simplified zero product 'x * 0' -> '0'")
                return LiteralNode(value=0, lit_type="number", raw="0", line=expr.line, column=expr.column)

        return expr

def optimize_program(ast_root: Optional[ProgramNode]) -> Tuple[Optional[ProgramNode], Dict[str, Any]]:
    optimizer = ASTOptimizer()
    return optimizer.optimize(ast_root)
