"""
Clang-based Frontend for Stage 2: Syntax Analysis (C++17 authoritative parser).
Uses libclang native bindings and custom standalone standard library stubs.
Maps Clang AST cursors recursively into normalized ASTNode hierarchy.
Falls back to UnsupportedASTNode for unmapped constructs to guarantee zero dropped nodes.
"""
import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional, Any, Dict

import clang.cindex
from clang.cindex import Index, TranslationUnit, CursorKind, TypeKind, AccessSpecifier, StorageClass

from .ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, RangeForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    IncludeNode, SyntaxErrorRecord, ASTNode, ArrayLiteralNode, ArrayAccessNode,
    ClassDefNode, StructDefNode, MemberAccessNode, InputNode, BreakNode, ContinueNode,
    TryCatchNode, CatchClauseNode, ThrowNode, LambdaExprNode, CastExprNode,
    NamespaceDefNode, EnumDefNode, TemplateDefNode, UsingDirectiveNode, TypeAliasNode,
    SwitchNode, CaseNode, ConditionalExprNode, UnsupportedASTNode
)

LIBCLANG_PATHS = [
    r"C:\Users\koush\AppData\Roaming\Python\Python313\site-packages\clang\native\libclang.dll",
    os.environ.get("LIBCLANG_PATH", ""),
]

def _ensure_libclang_loaded():
    if clang.cindex.Config.loaded:
        return
    for p in LIBCLANG_PATHS:
        if p and os.path.exists(p):
            try:
                clang.cindex.Config.set_library_file(p)
                return
            except Exception:
                pass
    for sp in sys.path:
        cand = os.path.join(sp, "clang", "native", "libclang.dll")
        if os.path.exists(cand):
            try:
                clang.cindex.Config.set_library_file(cand)
                return
            except Exception:
                pass


