"""
Semantic Analyzer implementation for Stage 3: Semantic Analysis.
Traverses the AST, validates symbols, types, scopes, and captures semantic diagnostics.
"""
from typing import List, Dict, Any, Tuple, Optional
from .symbol_table import SymbolTable, Symbol
from ..parser.ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    ASTNode, ArrayAccessNode, ArrayLiteralNode, StructDefNode, MemberAccessNode,
    InputNode, ClassDefNode, RangeForNode, TryCatchNode, CatchClauseNode,
    ThrowNode, LambdaExprNode, CastExprNode, NamespaceDefNode, EnumDefNode,
    TemplateDefNode, UsingDirectiveNode, TypeAliasNode, SwitchNode, CaseNode,
    ConditionalExprNode, UnsupportedASTNode
)

BUILTIN_FUNCTIONS = {
    "print", "printf", "println", "console.log", "range", "len",
    "scanf", "cin", "cout", "cerr", "clog", "sqrt", "pow", "abs", "max", "min",
    "fixed", "setprecision", "setw", "endl", "std", "getline",
    "stoi", "stod", "to_string", "push_back", "size", "clear",
    "make_pair", "make_tuple", "make_unique", "make_shared",
    "move", "forward", "this", "nullptr", "true", "false",
    "vector", "string", "map", "set", "pair", "tuple", "thread", "mutex",
    "lock_guard", "unique_lock", "async", "future", "atomic", "chrono", "exception"
}