class ClangFrontend:
    def __init__(self, code: str, filepath: str = "main.cpp", extra_args: Optional[List[str]] = None):
        self.code = code
        self.filepath = filepath
        self.extra_args = extra_args or []
        self.stubs_dir = Path(__file__).parent / "clang_stubs"
        self.errors: List[SyntaxErrorRecord] = []
        _ensure_libclang_loaded()

    def _get_text(self, cursor) -> str:
        try:
            s = cursor.extent.start.offset
            e = cursor.extent.end.offset
            if s is not None and e is not None and 0 <= s <= e <= len(self.code):
                return self.code[s:e]
        except Exception:
            pass
        return cursor.spelling or ""

    def parse(self) -> Tuple[Optional[ProgramNode], List[SyntaxErrorRecord]]:
        try:
            index = Index.create()
            args = [
                "-std=c++17",
                "-nostdinc",
                "-nostdinc++",
                f"-isystem{self.stubs_dir}",
                "-fsyntax-only",
                "-fno-delayed-template-parsing",
                "-Wno-everything",
            ] + self.extra_args

            tu = index.parse(
                self.filepath,
                unsaved_files=[(self.filepath, self.code)],
                args=args,
                options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
            )
        except Exception as e:
            self.errors.append(SyntaxErrorRecord(
                line=1, column=1, message=f"Clang invocation failed: {str(e)}",
                severity="fatal", category="Clang Frontend Error"
            ))
            return None, self.errors

        norm_file = os.path.normpath(self.filepath).lower()
        for diag in tu.diagnostics:
            diag_file = os.path.normpath(diag.location.file.name).lower() if diag.location.file else ""
            if diag_file and diag_file != norm_file and not diag_file.endswith("main.cpp") and not norm_file.endswith(diag_file):
                continue
            
            sev_str = "error"
            if diag.severity == 1:
                sev_str = "note"
            elif diag.severity == 2:
                sev_str = "note"
            elif diag.severity == 3:
                sev_str = "warning"
            elif diag.severity >= 4:
                sev_str = "error"

            self.errors.append(SyntaxErrorRecord(
                line=diag.location.line,
                column=diag.location.column,
                message=diag.spelling,
                severity=sev_str,
                category="Clang Diagnostic",
                suggested_fix=diag.fixits[0].value if diag.fixits else None
            ))

        body: List[ASTNode] = []
        for child in tu.cursor.get_children():
            if child.location.file:
                cfile = os.path.normpath(child.location.file.name).lower()
                if cfile != norm_file and not cfile.endswith("main.cpp") and not norm_file.endswith(cfile):
                    continue
            
            node = self._convert_top_level(child)
            if node:
                if isinstance(node, list):
                    body.extend(node)
                else:
                    body.append(node)

        program = ProgramNode(body=body, line=1, column=1)
        return program, self.errors

    def _convert_top_level(self, cursor) -> Optional[Any]:
        kind = cursor.kind
        line = cursor.location.line
        col = cursor.location.column

        if kind == CursorKind.INCLUSION_DIRECTIVE:
            return IncludeNode(header=cursor.spelling, is_system=True, line=line, column=col)

        if kind == CursorKind.USING_DIRECTIVE:
            return UsingDirectiveNode(target=cursor.spelling, line=line, column=col)

        if kind in (CursorKind.TYPE_ALIAS_DECL, CursorKind.TYPEDEF_DECL):
            return TypeAliasNode(name=cursor.spelling, target_type=cursor.underlying_typedef_type.spelling, line=line, column=col)

        if kind == CursorKind.NAMESPACE:
            ns_body = []
            for ch in cursor.get_children():
                n = self._convert_top_level(ch)
                if n:
                    if isinstance(n, list):
                        ns_body.extend(n)
                    else:
                        ns_body.append(n)
            return NamespaceDefNode(name=cursor.spelling, body=ns_body, line=line, column=col)

        if kind == CursorKind.NAMESPACE_ALIAS:
            ns_refs = [ch.spelling for ch in cursor.get_children() if ch.kind == CursorKind.NAMESPACE_REF]
            target_str = ".".join(ns_refs) if ns_refs else cursor.spelling
            return AssignNode(target=cursor.spelling, value=IdentifierNode(name=target_str, line=line, column=col), op="=", line=line, column=col)

        if kind == CursorKind.ENUM_DECL:
            return self._convert_enum(cursor)

        if kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL, CursorKind.UNION_DECL):
            return self._convert_class_or_struct(cursor)

        if kind in (CursorKind.CLASS_TEMPLATE, CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION):
            return self._convert_class_template(cursor)

        if kind in (CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR, CursorKind.CONVERSION_FUNCTION):
            return self._convert_function(cursor)

        if kind == CursorKind.FUNCTION_TEMPLATE:
            return self._convert_function_template(cursor)

        if kind == CursorKind.VAR_DECL:
            node = self._convert_var_decl(cursor)
            if cursor.semantic_parent and cursor.semantic_parent.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
                return AssignNode(target=node.name, value=node.init_val, op="=", line=line, column=col)
            return node

        if kind in (CursorKind.MACRO_DEFINITION, CursorKind.MACRO_INSTANTIATION):
            return None

        return UnsupportedASTNode(
            raw_kind=cursor.kind.name,
            text=self._get_text(cursor),
            location=f"{line}:{col}",
            details=cursor.spelling,
            line=line, column=col
        )

    def _convert_enum(self, cursor) -> EnumDefNode:
        line = cursor.location.line
        col = cursor.location.column
        name = cursor.spelling
        is_scoped = cursor.is_scoped_enum()
        base_type = cursor.enum_type.spelling if cursor.enum_type else None
        enumerators: List[Tuple[str, Optional[ASTNode]]] = []
        for ch in cursor.get_children():
            if ch.kind == CursorKind.ENUM_CONSTANT_DECL:
                init_val = None
                init_children = list(ch.get_children())
                if init_children:
                    init_val = self._convert_expr(init_children[0])
                enumerators.append((ch.spelling, init_val))
        return EnumDefNode(
            name=name, is_scoped=is_scoped, base_type=base_type,
            enumerators=enumerators, line=line, column=col
        )

    def _convert_class_template(self, cursor) -> TemplateDefNode:
        line = cursor.location.line
        col = cursor.location.column
        params = []
        for ch in cursor.get_children():
            if ch.kind in (CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_NON_TYPE_PARAMETER):
                params.append(ch.spelling)
        cls_node = self._convert_class_or_struct(cursor)
        return TemplateDefNode(params=params, declaration=cls_node, line=line, column=col)

    def _convert_class_or_struct(self, cursor) -> Optional[ClassDefNode]:
        line = cursor.location.line
        col = cursor.location.column
        name = cursor.spelling
        is_struct = (cursor.kind == CursorKind.STRUCT_DECL)

        base_classes = []
        fields = []
        methods = []
        body = []

        for ch in cursor.get_children():
            if ch.kind == CursorKind.CXX_BASE_SPECIFIER:
                acc = "public"
                if ch.access_specifier == AccessSpecifier.PRIVATE:
                    acc = "private"
                elif ch.access_specifier == AccessSpecifier.PROTECTED:
                    acc = "protected"
                is_virt = any(t.spelling == "virtual" for t in ch.get_tokens())
                base_classes.append((ch.type.spelling, acc, is_virt))
            elif ch.kind in (CursorKind.FIELD_DECL, CursorKind.VAR_DECL):
                f_node = self._convert_var_decl(ch)
                if f_node:
                    if ch.kind == CursorKind.VAR_DECL:
                        f_node.is_static = True
                    fields.append(f_node)
                    body.append(f_node)
            elif ch.kind in (CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR, CursorKind.FUNCTION_TEMPLATE, CursorKind.CONVERSION_FUNCTION):
                m_node = self._convert_function(ch)
                if m_node:
                    methods.append(m_node)
                    body.append(m_node)
            elif ch.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL, CursorKind.ENUM_DECL):
                nested = self._convert_top_level(ch)
                if nested:
                    body.append(nested)
            elif ch.kind == CursorKind.FRIEND_DECL:
                for fn_ch in ch.get_children():
                    if fn_ch.kind == CursorKind.FUNCTION_DECL:
                        if any(c.kind == CursorKind.COMPOUND_STMT for c in fn_ch.get_children()):
                            fn_node = self._convert_function(fn_ch)
                            if fn_node:
                                if fn_node.name == "operator<<":
                                    fn_node.name = "__str__"
                                    fn_node.is_static = False
                                    fn_node.params = [ParamNode(name="self", line=fn_node.line, column=fn_node.column)]
                                else:
                                    fn_node.is_static = True
                                methods.append(fn_node)
                                body.append(fn_node)
            elif ch.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                pass
            elif ch.kind in (CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_NON_TYPE_PARAMETER):
                pass
            else:
                un = UnsupportedASTNode(
                    raw_kind=ch.kind.name,
                    text=self._get_text(ch),
                    location=f"{ch.location.line}:{ch.location.column}",
                    details=ch.spelling,
                    line=ch.location.line, column=ch.location.column
                )
                body.append(un)

        return ClassDefNode(
            name=name,
            body=body,
            fields=fields,
            methods=methods,
            base_classes=base_classes,
            is_struct=is_struct,
            line=line, column=col
        )

    def _convert_function_template(self, cursor) -> Any:
        line = cursor.location.line
        col = cursor.location.column
        params = []
        for ch in cursor.get_children():
            if ch.kind in (CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_NON_TYPE_PARAMETER):
                params.append(ch.spelling)
        fn_node = self._convert_function(cursor)
        if isinstance(fn_node, FunctionDefNode):
            fn_node.template_params = params
        return fn_node

    def _convert_function(self, cursor) -> Optional[FunctionDefNode]:
        line = cursor.location.line
        col = cursor.location.column
        name = cursor.spelling
        ret_type = cursor.result_type.spelling if cursor.result_type else "void"

        params: List[ParamNode] = []
        body: List[ASTNode] = []

        is_virtual = cursor.is_virtual_method()
        is_pure_virtual = cursor.is_pure_virtual_method()
        is_const = cursor.is_const_method()
        is_static = cursor.is_static_method()

        is_override = False
        is_noexcept = False
        is_constexpr = False
        for ch in cursor.get_children():
            if ch.kind == CursorKind.CXX_OVERRIDE_ATTR:
                is_override = True

        for tok in cursor.get_tokens():
            if tok.spelling == "noexcept":
                is_noexcept = True
            elif tok.spelling == "constexpr":
                is_constexpr = True

        for ch in cursor.get_children():
            if ch.kind == CursorKind.PARM_DECL:
                default_val = None
                p_children = list(ch.get_children())
                expr_children = [c for c in p_children if not c.kind.name.endswith("_REF")]
                if expr_children:
                    default_val = self._convert_expr(expr_children[0])
                params.append(ParamNode(
                    name=ch.spelling,
                    type_name=ch.type.spelling,
                    default_val=default_val,
                    line=ch.location.line,
                    column=ch.location.column
                ))
            elif ch.kind == CursorKind.COMPOUND_STMT:
                body = self._convert_compound_stmt(ch)

        # Constructor member initializers
        if cursor.kind == CursorKind.CONSTRUCTOR:
            ctor_inits = []
            initialized_fields = set()
            ch_list = list(cursor.get_children())
            i = 0
            while i < len(ch_list):
                c = ch_list[i]
                if c.kind == CursorKind.MEMBER_REF:
                    mem_name = c.spelling
                    initialized_fields.add(mem_name)
                    init_expr = None
                    if i + 1 < len(ch_list) and ch_list[i + 1].kind not in (CursorKind.MEMBER_REF, CursorKind.COMPOUND_STMT):
                        init_expr = self._convert_expr(ch_list[i + 1])
                        if isinstance(init_expr, CallNode) and len(init_expr.args) == 1 and init_expr.callee in ("string", "std::string"):
                            init_expr = init_expr.args[0]
                        i += 1
                    if not init_expr:
                        init_expr = IdentifierNode(name=mem_name, line=c.location.line, column=c.location.column)
                    target_node = MemberAccessNode(object=IdentifierNode(name="this", line=c.location.line, column=c.location.column), member=mem_name, line=c.location.line, column=c.location.column)
                    ctor_inits.append(AssignNode(target=f"this.{mem_name}", value=init_expr, target_node=target_node, line=c.location.line, column=c.location.column))
                elif c.kind in (CursorKind.CALL_EXPR, CursorKind.UNEXPOSED_EXPR):
                    base_call = self._convert_expr(c)
                    if base_call and isinstance(base_call, CallNode) and base_call.callee not in ("string", "std::string", "int", "double", "float", "bool"):
                        clean_args = []
                        for a in base_call.args:
                            if isinstance(a, CallNode) and len(a.args) == 1 and a.callee in ("string", "std::string"):
                                clean_args.append(a.args[0])
                            else:
                                clean_args.append(a)
                        base_call.args = clean_args
                        ctor_inits.append(ExprStmtNode(expr=base_call, line=c.location.line, column=c.location.column))
                i += 1

            if cursor.semantic_parent:
                for f in cursor.semantic_parent.get_children():
                    if f.kind == CursorKind.FIELD_DECL and f.spelling not in initialized_fields:
                        f_type = f.type.spelling.lower()
                        init_expr = None
                        if "vector" in f_type or "deque" in f_type or "list" in f_type:
                            init_expr = CallNode(callee="vector", args=[], line=f.location.line, column=f.location.column)
                        elif "map" in f_type:
                            init_expr = CallNode(callee="map", args=[], line=f.location.line, column=f.location.column)
                        elif "set" in f_type:
                            init_expr = CallNode(callee="set", args=[], line=f.location.line, column=f.location.column)
                        elif "string" in f_type:
                            init_expr = LiteralNode(value="", lit_type="string", line=f.location.line, column=f.location.column)
                        if init_expr:
                            target_node = MemberAccessNode(object=IdentifierNode(name="this", line=f.location.line, column=f.location.column), member=f.spelling, line=f.location.line, column=f.location.column)
                            ctor_inits.append(AssignNode(target=f"this.{f.spelling}", value=init_expr, target_node=target_node, line=f.location.line, column=f.location.column))

            if ctor_inits:
                body = ctor_inits + body

        return FunctionDefNode(
            name=name,
            return_type=ret_type,
            params=params,
            body=body,
            is_virtual=is_virtual,
            is_pure_virtual=is_pure_virtual,
            is_override=is_override,
            is_const=is_const,
            is_static=is_static,
            is_noexcept=is_noexcept,
            is_constexpr=is_constexpr,
            line=line, column=col
        )

    def _convert_var_decl(self, cursor) -> VarDeclNode:
        line = cursor.location.line
        col = cursor.location.column
        name = cursor.spelling
        if cursor.kind == CursorKind.VAR_DECL and cursor.semantic_parent and cursor.semantic_parent.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL) and cursor.lexical_parent != cursor.semantic_parent:
            p_name = cursor.semantic_parent.spelling
            if p_name and not name.startswith(p_name + "."):
                name = f"{p_name}.{name}"
        t = cursor.type
        type_name = t.spelling

        is_const = t.is_const_qualified()
        is_pointer = (t.kind == TypeKind.POINTER)
        is_reference = (t.kind in (TypeKind.LVALUEREFERENCE, TypeKind.RVALUEREFERENCE))
        is_array = (t.kind == TypeKind.CONSTANTARRAY)
        is_static = (cursor.storage_class == StorageClass.STATIC)

        array_size = None
        if is_array:
            array_size = LiteralNode(value=t.element_count, lit_type="number", raw=str(t.element_count), line=line, column=col)

        is_constexpr = any(tok.spelling == "constexpr" for tok in cursor.get_tokens())

        init_val = None
        children = list(cursor.get_children())
        if is_array:
            init_candidates = [c for c in children if c.kind in (CursorKind.INIT_LIST_EXPR, CursorKind.STRING_LITERAL, CursorKind.CALL_EXPR, CursorKind.UNEXPOSED_EXPR)]
            if init_candidates:
                init_val = self._convert_expr(init_candidates[-1])
        else:
            expr_children = [c for c in children if not c.kind.name.endswith("_REF")]
            if expr_children:
                init_val = self._convert_expr(expr_children[-1])
            if not is_array and isinstance(init_val, ArrayLiteralNode):
                decl_kind = t.get_declaration().kind if hasattr(t, "get_declaration") else None
                if decl_kind in (CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL) or t.kind in (TypeKind.RECORD, TypeKind.ELABORATED):
                    clean_type = type_name.replace("struct ", "").replace("class ", "").strip()
                    if clean_type and clean_type not in ("vector", "std::vector", "list", "std::list", "set", "std::set", "deque", "std::deque"):
                        init_val = CallNode(callee=clean_type, args=init_val.elements, line=line, column=col)

        return VarDeclNode(
            name=name,
            type_name=type_name,
            init_val=init_val,
            is_const=is_const,
            is_array=is_array,
            array_size=array_size,
            is_static=is_static,
            is_constexpr=is_constexpr,
            is_reference=is_reference,
            is_pointer=is_pointer,
            line=line, column=col
        )

    def _convert_compound_stmt(self, cursor) -> List[ASTNode]:
        stmts: List[ASTNode] = []
        for ch in cursor.get_children():
            s = self._convert_stmt(ch)
            if s:
                if isinstance(s, list):
                    stmts.extend(s)
                else:
                    stmts.append(s)
        return stmts

    def _convert_stmt(self, cursor) -> Optional[Any]:
        kind = cursor.kind
        line = cursor.location.line
        col = cursor.location.column

        if kind == CursorKind.COMPOUND_STMT:
            return self._convert_compound_stmt(cursor)

        if kind == CursorKind.VAR_DECL:
            return self._convert_var_decl(cursor)

        if kind == CursorKind.DECL_STMT:
            decls = []
            for ch in cursor.get_children():
                if ch.kind == CursorKind.VAR_DECL:
                    decls.append(self._convert_var_decl(ch))
                elif ch.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL, CursorKind.ENUM_DECL):
                    decls.append(self._convert_top_level(ch))
                elif ch.kind == CursorKind.UNEXPOSED_DECL and ch.spelling.startswith("["):
                    names = [s.strip() for s in ch.spelling.strip("[]").split(",") if s.strip()]
                    sub_children = list(ch.get_children())
                    init_expr = None
                    if sub_children:
                        init_conv = self._convert_expr(sub_children[-1])
                        if isinstance(init_conv, CallNode) and len(init_conv.args) == 1:
                            init_expr = init_conv.args[0]
                        else:
                            init_expr = init_conv

                    decl = ch.type.get_declaration() if ch.type else None
                    fields = [f.spelling for f in decl.get_children() if f.kind == CursorKind.FIELD_DECL] if decl else []

                    for i, name in enumerate(names):
                        if i < len(fields) and fields[i]:
                            val = MemberAccessNode(object=init_expr, member=fields[i], line=ch.location.line, column=ch.location.column)
                        else:
                            val = ArrayAccessNode(array=init_expr, index=LiteralNode(value=i, lit_type="number", raw=str(i)), line=ch.location.line, column=ch.location.column)
                        decls.append(VarDeclNode(
                            name=name,
                            type_name="auto",
                            init_val=val,
                            line=ch.location.line,
                            column=ch.location.column
                        ))
            return decls if len(decls) > 1 else (decls[0] if decls else None)

        if kind == CursorKind.IF_STMT:
            children = list(cursor.get_children())
            has_init = False
            if len(children) >= 3 and children[0].kind in (CursorKind.DECL_STMT, CursorKind.VAR_DECL):
                has_init = True
            elif len(children) >= 4:
                has_init = True

            if has_init:
                init_stmt = self._convert_stmt(children[0])
                test = self._convert_expr(children[1]) if len(children) > 1 else None
                body = self._convert_block_stmt(children[2]) if len(children) > 2 else []
                orelse = self._convert_block_stmt(children[3]) if len(children) > 3 else []
                if_node = IfNode(test=test, body=body, orelse=orelse, line=line, column=col)
                if init_stmt:
                    if isinstance(init_stmt, list):
                        return init_stmt + [if_node]
                    return [init_stmt, if_node]
                return if_node
            else:
                test = self._convert_expr(children[0]) if len(children) > 0 else None
                body = self._convert_block_stmt(children[1]) if len(children) > 1 else []
                orelse = self._convert_block_stmt(children[2]) if len(children) > 2 else []
                return IfNode(test=test, body=body, orelse=orelse, line=line, column=col)

        if kind == CursorKind.WHILE_STMT:
            children = list(cursor.get_children())
            test = self._convert_expr(children[0]) if len(children) > 0 else None
            body = self._convert_block_stmt(children[1]) if len(children) > 1 else []
            return WhileNode(test=test, body=body, line=line, column=col)

        if kind == CursorKind.DO_STMT:
            children = list(cursor.get_children())
            body = self._convert_block_stmt(children[0]) if len(children) > 0 else []
            test = self._convert_expr(children[1]) if len(children) > 1 else None
            return WhileNode(test=test, body=body, line=line, column=col)

        if kind == CursorKind.FOR_STMT:
            children = list(cursor.get_children())
            init, test, step = None, None, None
            body_cursor = children[-1] if children else None
            other_children = children[:-1] if children else []
            if len(other_children) == 3:
                init = self._convert_stmt(other_children[0])
                test = self._convert_expr(other_children[1])
                step = self._convert_expr(other_children[2])
            elif len(other_children) == 2:
                init = self._convert_stmt(other_children[0])
                test = self._convert_expr(other_children[1])
            elif len(other_children) == 1:
                test = self._convert_expr(other_children[0])
            body = self._convert_block_stmt(body_cursor) if body_cursor else []
            return ForNode(init=init, test=test, step=step, body=body, line=line, column=col)

        if kind == CursorKind.CXX_FOR_RANGE_STMT:
            children = list(cursor.get_children())
            var_node = self._convert_var_decl(children[0]) if len(children) > 0 else None
            iterable = self._convert_expr(children[1]) if len(children) > 1 else None
            body = self._convert_block_stmt(children[2]) if len(children) > 2 else []
            return RangeForNode(var=var_node, iterable=iterable, body=body, line=line, column=col)

        if kind == CursorKind.SWITCH_STMT:
            children = list(cursor.get_children())
            disc = self._convert_expr(children[0]) if children else None
            cases = []
            if len(children) > 1:
                for ch in children[1].get_children():
                    if ch.kind in (CursorKind.CASE_STMT, CursorKind.DEFAULT_STMT):
                        c_children = list(ch.get_children())
                        val = None
                        c_body = []
                        if ch.kind == CursorKind.CASE_STMT and c_children:
                            val = self._convert_expr(c_children[0])
                            for stmt_child in c_children[1:]:
                                cs = self._convert_stmt(stmt_child)
                                if cs:
                                    if isinstance(cs, list):
                                        c_body.extend(cs)
                                    else:
                                        c_body.append(cs)
                        else:
                            for stmt_child in c_children:
                                cs = self._convert_stmt(stmt_child)
                                if cs:
                                    if isinstance(cs, list):
                                        c_body.extend(cs)
                                    else:
                                        c_body.append(cs)
                        cases.append(CaseNode(value=val, body=c_body, line=ch.location.line, column=ch.location.column))
            return SwitchNode(discriminant=disc, cases=cases, line=line, column=col)

        if kind == CursorKind.CXX_TRY_STMT:
            children = list(cursor.get_children())
            try_block = self._convert_block_stmt(children[0]) if children else []
            catch_blocks = []
            for ch in children[1:]:
                if ch.kind == CursorKind.CXX_CATCH_STMT:
                    c_children = list(ch.get_children())
                    param = None
                    is_all = True
                    c_body = []
                    for cc in c_children:
                        if cc.kind == CursorKind.VAR_DECL:
                            param = ParamNode(name=cc.spelling, type_name=cc.type.spelling, line=cc.location.line, column=cc.location.column)
                            is_all = False
                        elif cc.kind == CursorKind.COMPOUND_STMT:
                            c_body = self._convert_compound_stmt(cc)
                    catch_blocks.append(CatchClauseNode(param=param, body=c_body, is_catch_all=is_all, line=ch.location.line, column=ch.location.column))
            return TryCatchNode(try_block=try_block, catch_blocks=catch_blocks, line=line, column=col)

        if kind == CursorKind.CXX_THROW_EXPR:
            children = list(cursor.get_children())
            expr = self._convert_expr(children[0]) if children else None
            return ThrowNode(expr=expr, line=line, column=col)

        if kind == CursorKind.RETURN_STMT:
            children = list(cursor.get_children())
            val = self._convert_expr(children[0]) if children else None
            return ReturnNode(value=val, line=line, column=col)

        if kind == CursorKind.BREAK_STMT:
            return BreakNode(line=line, column=col)

        if kind == CursorKind.CONTINUE_STMT:
            return ContinueNode(line=line, column=col)

        if kind == CursorKind.NULL_STMT:
            return None

        if kind == CursorKind.CALL_EXPR and cursor.spelling == "operator<<":
            print_node = self._try_convert_cout(cursor)
            if print_node:
                return print_node

        expr = self._convert_expr(cursor)
        if expr:
            if isinstance(expr, (AssignNode, PrintNode, InputNode)):
                return expr
            return ExprStmtNode(expr=expr, line=line, column=col)

        return UnsupportedASTNode(
            raw_kind=cursor.kind.name,
            text=self._get_text(cursor),
            location=f"{line}:{col}",
            details=cursor.spelling,
            line=line, column=col
        )

    def _convert_block_stmt(self, cursor) -> List[ASTNode]:
        if cursor.kind == CursorKind.COMPOUND_STMT:
            return self._convert_compound_stmt(cursor)
        single = self._convert_stmt(cursor)
        if single is None:
            return []
        if isinstance(single, list):
            return single
        return [single]

    def _try_convert_cout(self, cursor) -> Optional[PrintNode]:
        args: List[ASTNode] = []
        cur = cursor
        has_endl = False

        while cur and cur.kind == CursorKind.CALL_EXPR and cur.spelling == "operator<<":
            children = list(cur.get_children())
            if len(children) < 2:
                break
            right_child = children[-1]
            right_text = self._get_text(right_child).strip()
            if right_text in ("std::endl", "endl", "std :: endl"):
                has_endl = True
            elif right_text in ('"\\n"', "'\\n'"):
                has_endl = True
            else:
                right_node = self._convert_expr(right_child)
                if right_node:
                    args.append(right_node)
            cur = children[0]
            if cur.kind == CursorKind.UNEXPOSED_EXPR:
                u_ch = list(cur.get_children())
                if u_ch:
                    cur = u_ch[0]

        stream_name = cur.spelling if cur else ""
        if stream_name in ("cout", "cerr", "clog"):
            args.reverse()
            end_str = "\n" if has_endl else ""
            return PrintNode(args=args, end=end_str, line=cursor.location.line, column=cursor.location.column)
        return None

    def _expr_to_name(self, node: Optional[ASTNode]) -> str:
        if not node:
            return ""
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, ArrayAccessNode):
            arr_str = self._expr_to_name(node.array) or "arr"
            idx_str = node.index.value if isinstance(node.index, LiteralNode) else (node.index.name if isinstance(node.index, IdentifierNode) else "0")
            return f"{arr_str}[{idx_str}]"
        if isinstance(node, MemberAccessNode):
            obj_str = self._expr_to_name(node.object) if node.object else "this"
            return f"{obj_str}.{node.member}" if obj_str else node.member
        if isinstance(node, BinaryOpNode):
            left_str = self._expr_to_name(node.left)
            right_str = self._expr_to_name(node.right)
            return f"({left_str} {node.op} {right_str})"
        if isinstance(node, CallNode):
            args_str = ", ".join(self._expr_to_name(a) for a in node.args)
            return f"{node.callee}({args_str})"
        return ""

    def _convert_expr(self, cursor) -> Optional[ASTNode]:
        kind = cursor.kind
        line = cursor.location.line
        col = cursor.location.column

        if kind in (CursorKind.UNEXPOSED_EXPR, CursorKind.PAREN_EXPR):
            children = list(cursor.get_children())
            if len(children) == 1:
                return self._convert_expr(children[0])
            elif not children:
                text = self._get_text(cursor).strip()
                if text:
                    return IdentifierNode(name=text, line=line, column=col)
            elif len(children) > 1:
                first = self._convert_expr(children[0])
                if isinstance(first, (MemberAccessNode, IdentifierNode)):
                    args = [self._convert_expr(c) for c in children[1:]]
                    args = [a for a in args if a is not None]
                    if args:
                        callee_str = f"{first.object.name if hasattr(first.object, 'name') else str(first.object)}.{first.member}" if isinstance(first, MemberAccessNode) else first.name
                        return CallNode(callee=callee_str, args=args, line=line, column=col)
                return first

        if kind == CursorKind.INTEGER_LITERAL:
            tok = self._get_text(cursor).strip()
            clean_tok = tok.replace("'", "")
            try:
                if len(clean_tok) > 1 and clean_tok.startswith("0") and clean_tok[1].isdigit() and not clean_tok.startswith(("0x", "0X", "0b", "0B", "0o", "0O")):
                    val = int(clean_tok.rstrip("uUlL"), 8)
                else:
                    val = int(clean_tok.rstrip("uUlL"), 0)
            except Exception:
                val = clean_tok
            return LiteralNode(value=val, lit_type="number", raw=tok, line=line, column=col)

        if kind == CursorKind.FLOATING_LITERAL:
            tok = self._get_text(cursor).strip()
            clean_tok = tok.replace("'", "")
            try:
                val = float(clean_tok.rstrip("fFlL"))
            except Exception:
                val = clean_tok
            return LiteralNode(value=val, lit_type="number", raw=tok, line=line, column=col)

        if kind == CursorKind.STRING_LITERAL:
            tok = self._get_text(cursor).strip()
            if (tok.startswith('R"') or tok.startswith('u8R"') or tok.startswith('uR"') or tok.startswith('UR"')) and '(' in tok and ')' in tok:
                s_idx = tok.index('(') + 1
                e_idx = tok.rindex(')')
                val = tok[s_idx:e_idx]
            elif (tok.startswith('"') and tok.endswith('"')) or (tok.startswith('s"') and tok.endswith('"')):
                val = tok[1:-1]
            else:
                val = tok
            return LiteralNode(value=val, lit_type="string", raw=tok, line=line, column=col)

        if kind == CursorKind.CHARACTER_LITERAL:
            tok = self._get_text(cursor).strip()
            val = tok
            for pfx in ("u8'", "u'", "U'", "L'", "'"):
                if val.startswith(pfx) and val.endswith("'"):
                    val = val[len(pfx):-1]
                    break
            return LiteralNode(value=val, lit_type="string", raw=tok, line=line, column=col)

        if kind == CursorKind.CXX_BOOL_LITERAL_EXPR:
            tok = self._get_text(cursor).strip()
            return LiteralNode(value=(tok == "true"), lit_type="boolean", raw=tok, line=line, column=col)

        if kind == CursorKind.CXX_NULL_PTR_LITERAL_EXPR:
            return LiteralNode(value=None, lit_type="null", raw="nullptr", line=line, column=col)

        if kind in (CursorKind.DECL_REF_EXPR, CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF):
            if kind == CursorKind.DECL_REF_EXPR:
                ref = cursor.referenced
                if ref and ref.kind == CursorKind.VAR_DECL and ref.semantic_parent and ref.semantic_parent.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
                    p_name = ref.semantic_parent.spelling
                    if p_name and not cursor.spelling.startswith(p_name + "."):
                        return IdentifierNode(name=f"{p_name}.{cursor.spelling}", line=line, column=col)
                qualifiers = [ch.spelling for ch in cursor.get_children() if ch.kind == CursorKind.NAMESPACE_REF or (ch.kind == CursorKind.TYPE_REF and ref and ref.kind in (CursorKind.CXX_METHOD, CursorKind.FIELD_DECL, CursorKind.VAR_DECL) and ref.semantic_parent and ref.semantic_parent.spelling == ch.spelling)]
                if qualifiers:
                    clean_quals = [re.sub(r"^(class|struct|enum)\s+", "", qual) for qual in qualifiers if qual]
                    q = ".".join(clean_quals)
                    if q and not cursor.spelling.startswith(q + "."):
                        return IdentifierNode(name=f"{q}.{cursor.spelling}", line=line, column=col)
            return IdentifierNode(name=cursor.spelling, line=line, column=col)

        if kind == CursorKind.CXX_THIS_EXPR:
            return IdentifierNode(name="this", line=line, column=col)

        if kind == CursorKind.MEMBER_REF_EXPR:
            children = list(cursor.get_children())
            obj = self._convert_expr(children[0]) if children else IdentifierNode(name="this", line=line, column=col)
            mem = cursor.spelling
            if not mem:
                txt = self._get_text(cursor).strip()
                if "->" in txt:
                    mem = txt.split("->")[-1].strip()
                elif "." in txt:
                    mem = txt.split(".")[-1].strip()
            return MemberAccessNode(object=obj, member=mem or "member", line=line, column=col)

        if kind == CursorKind.ARRAY_SUBSCRIPT_EXPR:
            children = list(cursor.get_children())
            arr = self._convert_expr(children[0]) if len(children) > 0 else None
            idx = self._convert_expr(children[1]) if len(children) > 1 else None
            return ArrayAccessNode(array=arr, index=idx, line=line, column=col)

        if kind == CursorKind.INIT_LIST_EXPR:
            elems = [self._convert_expr(ch) for ch in cursor.get_children()]
            elems = [e for e in elems if e is not None]
            return ArrayLiteralNode(elements=elems, line=line, column=col)

        if kind in (CursorKind.BINARY_OPERATOR, CursorKind.COMPOUND_ASSIGNMENT_OPERATOR):
            children = list(cursor.get_children())
            if len(children) == 2:
                left_c, right_c = children
                left = self._convert_expr(left_c)
                right = self._convert_expr(right_c)

                op = "="
                try:
                    s = left_c.extent.end.offset
                    e = right_c.extent.start.offset
                    if 0 <= s <= e <= len(self.code):
                        op = self.code[s:e].strip()
                except Exception:
                    pass

                if not op:
                    tokens = [t.spelling for t in cursor.get_tokens()]
                    for tok in ("+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=",
                                "==", "!=", "<=", ">=", "&&", "||", "<<", ">>", "+", "-", "*", "/", "%",
                                "<", ">", "&", "|", "^", "="):
                        if tok in tokens:
                            op = tok
                            break

                if op == "<<":
                    p = self._try_convert_cout(cursor)
                    if p:
                        return p

                if op == "=":
                    target_name = left.name if isinstance(left, IdentifierNode) else str(left)
                    return AssignNode(target=target_name, value=right, op="=", target_node=left, line=line, column=col)
                elif op.endswith("=") and op not in ("==", "!=", "<=", ">="):
                    target_name = left.name if isinstance(left, IdentifierNode) else str(left)
                    return AssignNode(target=target_name, value=right, op=op, target_node=left, line=line, column=col)
                else:
                    return BinaryOpNode(left=left, op=op, right=right, line=line, column=col)

        if kind == CursorKind.UNARY_OPERATOR:
            children = list(cursor.get_children())
            if children:
                ch = children[0]
                operand = self._convert_expr(ch)
                is_postfix = False
                op = "-"
                try:
                    prefix = self.code[cursor.extent.start.offset:ch.extent.start.offset].strip()
                    postfix = self.code[ch.extent.end.offset:cursor.extent.end.offset].strip()
                    if postfix:
                        op = postfix
                        is_postfix = True
                    elif prefix:
                        op = prefix
                except Exception:
                    pass
                if op == "&" and ch.kind != CursorKind.MEMBER_REF_EXPR and ((ch.referenced and ch.referenced.kind == CursorKind.FIELD_DECL) or (isinstance(operand, IdentifierNode) and "::" in operand.name)):
                    field_name = ch.spelling or operand.name.split("::")[-1]
                    return LiteralNode(value=field_name, lit_type="string", raw=f'"{field_name}"', line=line, column=col)
                return UnaryOpNode(op=op, operand=operand, is_postfix=is_postfix, line=line, column=col)

        if kind == CursorKind.CONDITIONAL_OPERATOR:
            children = list(cursor.get_children())
            if len(children) == 3:
                test = self._convert_expr(children[0])
                t_expr = self._convert_expr(children[1])
                f_expr = self._convert_expr(children[2])
                return ConditionalExprNode(test=test, true_expr=t_expr, false_expr=f_expr, line=line, column=col)

        if kind == CursorKind.CALL_EXPR:
            if cursor.spelling == "operator<<":
                p = self._try_convert_cout(cursor)
                if p:
                    return p

            # 0. User-defined literals: operator""s, operator""sv, etc.
            if cursor.spelling.startswith('operator""') or cursor.spelling.startswith('operator ""'):
                for ch in cursor.get_children():
                    if ch.kind in (CursorKind.STRING_LITERAL, CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL):
                        return self._convert_expr(ch)
                    conv = self._convert_expr(ch)
                    if isinstance(conv, LiteralNode):
                        return conv

            # Lambda conversion operator, e.g. operator int (*)(int, int)
            if cursor.spelling.startswith("operator") and ("(*)" in cursor.spelling or cursor.spelling.startswith("operator ")):
                for ch in cursor.walk_preorder():
                    if ch.kind == CursorKind.LAMBDA_EXPR:
                        return self._convert_expr(ch)

            # operator bool conversion
            if cursor.spelling in ("operator bool", "operator bool()"):
                for ch in cursor.walk_preorder():
                    if ch != cursor and ch.kind in (CursorKind.CALL_EXPR, CursorKind.DECL_REF_EXPR, CursorKind.MEMBER_REF_EXPR):
                        if ch.spelling not in ("operator bool", "operator bool()"):
                            conv = self._convert_expr(ch)
                            if conv:
                                return conv
                return LiteralNode(value=True, lit_type="boolean", raw="true", line=line, column=col)

            # 1. Overloaded operators
            op_node = None
            if cursor.spelling.startswith("operator"):
                op_node = cursor
            else:
                for ch in cursor.get_children():
                    if ch.kind == CursorKind.OVERLOADED_DECL_REF or (ch.kind == CursorKind.DECL_REF_EXPR and ch.spelling.startswith("operator")):
                        op_node = ch
                        break
                    for gch in ch.get_children():
                        if gch.kind == CursorKind.OVERLOADED_DECL_REF or (gch.kind == CursorKind.DECL_REF_EXPR and gch.spelling.startswith("operator")):
                            op_node = gch
                            break

            if op_node:
                sp = op_node.spelling
                op_raw = sp[len("operator"):].strip() if sp.startswith("operator") else sp
                children = list(cursor.get_children())
                operands = []
                for ch in children:
                    if ch == op_node or any(g == op_node for g in ch.get_children()):
                        continue
                    if ch.spelling == cursor.spelling and ch.kind in (
                        CursorKind.DECL_REF_EXPR, CursorKind.UNEXPOSED_EXPR, CursorKind.MEMBER_REF_EXPR
                    ):
                        continue
                    operands.append(ch)

                conv_args = [self._convert_expr(ch) for ch in operands if ch.kind != CursorKind.TYPE_REF]
                conv_args = [a for a in conv_args if a is not None]

                if op_raw in ("+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "&&", "||", "&", "|", "^", "<<", ">>"):
                    if len(conv_args) == 2:
                        return BinaryOpNode(left=conv_args[0], op=op_raw, right=conv_args[1], line=line, column=col)
                    elif len(conv_args) == 1 and op_raw in ("+", "-", "*", "&"):
                        return UnaryOpNode(op=op_raw, operand=conv_args[0], line=line, column=col)

                if op_raw in ("+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "="):
                    if len(conv_args) >= 2:
                        left = conv_args[0]
                        target_name = left.name if isinstance(left, IdentifierNode) else (left.member if isinstance(left, MemberAccessNode) else str(left))
                        return AssignNode(target=target_name, value=conv_args[1], op=op_raw, target_node=left, line=line, column=col)

                if op_raw == "[]" and len(conv_args) >= 2:
                    return ArrayAccessNode(array=conv_args[0], index=conv_args[1], line=line, column=col)

                if op_raw == "()" and len(conv_args) >= 1:
                    obj_node = conv_args[0]
                    obj_name = obj_node.name if isinstance(obj_node, IdentifierNode) else (self._get_text(operands[0]).strip() or "obj")
                    return CallNode(callee=obj_name, args=conv_args[1:], line=line, column=col)

                if op_raw in ("++", "--"):
                    if conv_args:
                        is_postfix = len(conv_args) > 1 or (len(operands) > 1 and operands[-1].kind == CursorKind.INTEGER_LITERAL)
                        return UnaryOpNode(op=op_raw, operand=conv_args[0], is_postfix=is_postfix, line=line, column=col)

                if op_raw == "!" and conv_args:
                    return UnaryOpNode(op="!", operand=conv_args[0], line=line, column=col)

                if op_raw == "~" and conv_args:
                    return UnaryOpNode(op="~", operand=conv_args[0], line=line, column=col)

                if len(conv_args) == 1:
                    return conv_args[0]

            # 2. Regular calls and constructor calls
            children = list(cursor.get_children())
            is_constructor = (
                (cursor.referenced and cursor.referenced.kind == CursorKind.CONSTRUCTOR) or
                (cursor.type and cursor.type.kind in (TypeKind.RECORD, TypeKind.ELABORATED) and
                 (not children or (children[0].referenced and children[0].referenced.kind not in (CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD))))
            )

            if is_constructor:
                callee_name = cursor.spelling
                arg_children = children
            else:
                if children:
                    ch0_node = self._convert_expr(children[0])
                    callee_name = self._expr_to_name(ch0_node) or self._get_text(children[0]).strip() or cursor.spelling
                    arg_children = children[1:]
                else:
                    callee_name = cursor.spelling
                    arg_children = []

                if callee_name:
                    callee_name = callee_name.replace("::", ".")

                # Qualify static member calls if semantic_parent is available
                ref = cursor.referenced or (children[0].referenced if children else None)
                parent = ref.semantic_parent if ref else None
                if parent and parent.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL, CursorKind.CLASS_TEMPLATE, CursorKind.NAMESPACE):
                    p_name = parent.spelling
                    if p_name and not callee_name.startswith(p_name + ".") and not f".{p_name}." in callee_name and not callee_name.endswith("." + p_name) and callee_name != p_name:
                        method_name = callee_name.split(".")[-1]
                        if ref and ref.is_static_method():
                            if "chrono" in callee_name or p_name == "chrono":
                                if not callee_name.startswith("std.chrono."):
                                    callee_name = f"std.chrono.{method_name}" if p_name == "chrono" else f"std.chrono.{p_name}.{method_name}"
                            elif callee_name.startswith("std."):
                                if p_name != "std":
                                    callee_name = f"std.{p_name}.{method_name}"
                            else:
                                callee_name = f"{p_name}.{method_name}"
                        elif parent.spelling in ("numeric_limits", "system_clock", "steady_clock", "high_resolution_clock"):
                            callee_name = f"{p_name}.{method_name}"

            if cursor.spelling == "get" or (callee_name and callee_name.endswith("get")):
                tokens = [t.spelling for t in cursor.get_tokens()]
                for i in range(len(tokens) - 3):
                    if tokens[i] == "get" and tokens[i+1] == "<" and tokens[i+2].isdigit() and tokens[i+3] == ">":
                        callee_name = f"get<{tokens[i+2]}>"
                        break

            args = []
            for ch in arg_children:
                if ch.kind in (CursorKind.TYPE_REF, CursorKind.NAMESPACE_REF, CursorKind.TEMPLATE_REF):
                    continue
                if ch.extent.start.offset == ch.extent.end.offset:
                    continue
                a = self._convert_expr(ch)
                if a is not None:
                    args.append(a)

            # Simplify smart pointer wrappers: unique_ptr(x) -> x, shared_ptr(x) -> x
            if callee_name in ("std::unique_ptr", "unique_ptr", "std::shared_ptr", "shared_ptr") and len(args) == 1:
                return args[0]

            # Handle make_unique and make_shared
            if callee_name in ("std::make_unique", "make_unique", "std::make_shared", "make_shared") or cursor.spelling in ("make_unique", "make_shared"):
                type_m = re.search(r"<(?:.*::)?(\w+)>", cursor.type.spelling)
                t_name = type_m.group(1) if type_m else None
                if "make_unique" in (callee_name or cursor.spelling):
                    if "[]" in cursor.type.spelling or "[" in self._get_text(cursor):
                        return BinaryOpNode(left=ArrayLiteralNode(elements=[LiteralNode(value=0, lit_type="number", raw="0")]), op="*", right=args[0] if args else LiteralNode(value=0, lit_type="number", raw="0"), line=line, column=col)
                    if t_name and t_name not in ("int", "double", "float", "char", "bool"):
                        return CallNode(callee=t_name, args=args, line=line, column=col)
                    return args[0] if len(args) == 1 else CallNode(callee="tuple", args=args, line=line, column=col)
                elif "make_shared" in (callee_name or cursor.spelling):
                    if t_name and t_name not in ("int", "double", "float", "char", "bool"):
                        return CallNode(callee=t_name, args=args, line=line, column=col)
                    return CallNode(callee="make_shared", args=args, line=line, column=col)

            if (callee_name.endswith(".emplace_back") or cursor.spelling == "emplace_back") and len(children) > 0 and len(args) > 0:
                ch0 = children[0]
                container_type = ""
                if ch0.kind == CursorKind.MEMBER_REF_EXPR:
                    for sub in ch0.get_children():
                        container_type = sub.type.spelling
                        break
                if not container_type:
                    container_type = cursor.type.spelling
                m = re.search(r'<(?:.*::)?(\w+)>', container_type)
                if m:
                    elem_type = m.group(1)
                    if elem_type not in ("int", "double", "float", "char", "bool", "string", "size_t"):
                        if len(args) > 1 or (len(args) == 1 and not (isinstance(args[0], CallNode) and args[0].callee == elem_type)):
                            args = [CallNode(callee=elem_type, args=args, line=line, column=col)]

            return CallNode(callee=callee_name, args=args, line=line, column=col)

        if kind == CursorKind.LAMBDA_EXPR:
            captures = []
            params = []
            body = []
            for ch in cursor.get_children():
                if ch.kind == CursorKind.VARIABLE_REF:
                    captures.append(ch.spelling)
                elif ch.kind == CursorKind.PARM_DECL:
                    params.append(ParamNode(name=ch.spelling, type_name=ch.type.spelling, line=ch.location.line, column=ch.location.column))
                elif ch.kind == CursorKind.COMPOUND_STMT:
                    body = self._convert_compound_stmt(ch)
                    tokens = [t.spelling for t in ch.get_tokens()]
                    if "cout" in tokens and (not body or any("None" in str(s) or (isinstance(s, ExprStmtNode) and isinstance(s.expr, BinaryOpNode) and s.expr.op == "<<") for s in body)):
                            print_args = []
                            i = 0
                            while i < len(tokens):
                                if tokens[i] == "<<" and i + 1 < len(tokens):
                                    tok = tokens[i+1]
                                    if tok in ('"\\n"', "'\\n'", "endl", "std::endl"):
                                        pass
                                    elif tok.startswith('"') or tok.startswith("'"):
                                        print_args.append(LiteralNode(value=tok.strip('"\''), lit_type="string", raw=tok, line=line, column=col))
                                    else:
                                        print_args.append(IdentifierNode(name=tok, line=line, column=col))
                                    i += 1
                                i += 1
                            if print_args:
                                body = [PrintNode(args=print_args, end="\n", line=line, column=col)]
            return LambdaExprNode(captures=captures, params=params, body=body, line=line, column=col)

        if kind in (CursorKind.CXX_STATIC_CAST_EXPR, CursorKind.CXX_DYNAMIC_CAST_EXPR,
                    CursorKind.CXX_REINTERPRET_CAST_EXPR, CursorKind.CXX_CONST_CAST_EXPR,
                    CursorKind.CSTYLE_CAST_EXPR, CursorKind.CXX_FUNCTIONAL_CAST_EXPR):
            cast_map = {
                CursorKind.CXX_STATIC_CAST_EXPR: "static",
                CursorKind.CXX_DYNAMIC_CAST_EXPR: "dynamic",
                CursorKind.CXX_REINTERPRET_CAST_EXPR: "reinterpret",
                CursorKind.CXX_CONST_CAST_EXPR: "const",
                CursorKind.CSTYLE_CAST_EXPR: "cstyle",
                CursorKind.CXX_FUNCTIONAL_CAST_EXPR: "functional",
            }
            children = list(cursor.get_children())
            inner_expr = None
            for ch in children:
                if not ch.kind.name.endswith("_REF"):
                    inner_expr = self._convert_expr(ch)
                    break
            return CastExprNode(
                cast_kind=cast_map.get(kind, "static"),
                target_type=cursor.type.spelling,
                expr=inner_expr,
                line=line, column=col
            )

        if kind == CursorKind.CXX_THROW_EXPR:
            children = list(cursor.get_children())
            expr = self._convert_expr(children[0]) if children else None
            return ThrowNode(expr=expr, line=line, column=col)

        if kind == CursorKind.CXX_UNARY_EXPR:
            text = self._get_text(cursor).strip()
            op = "sizeof"
            if text.startswith("alignof"):
                op = "alignof"
            elif text.startswith("noexcept"):
                op = "noexcept"
            children = list(cursor.get_children())
            if children:
                operand = self._convert_expr(children[0])
            else:
                inner = text
                if text.startswith("sizeof"):
                    inner = text[len("sizeof"):].strip().strip("()")
                elif text.startswith("alignof"):
                    inner = text[len("alignof"):].strip().strip("()")
                elif text.startswith("noexcept"):
                    inner = text[len("noexcept"):].strip().strip("()")
                operand = IdentifierNode(name=inner, line=line, column=col)
            return UnaryOpNode(op=op, operand=operand, line=line, column=col)

        if kind == CursorKind.CXX_NEW_EXPR:
            children = list(cursor.get_children())
            text = self._get_text(cursor)
            is_array = ("[" in text)
            if not is_array:
                call_child = next((ch for ch in children if ch.kind == CursorKind.CALL_EXPR), None)
                if call_child:
                    return self._convert_expr(call_child)
            init_list = None
            args = []
            for ch in children:
                if ch.kind == CursorKind.INIT_LIST_EXPR:
                    init_list = self._convert_expr(ch)
                elif not ch.kind.name.endswith("_REF"):
                    expr_conv = self._convert_expr(ch)
                    if expr_conv:
                        args.append(expr_conv)

            if is_array:
                if init_list:
                    return init_list
                if args:
                    return BinaryOpNode(left=ArrayLiteralNode(elements=[LiteralNode(value=0, lit_type="number", raw="0")]), op="*", right=args[0], line=line, column=col)
                return ArrayLiteralNode(elements=[], line=line, column=col)

            type_name = cursor.type.spelling.rstrip("*").strip()
            if type_name in ("int", "double", "float", "char", "bool", "long", "short"):
                return args[0] if args else LiteralNode(value=0, lit_type="number", raw="0")
            return CallNode(callee=type_name, args=args, line=line, column=col)

        if kind == CursorKind.CXX_DELETE_EXPR:
            children = list(cursor.get_children())
            operand = self._convert_expr(children[0]) if children else None
            return UnaryOpNode(op="delete", operand=operand, line=line, column=col)

        return UnsupportedASTNode(
            raw_kind=cursor.kind.name,
            text=self._get_text(cursor),
            location=f"{line}:{col}",
            details=cursor.spelling,
            line=line, column=col
        )