class SemanticAnalyzer:
    """Performs semantic checks on AST nodes and populates the symbol table."""

    def __init__(self, language: str):
        self.language = language.lower()
        self.symbol_table = SymbolTable()
        self.type_table: Dict[str, Dict[str, str]] = {}
        self.errors: List[Dict[str, Any]] = []
        self.in_function = False

    def analyze(self, ast: Optional[ProgramNode]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not ast:
            return [], self.errors

        for stmt in ast.body:
            self._visit_node(stmt)

        # Post-analysis check: unused variables warning
        for sym in self.symbol_table.all_symbols:
            if sym.category in ("variable", "parameter") and sym.reference_count == 0 and not sym.name.startswith("_"):
                self.errors.append({
                    "line": sym.line,
                    "column": sym.column,
                    "message": f"Variable '{sym.name}' declared but never used",
                    "token_value": sym.name,
                    "severity": "warning",
                    "source": "compiler",
                    "category": "Semantic Warning",
                    "suggested_fix": f"Use '{sym.name}' or remove the declaration"
                })

        return self.symbol_table.get_all_records(), self.errors

    def _visit_node(self, node: Optional[ASTNode]):
        if not node:
            return

        if isinstance(node, FunctionDefNode):
            self._visit_function(node)
        elif isinstance(node, StructDefNode):
            self._visit_struct_def(node)
        elif isinstance(node, ClassDefNode):
            self._visit_class_def(node)
        elif isinstance(node, NamespaceDefNode):
            self._visit_namespace(node)
        elif isinstance(node, TemplateDefNode):
            if node.declaration:
                self._visit_node(node.declaration)
        elif isinstance(node, EnumDefNode):
            self._visit_enum(node)
        elif isinstance(node, TypeAliasNode):
            self.type_table[node.name] = {}
            sym = Symbol(name=node.name, type_name="type", scope_level=self.symbol_table.scope_level,
                         line=node.line, column=node.column, category="type", is_initialized=True)
            self.symbol_table.define(sym)
        elif isinstance(node, InputNode):
            self._visit_input(node)
        elif isinstance(node, VarDeclNode):
            self._visit_var_decl(node)
        elif isinstance(node, AssignNode):
            self._visit_assign(node)
        elif isinstance(node, IfNode):
            self._visit_if(node)
        elif isinstance(node, WhileNode):
            self._visit_while(node)
        elif isinstance(node, ForNode):
            self._visit_for(node)
        elif isinstance(node, RangeForNode):
            self._visit_range_for(node)
        elif isinstance(node, SwitchNode):
            self._visit_switch(node)
        elif isinstance(node, CaseNode):
            self._visit_case(node)
        elif isinstance(node, TryCatchNode):
            self._visit_try_catch(node)
        elif isinstance(node, ThrowNode):
            if node.expr:
                self._visit_expr(node.expr)
        elif isinstance(node, ReturnNode):
            self._visit_return(node)
        elif isinstance(node, PrintNode):
            for a in node.args:
                self._visit_expr(a)
        elif isinstance(node, ExprStmtNode):
            self._visit_expr(node.expr)

    def _visit_struct_def(self, node: StructDefNode):
        self.type_table[node.name] = {f.name: getattr(f, "type_name", "auto") for f in node.fields if hasattr(f, 'name')}
        sym = Symbol(
            name=node.name,
            type_name="type",
            scope_level=self.symbol_table.scope_level,
            line=node.line,
            column=node.column,
            category="type",
            is_initialized=True
        )
        self.symbol_table.define(sym)
        for f in node.fields:
            if isinstance(f, VarDeclNode):
                f_sym = Symbol(
                    name=f.name,
                    type_name=f.type_name or "auto",
                    scope_level=self.symbol_table.scope_level + 1,
                    line=f.line,
                    column=f.column,
                    category="field",
                    is_initialized=True,
                    reference_count=1
                )
                self.symbol_table.define(f_sym)
            else:
                self._visit_node(f)
        for m in node.methods:
            self._visit_node(m)

    def _visit_class_def(self, node: ClassDefNode):
        self.type_table[node.name] = {f.name: getattr(f, "type_name", "auto") for f in node.fields if hasattr(f, 'name')}
        sym = Symbol(
            name=node.name,
            type_name="type",
            scope_level=self.symbol_table.scope_level,
            line=node.line,
            column=node.column,
            category="type",
            is_initialized=True
        )
        self.symbol_table.define(sym)
        self.symbol_table.enter_scope()
        for f in node.fields:
            if isinstance(f, VarDeclNode):
                f_sym = Symbol(
                    name=f.name,
                    type_name=f.type_name or "auto",
                    scope_level=self.symbol_table.scope_level,
                    line=f.line,
                    column=f.column,
                    category="field",
                    is_initialized=True,
                    reference_count=1
                )
                self.symbol_table.define(f_sym)
            else:
                self._visit_node(f)
        for m in node.methods:
            self._visit_node(m)
        if node.body:
            for item in node.body:
                if item not in node.fields and item not in node.methods:
                    self._visit_node(item)
        self.symbol_table.exit_scope()

    def _visit_input(self, node: InputNode):
        for tgt in node.targets:
            if isinstance(tgt, IdentifierNode):
                sym = self.symbol_table.lookup(tgt.name)
                if sym:
                    sym.is_initialized = True
                    sym.reference_count += 1
            elif isinstance(tgt, MemberAccessNode):
                self._visit_expr(tgt.object)
            elif isinstance(tgt, ArrayAccessNode):
                self._visit_expr(tgt.array)
                self._visit_expr(tgt.index)

    def _visit_function(self, node: FunctionDefNode):
        # Register function in current scope
        fn_symbol = Symbol(
            name=node.name,
            type_name=node.return_type or "void",
            scope_level=self.symbol_table.scope_level,
            line=node.line,
            column=node.column,
            category="function",
            is_initialized=True
        )
        if not self.symbol_table.define(fn_symbol):
            if self.language not in ("cpp", "c++", "c"):
                self.errors.append({
                    "line": node.line,
                    "column": node.column,
                    "message": f"Redeclaration of function '{node.name}' in the same scope",
                    "token_value": node.name,
                    "severity": "error",
                    "source": "compiler",
                    "category": "Semantic Error"
                })

        # Enter function scope
        prev_in_fn = self.in_function
        self.in_function = True
        self.symbol_table.enter_scope()

        # Register parameters
        for p in node.params:
            p_sym = Symbol(
                name=p.name,
                type_name=p.type_name or "auto",
                scope_level=self.symbol_table.scope_level,
                line=p.line,
                column=p.column,
                category="parameter",
                is_initialized=True
            )
            self.symbol_table.define(p_sym)

        # Visit body
        for s in node.body:
            self._visit_node(s)

        # Exit function scope
        self.symbol_table.exit_scope()
        self.in_function = prev_in_fn

    def _visit_namespace(self, node: NamespaceDefNode):
        sym = Symbol(name=node.name, type_name="namespace", scope_level=self.symbol_table.scope_level,
                     line=node.line, column=node.column, category="namespace", is_initialized=True)
        self.symbol_table.define(sym)
        self.symbol_table.enter_scope()
        for s in node.body:
            self._visit_node(s)
        self.symbol_table.exit_scope()

    def _visit_enum(self, node: EnumDefNode):
        sym = Symbol(name=node.name, type_name="enum", scope_level=self.symbol_table.scope_level,
                     line=node.line, column=node.column, category="type", is_initialized=True)
        self.symbol_table.define(sym)
        for name, val in node.enumerators:
            e_sym = Symbol(name=name, type_name=node.name, scope_level=self.symbol_table.scope_level,
                           line=node.line, column=node.column, category="constant", is_initialized=True)
            self.symbol_table.define(e_sym)
            if val:
                self._visit_expr(val)

    def _visit_range_for(self, node: RangeForNode):
        if node.iterable:
            self._visit_expr(node.iterable)
        self.symbol_table.enter_scope()
        if node.var:
            if isinstance(node.var, VarDeclNode):
                sym = Symbol(
                    name=node.var.name,
                    type_name=node.var.type_name or "auto",
                    scope_level=self.symbol_table.scope_level,
                    line=node.var.line,
                    column=node.var.column,
                    category="variable",
                    is_initialized=True
                )
                self.symbol_table.define(sym)
                if "[" in node.var.name and "]" in node.var.name:
                    inner = node.var.name.strip("[]")
                    for part in inner.split(","):
                        p_name = part.strip().lstrip("&* ")
                        if p_name:
                            p_sym = Symbol(
                                name=p_name,
                                type_name="auto",
                                scope_level=self.symbol_table.scope_level,
                                line=node.var.line,
                                column=node.var.column,
                                category="variable",
                                is_initialized=True
                            )
                            self.symbol_table.define(p_sym)
            else:
                self._visit_node(node.var)
        for s in node.body:
            self._visit_node(s)
        self.symbol_table.exit_scope()

    def _visit_switch(self, node: SwitchNode):
        if node.discriminant:
            self._visit_expr(node.discriminant)
        for c in node.cases:
            self._visit_node(c)

    def _visit_case(self, node: CaseNode):
        if node.value:
            self._visit_expr(node.value)
        for s in node.body:
            self._visit_node(s)

    def _visit_try_catch(self, node: TryCatchNode):
        for s in node.try_block:
            self._visit_node(s)
        for c in node.catch_blocks:
            self.symbol_table.enter_scope()
            if c.param:
                p_sym = Symbol(name=c.param.name, type_name=c.param.type_name or "auto",
                               scope_level=self.symbol_table.scope_level, line=c.param.line,
                               column=c.param.column, category="parameter", is_initialized=True,
                               reference_count=1)
                self.symbol_table.define(p_sym)
            for s in c.body:
                self._visit_node(s)
            self.symbol_table.exit_scope()

    def _visit_lambda(self, node: LambdaExprNode):
        prev_in_fn = self.in_function
        self.in_function = True
        self.symbol_table.enter_scope()
        for p in node.params:
            p_sym = Symbol(name=p.name, type_name=p.type_name or "auto",
                           scope_level=self.symbol_table.scope_level, line=p.line,
                           column=p.column, category="parameter", is_initialized=True)
            self.symbol_table.define(p_sym)
        for s in node.body:
            self._visit_node(s)
        self.symbol_table.exit_scope()
        self.in_function = prev_in_fn

    def _visit_var_decl(self, node: VarDeclNode):
        # Type & initialization check
        inferred_type = node.type_name or "auto"
        if node.init_val:
            self._visit_expr(node.init_val)

        is_init = (node.init_val is not None) or getattr(node, "is_array", False) or (node.type_name in self.type_table)

        sym = Symbol(
            name=node.name,
            type_name=inferred_type,
            scope_level=self.symbol_table.scope_level,
            line=node.line,
            column=node.column,
            category="variable",
            is_initialized=is_init
        )
        if not self.symbol_table.define(sym):
            if self.language in ("c", "java"):
                self.errors.append({
                    "line": node.line,
                    "column": node.column,
                    "message": f"Redeclaration of variable '{node.name}' in the same scope",
                    "token_value": node.name,
                    "severity": "error",
                    "source": "compiler",
                    "category": "Semantic Error"
                })

    def _visit_assign(self, node: AssignNode):
        if node.value:
            self._visit_expr(node.value)

        if node.target_node:
            if isinstance(node.target_node, MemberAccessNode):
                self._visit_expr(node.target_node.object)
                return
            elif isinstance(node.target_node, ArrayAccessNode):
                self._visit_expr(node.target_node.array)
                self._visit_expr(node.target_node.index)
                return
            elif isinstance(node.target_node, UnaryOpNode):
                self._visit_expr(node.target_node.operand)
                return
            elif isinstance(node.target_node, IdentifierNode):
                base_name = node.target_node.name
            else:
                return
        else:
            base_name = node.target
            if '.' in base_name:
                base_name = base_name.split('.')[0]
            if '[' in base_name:
                base_name = base_name.split('[')[0]
            if '->' in base_name:
                base_name = base_name.split('->')[0]
            base_name = base_name.strip()

        if not base_name or not base_name.isidentifier():
            return

        is_cpp = self.language in ("cpp", "c++")
        if is_cpp and ("::" in base_name or base_name in BUILTIN_FUNCTIONS or base_name in self.type_table):
            return

        existing = self.symbol_table.lookup(base_name)
        if not existing:
            if self.language in ("c", "java"):
                self.errors.append({
                    "line": node.line,
                    "column": node.column,
                    "message": f"Undeclared variable '{base_name}' used in assignment",
                    "token_value": base_name,
                    "severity": "error",
                    "source": "compiler",
                    "category": "Semantic Error",
                    "suggested_fix": f"Declare '{base_name}' with a type before assignment"
                })
            elif not is_cpp:
                # In Python / JS, assignment implicitly declares variable in local scope
                sym = Symbol(
                    name=base_name,
                    type_name="auto",
                    scope_level=self.symbol_table.scope_level,
                    line=node.line,
                    column=node.column,
                    category="variable",
                    is_initialized=True
                )
                self.symbol_table.define(sym)
        else:
            existing.is_initialized = True
            existing.reference_count += 1

        if node.value:
            self._visit_expr(node.value)

    def _visit_if(self, node: IfNode):
        if node.test:
            self._visit_expr(node.test)
        self.symbol_table.enter_scope()
        for s in node.body:
            self._visit_node(s)
        self.symbol_table.exit_scope()

        if node.orelse:
            self.symbol_table.enter_scope()
            for s in node.orelse:
                self._visit_node(s)
            self.symbol_table.exit_scope()

    def _visit_while(self, node: WhileNode):
        if node.test:
            self._visit_expr(node.test)
        self.symbol_table.enter_scope()
        for s in node.body:
            self._visit_node(s)
        self.symbol_table.exit_scope()

    def _visit_for(self, node: ForNode):
        self.symbol_table.enter_scope()
        if node.init:
            self._visit_node(node.init)
        if node.test:
            self._visit_expr(node.test)
        if node.step:
            self._visit_node(node.step)
        for s in node.body:
            self._visit_node(s)
        self.symbol_table.exit_scope()

    def _visit_return(self, node: ReturnNode):
        if not self.in_function and self.language in ("c", "cpp", "c++", "java", "python"):
            # Return outside function
            self.errors.append({
                "line": node.line,
                "column": node.column,
                "message": "Return statement outside function body",
                "token_value": "return",
                "severity": "error",
                "source": "compiler",
                "category": "Semantic Error"
            })
        if node.value:
            self._visit_expr(node.value)

    def _visit_expr(self, expr: Optional[ASTNode]):
        if not expr:
            return

        if isinstance(expr, IdentifierNode):
            sym = self.symbol_table.lookup(expr.name)
            is_cpp = self.language in ("cpp", "c++")
            is_known = (
                expr.name in BUILTIN_FUNCTIONS or
                "::" in expr.name or
                expr.name.startswith("std") or
                expr.name.startswith("operator") or
                expr.name.startswith("class ") or
                expr.name.startswith("struct ") or
                (is_cpp and (
                    expr.name in self.type_table or
                    expr.name.startswith("is_") or
                    expr.name.startswith("make_") or
                    expr.name.endswith("_") or
                    expr.name in ("npos", "app", "in", "out", "binary", "trunc", "ate", "fixed", "scientific", "dec", "hex", "oct", "PI")
                ))
            )
            if not sym and not is_known and not is_cpp:
                self.errors.append({
                    "line": expr.line,
                    "column": expr.column,
                    "message": f"Use of undeclared variable '{expr.name}'",
                    "token_value": expr.name,
                    "severity": "error",
                    "source": "compiler",
                    "category": "Semantic Error",
                    "suggested_fix": f"Declare or initialize '{expr.name}' before use"
                })
            elif sym:
                sym.reference_count += 1
                if not sym.is_initialized and sym.category == "variable":
                    self.errors.append({
                        "line": expr.line,
                        "column": expr.column,
                        "message": f"Variable '{expr.name}' may be uninitialized",
                        "token_value": expr.name,
                        "severity": "warning",
                        "source": "compiler",
                        "category": "Semantic Warning"
                    })

        elif isinstance(expr, BinaryOpNode):
            self._visit_expr(expr.left)
            self._visit_expr(expr.right)

        elif isinstance(expr, UnaryOpNode):
            self._visit_expr(expr.operand)

        elif isinstance(expr, CallNode):
            sym = self.symbol_table.lookup(expr.callee)
            if sym:
                sym.reference_count += 1
            elif "." in expr.callee or "->" in expr.callee or "::" in expr.callee:
                base = expr.callee.replace("->", ".").split(".")[0].split("::")[-1].strip()
                base_sym = self.symbol_table.lookup(base)
                if base_sym:
                    base_sym.reference_count += 1
            for a in expr.args:
                self._visit_expr(a)

        elif isinstance(expr, ArrayAccessNode):
            self._visit_expr(expr.array)
            self._visit_expr(expr.index)

        elif isinstance(expr, ArrayLiteralNode):
            for el in expr.elements:
                self._visit_expr(el)

        elif isinstance(expr, MemberAccessNode):
            self._visit_expr(expr.object)
            if expr.member:
                m_sym = self.symbol_table.lookup(expr.member)
                if m_sym:
                    m_sym.reference_count += 1

        elif isinstance(expr, LambdaExprNode):
            self._visit_lambda(expr)

        elif isinstance(expr, CastExprNode):
            if expr.expr:
                self._visit_expr(expr.expr)

        elif isinstance(expr, ConditionalExprNode):
            if expr.test:
                self._visit_expr(expr.test)
            if expr.true_expr:
                self._visit_expr(expr.true_expr)
            if expr.false_expr:
                self._visit_expr(expr.false_expr)

        elif isinstance(expr, UnsupportedASTNode):
            pass
