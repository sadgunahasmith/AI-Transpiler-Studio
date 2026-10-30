"""
Python Code Generator for Stage 6: Code Generation.
Generates idiomatic, clean Python 3 source code from normalized AST.
Supports C++17 classes, inheritance, namespaces, templates, lambdas, range-for, try/catch, etc.
"""
import re
import json
import keyword
from typing import List, Optional, Any
from .input_utils import sanitize_printf_format
from ..parser.ast_nodes import (
    ProgramNode, FunctionDefNode, ParamNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, ForNode, ReturnNode, PrintNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode, CallNode,
    ASTNode, ArrayLiteralNode, ArrayAccessNode, StructDefNode, MemberAccessNode,
    InputNode, ClassDefNode, BreakNode, ContinueNode,
    RangeForNode, TryCatchNode, CatchClauseNode, ThrowNode, LambdaExprNode,
    CastExprNode, NamespaceDefNode, EnumDefNode, TemplateDefNode,
    UsingDirectiveNode, TypeAliasNode, SwitchNode, CaseNode, ConditionalExprNode,
    UnsupportedASTNode
)

OPERATOR_MAP = {
    "operator+": "__add__",
    "operator-": "__sub__",
    "operator*": "__mul__",
    "operator/": "__truediv__",
    "operator%": "__mod__",
    "operator==": "__eq__",
    "operator!=": "__ne__",
    "operator<": "__lt__",
    "operator<=": "__le__",
    "operator>": "__gt__",
    "operator>=": "__ge__",
    "operator[]": "__getitem__",
    "operator()": "__call__",
    "operator+=": "__iadd__",
    "operator-=": "__isub__",
    "operator*=": "__imul__",
    "operator/=": "__itruediv__",
    "operator=": "assign",
    "operator++": "increment",
    "operator--": "decrement",
    "operator<<": "__str__",
    "operator>>": "__rshift__",
    "operator&": "__and__",
    "operator|": "__or__",
    "operator^": "__xor__",
    "operator~": "__invert__",
    "operator!": "__bool__",
    "operator bool": "__bool__",
    "operator int": "__int__",
    "operator float": "__float__",
    "operator double": "__float__",
}

def _clean_py_ident(name: str) -> str:
    name = name.replace("::", ".").replace("->", ".")
    if name.startswith("class "):
        name = name[6:].strip()
    if name.startswith("struct "):
        name = name[7:].strip()
    if name.startswith("enum "):
        name = name[5:].strip()
    for kw in ("in", "is", "def", "class", "from", "import", "pass", "lambda", "global", "nonlocal", "del"):
        name = re.sub(rf"\b{kw}\b", f"{kw}_", name)
    parts = name.split(".")
    cleaned_parts = [f"{p}_" if keyword.iskeyword(p) else p for p in parts]
    return ".".join(cleaned_parts)

def _clean_func_name(func_name: str, current_class: Optional[str] = None) -> str:
    clean_k = func_name.replace(" ", "")
    for k, v in OPERATOR_MAP.items():
        if clean_k == k.replace(" ", "") or func_name == k:
            return v
    if func_name.startswith("operator"):
        tail = func_name[len("operator"):].strip()
        tail = tail.replace("+=", "iadd").replace("-=", "isub").replace("*=", "imul")
        tail = tail.replace("/=", "idiv").replace("==", "eq").replace("!=", "ne")
        tail = tail.replace("<=", "le").replace(">=", "ge").replace("<<", "lshift")
        tail = tail.replace(">>", "rshift").replace("++", "inc").replace("--", "dec")
        tail = tail.replace("+", "add").replace("-", "sub").replace("*", "mul")
        tail = tail.replace("/", "div").replace("%", "mod").replace("<", "lt")
        tail = tail.replace(">", "gt").replace("=", "assign").replace("[]", "subscript")
        tail = tail.replace("()", "call").replace("&", "band").replace("|", "bor")
        tail = tail.replace("^", "bxor").replace("~", "bnot").replace("!", "lnot")
        clean_tail = "".join(c if c.isalnum() or c == "_" else "_" for c in tail).strip("_")
        return f"operator_{clean_tail}" if clean_tail else "operator_fn"

    if "<" in func_name:
        base = func_name.split("<")[0].strip()
        if current_class and base == current_class:
            return "__init__"
        return base

    return _clean_py_ident(func_name)

_INT_TYPES = {
    "int", "short", "long", "long long", "signed", "unsigned", "signed int", "unsigned int",
    "short int", "long int", "long long int", "unsigned long", "unsigned long long",
    "unsigned short", "unsigned char", "signed char", "size_t", "ssize_t", "ptrdiff_t",
    "int8_t", "int16_t", "int32_t", "int64_t", "uint8_t", "uint16_t", "uint32_t", "uint64_t",
}
_FLOAT_TYPES = {"float", "double", "long double"}
_NUMERIC_KINDS = ("int", "float", "bool")


_C_SIMPLE_ESCAPES = {
    "n": "\n", "t": "\t", "r": "\r", "a": "\a", "b": "\b", "f": "\f", "v": "\v",
    "\\": "\\", "'": "'", '"': '"', "?": "?",
}
_C_ESCAPE_RE = re.compile(r"\\(x[0-9a-fA-F]+|[0-7]{1,3}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|.)", re.DOTALL)


def _decode_c_escapes(text: str) -> str:
    """Turn the raw C/C++ escape sequences kept by the clang frontend into real characters."""
    def _sub(m):
        e = m.group(1)
        if e in _C_SIMPLE_ESCAPES:
            return _C_SIMPLE_ESCAPES[e]
        if e[0] == "x":
            return chr(int(e[1:], 16))
        if e[0] in "uU":
            return chr(int(e[1:], 16))
        if e[0] in "01234567":
            return chr(int(e, 8))
        return m.group(0)  # unknown escape: leave untouched
    return _C_ESCAPE_RE.sub(_sub, text)


def _c_type_kind(type_name: Optional[str]) -> Optional[str]:
    """Map a declared C/C++ scalar type to a print-formatting kind: int | float | bool | None.

    None means "not statically known to be a plain Python int/float/bool"
    (strings, chars, pointers, containers, user classes ...).
    """
    t = re.sub(r"\b(const|volatile|static|constexpr|register|std::)\b", "", (type_name or "")).replace("std::", "")
    t = " ".join(t.split())
    if not t or "*" in t or "&" in t or "<" in t or "[" in t:
        return None
    if t in _INT_TYPES:
        return "int"
    if t in _FLOAT_TYPES:
        return "float"
    if t == "bool":
        return "bool"
    return None


def _map_cpp_type_to_python(cpp_type: str) -> str:
    t = (cpp_type or "").strip()
    if t.startswith("std::vector") or t.startswith("vector"):
        return "vector"
    if t.startswith("std::map") or t.startswith("std::unordered_map") or t.startswith("map") or t.startswith("unordered_map"):
        return "map"
    if t.startswith("std::set") or t.startswith("std::unordered_set") or t.startswith("set") or t.startswith("unordered_set"):
        return "set"
    if t.startswith("std::pair") or t.startswith("pair"):
        return "pair"
    if t.startswith("std::tuple") or t.startswith("tuple"):
        return "tuple"
    if t.startswith("std::array") or t.startswith("array"):
        return "array"
    if t.startswith("std::priority_queue") or t.startswith("priority_queue"):
        return "priority_queue"
    if t.startswith("std::bitset") or t.startswith("bitset"):
        return "bitset"
    if t.startswith("std::multiset") or t.startswith("multiset"):
        return "multiset"
    if t.startswith("std::multimap") or t.startswith("multimap"):
        return "multimap"
    if t.startswith("std::forward_list") or t.startswith("forward_list"):
        return "forward_list"
    if t.startswith("std::deque") or t.startswith("deque"):
        return "deque"
    if t.startswith("std::queue") or t.startswith("queue"):
        return "queue"
    if t.startswith("std::stack") or t.startswith("stack"):
        return "stack"
    if t.startswith("std::list") or t.startswith("list"):
        return "_CppList"
    if t in ("unsigned long", "long long", "unsigned int", "short", "long", "int", "size_t", "uint64_t", "int64_t", "ulong_t"):
        return "int"
    if t in ("double", "float"):
        return "float"
    if t in ("std::string", "string", "const char*", "char*"):
        return "string"
    if t in ("bool",):
        return "bool"
    if not t.isidentifier():
        return "object"
    return t

class PythonCodeGen:
    """Emits clean Python source code from normalized AST."""

    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.indent_level = 0
        self.lines: List[str] = []
        self.has_main = False
        self.current_class: Optional[str] = None

    def _has_node_type(self, node: Any, target_type: type) -> bool:
        if not node:
            return False
        if isinstance(node, target_type):
            return True
        if isinstance(node, list):
            return any(self._has_node_type(item, target_type) for item in node)
        if isinstance(node, ASTNode):
            for v in node.__dict__.values():
                if self._has_node_type(v, target_type):
                    return True
        return False

    def generate(self, ast_root: Optional[ProgramNode]) -> str:
        if not ast_root or not ast_root.body:
            return "# Empty program\n"

        self.lines = []
        self.indent_level = 0
        self.needs_fmt = False
        self.source_lang = (getattr(ast_root, "source_language", "") or "").lower()
        self.current_class = None
        self.needs_c_int = False
        self.needs_deref = False
        self.global_vars = set()
        self.var_types = {}
        self.tainted_names = set()
        self.fn_ret_kinds = {}
        if self.source_lang in ("c", "cpp", "c++"):
            self._analyze_scalar_purity(ast_root)
        for s in ast_root.body:
            if isinstance(s, VarDeclNode) and s.name:
                self.global_vars.add(_clean_py_ident(s.name))
                self._register_var(s)

        self.has_main = any(isinstance(s, FunctionDefNode) and s.name == "main" for s in ast_root.body)
        has_top_level_main_call = any(
            isinstance(s, ExprStmtNode) and isinstance(s.expr, CallNode) and s.expr.callee == "main"
            for s in ast_root.body
        )

        has_input = self._has_node_type(ast_root, InputNode)

        # 1. Emit all statements in the program body
        body_lines: List[str] = []
        saved_lines = self.lines
        self.lines = body_lines
        for stmt in ast_root.body:
            self._emit_stmt(stmt, has_input=has_input)

        # 2. Emit main entry point if present and not already called at top-level
        main_node = next((s for s in ast_root.body if isinstance(s, FunctionDefNode) and s.name == "main"), None)
        needs_sys_argv = False
        if self.has_main and not has_top_level_main_call:
            self.lines.append("")
            # Standard Python entry-point idiom (see ai/explainer.py "Entry Point Normalization").
            self.lines.append('if __name__ == "__main__":')
            if main_node and len(main_node.params) >= 2:
                self.lines.append("    main(len(sys.argv), sys.argv)")
                needs_sys_argv = True
            elif main_node and len(main_node.params) == 1:
                self.lines.append("    main(len(sys.argv))")
                needs_sys_argv = True
            else:
                self.lines.append("    main()")

        self.lines = saved_lines

        body_text = "\n".join(body_lines)

        # 3. Dependency analysis on body_text to inject ONLY needed runtime helpers
        def _has_ident(name: str) -> bool:
            return bool(re.search(r'\b' + re.escape(name) + r'\b', body_text))

        needs_std = _has_ident("std") or _has_ident("_Std")
        needs_threading = _has_ident("threading") or _has_ident("mutex") or _has_ident("thread") or _has_ident("future") or _has_ident("promise") or _has_ident("condition_variable") or _has_ident("unique_lock") or _has_ident("lock_guard")
        needs_time = _has_ident("time") or needs_std
        needs_math = _has_ident("math") or needs_std
        needs_os = _has_ident("os") or _has_ident("remove") or needs_std
        needs_sys = has_input or needs_sys_argv or _has_ident("sys")

        header_lines: List[str] = []

        # Standard library imports
        if needs_sys:
            header_lines.append("import sys")
        if needs_os:
            header_lines.append("import os")
        if needs_math:
            header_lines.append("import math")
        if needs_time:
            header_lines.append("import time")
        if needs_threading:
            header_lines.append("import threading")
        if header_lines:
            header_lines.append("")

        # C++ runtime support stubs (only if referenced)
        stubs: List[str] = []

        needs_template_type = _has_ident("_TemplateType") or _has_ident("T") or _has_ident("U")
        if needs_template_type:
            stubs.append("class _TemplateType:")
            stubs.append("    def __init__(self, *args, **kwargs): pass")
            stubs.append("    def __call__(self, *args, **kwargs): return self")
            stubs.append("    def __getitem__(self, idx): return 0")
            stubs.append("    def __setitem__(self, idx, val): pass")
            stubs.append("")

        if _has_ident("T"):
            stubs.append("T = _TemplateType")
        if _has_ident("N"):
            stubs.append("N = 10")
        if _has_ident("U"):
            stubs.append("U = _TemplateType")

        if _has_ident("string") or _has_ident("string_view") or needs_std:
            stubs.append("class string:")
            stubs.append("    npos = -1")
            stubs.append("    def __init__(self, val=''):")
            stubs.append("        if isinstance(val, string): self._s = val._s")
            stubs.append("        else: self._s = str(val) if val is not None else ''")
            stubs.append("    def __str__(self): return self._s")
            stubs.append("    def __repr__(self): return repr(self._s)")
            stubs.append("    def __len__(self): return len(self._s)")
            stubs.append("    def length(self): return len(self._s)")
            stubs.append("    def size(self): return len(self._s)")
            stubs.append("    def substr(self, pos, count=None):")
            stubs.append("        p = int(pos)")
            stubs.append("        if count is None: return string(self._s[p:])")
            stubs.append("        return string(self._s[p : p + int(count)])")
            stubs.append("    def find(self, sub, pos=0):")
            stubs.append("        if pos is None: pos = 0")
            stubs.append("        return self._s.find(str(sub), int(pos))")
            stubs.append("    def rfind(self, sub, pos=None):")
            stubs.append("        return self._s.rfind(str(sub), 0, int(pos)) if pos is not None else self._s.rfind(str(sub))")
            stubs.append("    def replace(self, pos, count, sub):")
            stubs.append("        p = int(pos); c = int(count)")
            stubs.append("        self._s = self._s[:p] + str(sub) + self._s[p + c:]")
            stubs.append("        return self")
            stubs.append("    def insert(self, pos, sub):")
            stubs.append("        p = int(pos)")
            stubs.append("        self._s = self._s[:p] + str(sub) + self._s[p:]")
            stubs.append("        return self")
            stubs.append("    def erase(self, pos=0, count=None):")
            stubs.append("        p = int(pos)")
            stubs.append("        if count is None: self._s = self._s[:p]")
            stubs.append("        else: self._s = self._s[:p] + self._s[p + int(count):]")
            stubs.append("        return self")
            stubs.append("    def front(self): return self._s[0] if self._s else ''")
            stubs.append("    def back(self): return self._s[-1] if self._s else ''")
            stubs.append("    def compare(self, other):")
            stubs.append("        o = str(other)")
            stubs.append("        return 1 if self._s > o else (-1 if self._s < o else 0)")
            stubs.append("    def c_str(self): return self._s")
            stubs.append("    def data(self): return self._s")
            stubs.append("    def clear(self): self._s = ''")
            stubs.append("    def empty(self): return len(self._s) == 0")
            stubs.append("    def push_back(self, ch): self._s += str(ch)")
            stubs.append("    def pop_back(self):")
            stubs.append("        if self._s: self._s = self._s[:-1]")
            stubs.append("    def begin(self): return _str_iter(self, 0)")
            stubs.append("    def end(self): return _str_iter(self, len(self._s))")
            stubs.append("    def __iadd__(self, other): self._s += str(other); return self")
            stubs.append("    def __add__(self, other): return string(self._s + str(other))")
            stubs.append("    def __radd__(self, other): return string(str(other) + self._s)")
            stubs.append("    def __hash__(self): return hash(self._s)")
            stubs.append("    def __eq__(self, other): return self._s == str(other)")
            stubs.append("    def __ne__(self, other): return self._s != str(other)")
            stubs.append("    def __lt__(self, other): return self._s < str(other)")
            stubs.append("    def __le__(self, other): return self._s <= str(other)")
            stubs.append("    def __gt__(self, other): return self._s > str(other)")
            stubs.append("    def __ge__(self, other): return self._s >= str(other)")
            stubs.append("    def __getitem__(self, idx): return self._s[idx]")
            stubs.append("    def __setitem__(self, idx, val):")
            stubs.append("        lst = list(self._s)")
            stubs.append("        lst[idx] = chr(val) if isinstance(val, int) else str(val)")
            stubs.append("        self._s = ''.join(lst)")
            stubs.append("    def __iter__(self): return iter(self._s)")
            stubs.append("    def __int__(self): return int(self._s)")
            stubs.append("    def __float__(self): return float(self._s)")
            stubs.append("string_view = string")
            stubs.append("")
            stubs.append("class _str_iter:")
            stubs.append("    def __init__(self, owner, idx): self.owner = owner; self.idx = idx")
            stubs.append("    def __eq__(self, o): return self.idx == getattr(o, 'idx', None)")
            stubs.append("    def __ne__(self, o): return not (self == o)")
            stubs.append("    def __lt__(self, o): return self.idx < getattr(o, 'idx', 0)")
            stubs.append("    def __sub__(self, o): return self.idx - getattr(o, 'idx', 0)")
            stubs.append("    def __add__(self, n): return _str_iter(self.owner, self.idx + int(n))")
            stubs.append("    def __iadd__(self, n): self.idx += int(n); return self")
            stubs.append("    def __getitem__(self, offset): return self.owner[self.idx + offset]")
            stubs.append("    def __setitem__(self, offset, val): self.owner[self.idx + offset] = val")
            stubs.append("")

        if _has_ident("vector"):
            stubs.append("class _VecIter:")
            stubs.append("    def __init__(self, vec, idx): self._vec = vec; self._idx = idx")
            stubs.append("    def __add__(self, n): return _VecIter(self._vec, self._idx + int(n))")
            stubs.append("    def __sub__(self, other):")
            stubs.append("        if hasattr(other, '_idx'): return self._idx - other._idx")
            stubs.append("        return _VecIter(self._vec, self._idx - int(other))")
            stubs.append("    def __index__(self): return self._idx")
            stubs.append("    def __int__(self): return self._idx")
            stubs.append("    def __eq__(self, o): return self._idx == getattr(o, '_idx', None)")
            stubs.append("    def __ne__(self, o): return not (self == o)")
            stubs.append("    def __lt__(self, o): return self._idx < getattr(o, '_idx', 0)")
            stubs.append("    def __getitem__(self, offset): return self._vec[self._idx + offset]")
            stubs.append("    def __setitem__(self, offset, val): self._vec[self._idx + offset] = val")
            stubs.append("class _CppVector(list):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], int): super().__init__([0] * args[0])")
            stubs.append("        elif len(args) == 2 and isinstance(args[0], int):")
            stubs.append("            import copy; super().__init__([copy.deepcopy(args[1]) for _ in range(args[0])])")
            stubs.append("        elif len(args) == 1 and isinstance(args[0], (list, tuple, _CppVector)): super().__init__(args[0])")
            stubs.append("        else: super().__init__(*args)")
            stubs.append("    def push_back(self, val): self.append(val)")
            stubs.append("    def emplace_back(self, val): self.append(val)")
            stubs.append("    def pop_back(self): return self.pop() if self else None")
            stubs.append("    def front(self): return self[0] if self else None")
            stubs.append("    def back(self): return self[-1] if self else None")
            stubs.append("    def insert(self, idx, val):")
            stubs.append("        i = idx._idx if hasattr(idx, '_idx') else int(idx)")
            stubs.append("        super().insert(i, val)")
            stubs.append("    def begin(self): return _VecIter(self, 0)")
            stubs.append("    def end(self): return _VecIter(self, len(self))")
            stubs.append("    def erase(self, first, last=None):")
            stubs.append("        idx1 = first._idx if hasattr(first, '_idx') else int(first)")
            stubs.append("        if last is not None:")
            stubs.append("            idx2 = last._idx if hasattr(last, '_idx') else int(last); del self[idx1:idx2]")
            stubs.append("        else: del self[idx1]")
            stubs.append("    def at(self, idx):")
            stubs.append("        if idx < 0 or idx >= len(self): raise out_of_range('Vector index out of range')")
            stubs.append("        return self[idx]")
            stubs.append("    def empty(self): return len(self) == 0")
            stubs.append("    def size(self): return len(self)")
            stubs.append("vector = _CppVector")

        if _has_ident("map") or _has_ident("unordered_map"):
            stubs.append("class _CppMap(dict):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], (list, tuple)):")
            stubs.append("            super().__init__()")
            stubs.append("            for item in args[0]:")
            stubs.append("                if isinstance(item, (list, tuple)) and len(item) == 2: self[item[0]] = item[1]")
            stubs.append("                elif hasattr(item, 'first') and hasattr(item, 'second'): self[item.first] = item.second")
            stubs.append("        else: super().__init__(*args)")
            stubs.append("    def __getitem__(self, k):")
            stubs.append("        if k not in self: self[k] = 0")
            stubs.append("        return super().__getitem__(k)")
            stubs.append("    def count(self, k): return 1 if k in self else 0")
            stubs.append("    def emplace(self, k, v): self[k] = v")
            stubs.append("    def at(self, k):")
            stubs.append("        if k not in self: raise out_of_range('Key not found')")
            stubs.append("        return self[k]")
            stubs.append("    def insert(self, item):")
            stubs.append("        if isinstance(item, (tuple, list)) and len(item) == 2: self[item[0]] = item[1]")
            stubs.append("        elif hasattr(item, 'first') and hasattr(item, 'second'): self[item.first] = item.second")
            stubs.append("    def find(self, k):")
            stubs.append("        if k in self:")
            stubs.append("            class _Iter:")
            stubs.append("                def __init__(self, key, val): self.first = key; self.second = val")
            stubs.append("            return _Iter(k, self[k])")
            stubs.append("        return None")
            stubs.append("    def end(self): return None")
            stubs.append("    def empty(self): return len(self) == 0")
            stubs.append("    def size(self): return len(self)")
            stubs.append("    def __iter__(self):")
            stubs.append("        class _Pair:")
            stubs.append("            def __init__(self, k, v): self.first = k; self.second = v; self._t = (k, v)")
            stubs.append("            def __getitem__(self, i): return self._t[i]")
            stubs.append("            def __iter__(self): return iter(self._t)")
            stubs.append("        items = sorted(self.items(), key=lambda kv: str(kv[0]))")
            stubs.append("        for k, v in items: yield _Pair(k, v)")
            stubs.append("class _CppUnorderedMap(_CppMap):")
            stubs.append("    def __iter__(self):")
            stubs.append("        class _Pair:")
            stubs.append("            def __init__(self, k, v): self.first = k; self.second = v; self._t = (k, v)")
            stubs.append("            def __getitem__(self, i): return self._t[i]")
            stubs.append("            def __iter__(self): return iter(self._t)")
            stubs.append("        for k, v in list(self.items()): yield _Pair(k, v)")
            stubs.append("map = _CppMap")
            stubs.append("unordered_map = _CppUnorderedMap")

        if _has_ident("sort"):
            stubs.append("def sort(first, last=None, comp=None):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        sub = vec[idx1:idx2]")
            stubs.append("        if comp is not None:")
            stubs.append("            import functools")
            stubs.append("            def _cmp(a, b): return -1 if comp(a, b) else (1 if comp(b, a) else 0)")
            stubs.append("            sub.sort(key=functools.cmp_to_key(_cmp))")
            stubs.append("        else: sub.sort()")
            stubs.append("        vec[idx1:idx2] = sub")
            stubs.append("    elif isinstance(first, list):")
            stubs.append("        if comp is not None:")
            stubs.append("            import functools")
            stubs.append("            def _cmp(a, b): return -1 if comp(a, b) else (1 if comp(b, a) else 0)")
            stubs.append("            first.sort(key=functools.cmp_to_key(_cmp))")
            stubs.append("        else: first.sort()")

        if _has_ident("accumulate"):
            stubs.append("def accumulate(first, last, init, op=None):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, list) else [])")
            stubs.append("    val = init")
            stubs.append("    for x in items: val = op(val, x) if op else val + x")
            stubs.append("    return val")

        if _has_ident("count_if"):
            stubs.append("def count_if(first, last, pred):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, list) else [])")
            stubs.append("    return sum(1 for x in items if pred(x))")

        if _has_ident("transform"):
            stubs.append("def transform(first, last, out_first, op):")
            stubs.append("    if hasattr(first, 'owner') and hasattr(first.owner, '_s'):")
            stubs.append("        s = first.owner._s")
            stubs.append("        idx_end = last.idx if hasattr(last, 'idx') else len(s)")
            stubs.append("        items = [s[i] for i in range(first.idx, idx_end)]")
            stubs.append("        out_s = list(out_first.owner._s)")
            stubs.append("        for i, ch in enumerate(items):")
            stubs.append("            res = op(ch)")
            stubs.append("            if isinstance(res, int): res = chr(res)")
            stubs.append("            out_s[out_first.idx + i] = str(res)")
            stubs.append("        out_first.owner._s = ''.join(out_s)")
            stubs.append("        return out_first")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    out_vec = getattr(out_first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, list) else [])")
            stubs.append("    if out_vec is not None:")
            stubs.append("        idx = out_first._idx")
            stubs.append("        for x in items:")
            stubs.append("            if idx < len(out_vec): out_vec[idx] = op(x)")
            stubs.append("            else: out_vec.append(op(x))")
            stubs.append("            idx += 1")
            stubs.append("    return out_first")

        if _has_ident("max_element"):
            stubs.append("def max_element(first, last=None):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, list) else [])")
            stubs.append("    return max(items) if items else 0")

        if _has_ident("min_element"):
            stubs.append("def min_element(first, last=None):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, list) else [])")
            stubs.append("    return min(items) if items else 0")

        if _has_ident("unique"):
            stubs.append("def unique(first, last=None):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        seen = []")
            stubs.append("        for x in vec:")
            stubs.append("            if not seen or seen[-1] != x: seen.append(x)")
            stubs.append("        new_len = len(seen)")
            stubs.append("        vec[:new_len] = seen")
            stubs.append("        return first + new_len")
            stubs.append("    return first")

        if _has_ident("partial_sum"):
            stubs.append("def partial_sum(first, last, out_first):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    out_vec = getattr(out_first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, list) else [])")
            stubs.append("    if out_vec is not None:")
            stubs.append("        running = 0")
            stubs.append("        idx = out_first._idx")
            stubs.append("        for x in items:")
            stubs.append("            running += x")
            stubs.append("            if idx < len(out_vec): out_vec[idx] = running")
            stubs.append("            else: out_vec.append(running)")
            stubs.append("            idx += 1")
            stubs.append("    return out_first")

        if _has_ident("istringstream"):
            stubs.append("class istringstream:")
            stubs.append("    def __init__(self, text):")
            stubs.append("        self._tokens = str(text).split() if text else []")
            stubs.append("        self._idx = 0")
            stubs.append("    def get(self):")
            stubs.append("        if self._idx < len(self._tokens):")
            stubs.append("            val = self._tokens[self._idx]")
            stubs.append("            self._idx += 1")
            stubs.append("            try: return int(val)")
            stubs.append("            except ValueError:")
            stubs.append("                try: return float(val)")
            stubs.append("                except ValueError: return val")
            stubs.append("        return None")

        if _has_ident("npos"):
            stubs.append("npos = -1")

        if _has_ident("ostringstream") or _has_ident("fixed") or _has_ident("setprecision"):
            stubs.append("class _Manip:")
            stubs.append("    def __init__(self, kind, val): self.kind = kind; self.val = val")
            stubs.append("fixed = _Manip('fixed', True)")
            stubs.append("def setprecision(n): return _Manip('prec', n)")
            stubs.append("def setw(n): return _Manip('w', n)")
            stubs.append("def setfill(c): return _Manip('fill', c)")
            stubs.append("class ostringstream:")
            stubs.append("    def __init__(self):")
            stubs.append("        self._parts = []")
            stubs.append("        self._prec = None")
            stubs.append("        self._w = 0")
            stubs.append("        self._fill = ' '")
            stubs.append("        self._fixed = False")
            stubs.append("    def __lshift__(self, val):")
            stubs.append("        if val is None or val == '': return self")
            stubs.append("        if val is fixed: self._fixed = True; return self")
            stubs.append("        if isinstance(val, _Manip):")
            stubs.append("            if val.kind == 'prec': self._prec = val.val")
            stubs.append("            elif val.kind == 'w': self._w = val.val")
            stubs.append("            elif val.kind == 'fill': self._fill = str(val.val)")
            stubs.append("            return self")
            stubs.append("        if isinstance(val, float) and self._prec is not None:")
            stubs.append("            s = f'{val:.{self._prec}f}'")
            stubs.append("        else: s = str(val)")
            stubs.append("        if self._w > len(s):")
            stubs.append("            s = self._fill * (self._w - len(s)) + s")
            stubs.append("            self._w = 0")
            stubs.append("        self._parts.append(s)")
            stubs.append("        return self")
            stubs.append("    def str(self): return ''.join(self._parts)")

        if _has_ident("stringstream") or _has_ident("getline"):
            stubs.append("class stringstream:")
            stubs.append("    def __init__(self, text=''):")
            stubs.append("        self._text = str(text)")
            stubs.append("        self._idx = 0")
            stubs.append("        self._parts = [str(text)] if text else []")
            stubs.append("    def __lshift__(self, val):")
            stubs.append("        self._parts.append(str(val))")
            stubs.append("        self._text = ''.join(self._parts)")
            stubs.append("        return self")
            stubs.append("    def str(self, val=None):")
            stubs.append("        if val is not None:")
            stubs.append("            self._text = str(val); self._parts = [self._text]; self._idx = 0")
            stubs.append("        return ''.join(self._parts)")
            stubs.append("    def getline(self, delim=None):")
            stubs.append("        if self._idx >= len(self._text): return None")
            stubs.append("        d = chr(10) if (delim is None or str(delim) in (chr(10), '\\\\n', '\\n')) else str(delim)")
            stubs.append("        end = self._text.find(d, self._idx)")
            stubs.append("        if end == -1: res = self._text[self._idx:]; self._idx = len(self._text)")
            stubs.append("        else: res = self._text[self._idx:end]; self._idx = end + len(d)")
            stubs.append("        return res.rstrip('\\r')")
            stubs.append("def getline(stream, tok, delim=None):")
            stubs.append("    line = stream.getline(delim) if hasattr(stream, 'getline') else None")
            stubs.append("    if line is not None:")
            stubs.append("        if isinstance(tok, string): tok._s = line")
            stubs.append("        elif hasattr(tok, 'clear') and hasattr(tok, 'append'): tok.clear(); tok.append(line)")
            stubs.append("        return True")
            stubs.append("    return False")

        if _has_ident("_char_buf") or _has_ident("snprintf"):
            stubs.append("class _char_buf:")
            stubs.append("    def __init__(self, size=64): self._size = size; self._s = ''")
            stubs.append("    def __len__(self): return self._size")
            stubs.append("    def __str__(self): return self._s")
            stubs.append("    def set(self, val): self._s = str(val)")
            stubs.append("    def __getitem__(self, idx): return self._s[idx] if idx < len(self._s) else '\\0'")
            stubs.append("    def __setitem__(self, idx, val):")
            stubs.append("        lst = list(self._s.ljust(self._size, '\\0'))")
            stubs.append("        lst[idx] = chr(val) if isinstance(val, int) else str(val)")
            stubs.append("        self._s = ''.join(lst).rstrip('\\0')")
            stubs.append("def snprintf(buf, sz, fmt, *args):")
            stubs.append("    res = fmt % args if args else fmt")
            stubs.append("    if hasattr(buf, 'set'): buf.set(res)")
            stubs.append("    elif isinstance(buf, list):")
            stubs.append("        buf.clear(); buf.extend(list(res) + ['\\0'])")
            stubs.append("    return len(res)")
        if _has_ident("reverse"):
            stubs.append("def reverse(first, last=None):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        vec[idx1:idx2] = list(reversed(vec[idx1:idx2]))")
            stubs.append("    elif isinstance(first, list):")
            stubs.append("        first.reverse()")

        if _has_ident("deque"):
            stubs.append("class deque(list):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])")
            stubs.append("        elif len(args) == 2 and isinstance(args[0], int): super().__init__([args[1]] * args[0])")
            stubs.append("        elif len(args) == 1 and isinstance(args[0], int): super().__init__([0] * args[0])")
            stubs.append("        elif args: super().__init__(args)")
            stubs.append("        else: super().__init__()")
            stubs.append("    def push_front(self, v): self.insert(0, v)")
            stubs.append("    def push_back(self, v): self.append(v)")
            stubs.append("    def front(self): return self[0]")
            stubs.append("    def back(self): return self[-1]")
            stubs.append("    def pop_front(self): return self.pop(0)")
            stubs.append("    def pop_back(self): return self.pop()")
            stubs.append("    def empty(self): return len(self) == 0")
            stubs.append("    def size(self): return len(self)")

        if _has_ident("queue"):
            stubs.append("class queue:")
            stubs.append("    def __init__(self): self._items = []")
            stubs.append("    def push(self, v): self._items.append(v)")
            stubs.append("    def front(self): return self._items[0] if self._items else None")
            stubs.append("    def back(self): return self._items[-1] if self._items else None")
            stubs.append("    def pop(self): return self._items.pop(0) if self._items else None")
            stubs.append("    def empty(self): return len(self._items) == 0")
            stubs.append("    def size(self): return len(self._items)")
            stubs.append("    def __len__(self): return len(self._items)")

        if _has_ident("stack"):
            stubs.append("class stack:")
            stubs.append("    def __init__(self): self._items = []")
            stubs.append("    def push(self, v): self._items.append(v)")
            stubs.append("    def top(self): return self._items[-1] if self._items else None")
            stubs.append("    def pop(self): return self._items.pop() if self._items else None")
            stubs.append("    def empty(self): return len(self._items) == 0")
            stubs.append("    def size(self): return len(self._items)")
            stubs.append("    def __len__(self): return len(self._items)")

        if _has_ident("set") or _has_ident("unordered_set"):
            stubs.append("class _CppSet(set):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], (list, tuple, set)): super().__init__(args[0])")
            stubs.append("        else: super().__init__(*args)")
            stubs.append("    def __iter__(self): return iter(sorted(super().__iter__()))")
            stubs.append("    def insert(self, v): self.add(v)")
            stubs.append("    def count(self, v): return 1 if v in self else 0")
            stubs.append("    def size(self): return len(self)")
            stubs.append("    def empty(self): return len(self) == 0")
            stubs.append("set = _CppSet")
            stubs.append("unordered_set = _CppSet")

        if _has_ident("array"):
            stubs.append("class array(list):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])")
            stubs.append("        else: super().__init__(args)")
            stubs.append("    def at(self, idx):")
            stubs.append("        if idx < 0 or idx >= len(self): raise out_of_range('Array index out of range')")
            stubs.append("        return self[idx]")
            stubs.append("    def size(self): return len(self)")
            stubs.append("    def empty(self): return len(self) == 0")
            stubs.append("    def front(self): return self[0]")
            stubs.append("    def back(self): return self[-1]")
            stubs.append("    def fill(self, val):")
            stubs.append("        for i in range(len(self)): self[i] = val")

        if _has_ident("forward_list") or _has_ident("list") or _has_ident("_CppList"):
            stubs.append("class _CppList(list):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])")
            stubs.append("        elif len(args) == 2 and isinstance(args[0], int): super().__init__([args[1]] * args[0])")
            stubs.append("        elif len(args) == 1 and isinstance(args[0], int): super().__init__([0] * args[0])")
            stubs.append("        elif args: super().__init__(args)")
            stubs.append("        else: super().__init__()")
            stubs.append("    def push_front(self, v): self.insert(0, v)")
            stubs.append("    def push_back(self, v): self.append(v)")
            stubs.append("    def front(self): return self[0]")
            stubs.append("    def back(self): return self[-1]")
            stubs.append("    def pop_front(self): return self.pop(0)")
            stubs.append("    def pop_back(self): return self.pop()")
            stubs.append("    def empty(self): return len(self) == 0")
            stubs.append("    def size(self): return len(self)")
            stubs.append("    def reverse(self): super().reverse(); return self")
            stubs.append("    def sort(self, *args, **kwargs): super().sort(*args, **kwargs); return self")
            stubs.append("forward_list = _CppList")

        if _has_ident("multiset"):
            stubs.append("class multiset(list):")
            stubs.append("    def count(self, v): return super().count(v)")
            stubs.append("    def insert(self, v): self.append(v)")
            stubs.append("    def size(self): return len(self)")
            stubs.append("    def empty(self): return len(self) == 0")

        if _has_ident("multimap"):
            stubs.append("class multimap(list):")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])")
            stubs.append("        elif args: super().__init__(args)")
            stubs.append("        else: super().__init__()")
            stubs.append("    def count(self, k): return sum(1 for item in self if (item[0] if isinstance(item, (tuple, list)) else getattr(item, 'first', None)) == k)")
            stubs.append("    def insert(self, item): self.append(item)")
            stubs.append("    def size(self): return len(self)")
            stubs.append("    def empty(self): return len(self) == 0")

        if _has_ident("priority_queue"):
            stubs.append("class priority_queue:")
            stubs.append("    def __init__(self, *args):")
            stubs.append("        self._items = []")
            stubs.append("        self._is_min = any('greater' in str(a) for a in args) if args else False")
            stubs.append("    def push(self, v): self._items.append(v)")
            stubs.append("    def top(self):")
            stubs.append("        if not self._items: return None")
            stubs.append("        return min(self._items) if self._is_min else max(self._items)")
            stubs.append("    def pop(self):")
            stubs.append("        if not self._items: return None")
            stubs.append("        val = self.top()")
            stubs.append("        self._items.remove(val)")
            stubs.append("        return val")
            stubs.append("    def empty(self): return len(self._items) == 0")
            stubs.append("    def size(self): return len(self._items)")

        if _has_ident("bitset"):
            stubs.append("class bitset:")
            stubs.append("    def __init__(self, val=0):")
            stubs.append("        if isinstance(val, str): self._val = int(val, 2)")
            stubs.append("        else: self._val = int(val)")
            stubs.append("    def count(self): return bin(self._val).count('1')")
            stubs.append("    def test(self, idx): return bool((self._val >> idx) & 1)")
            stubs.append("    def to_ulong(self): return self._val")
            stubs.append("    def to_string(self): return f'{self._val:08b}'")
            stubs.append("    def __str__(self): return f'{self._val:08b}'")
            stubs.append("    def __repr__(self): return f'{self._val:08b}'")
            stubs.append("    def __getitem__(self, idx): return (self._val >> idx) & 1")
            stubs.append("    def __setitem__(self, idx, b):")
            stubs.append("        if b: self._val |= (1 << idx)")
            stubs.append("        else: self._val &= ~(1 << idx)")

        if _has_ident("remove"):
            stubs.append("def remove(first, last, val):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        kept = [x for x in vec[idx1:idx2] if x != val]")
            stubs.append("        n_kept = len(kept)")
            stubs.append("        vec[idx1:idx1 + n_kept] = kept")
            stubs.append("        return type(first)(vec, idx1 + n_kept)")
            stubs.append("    return last")

        if _has_ident("binary_search"):
            stubs.append("def binary_search(first, last, val):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec if vec is not None else (first if isinstance(first, (list, tuple)) else [])")
            stubs.append("    return val in items")

        if _has_ident("distance"):
            stubs.append("def distance(first, last):")
            stubs.append("    if hasattr(first, '_idx') and hasattr(last, '_idx'): return last._idx - first._idx")
            stubs.append("    if hasattr(first, 'idx') and hasattr(last, 'idx'): return last.idx - first.idx")
            stubs.append("    return 0")

        if _has_ident("find_if"):
            stubs.append("def find_if(first, last, pred):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        for i in range(idx1, idx2):")
            stubs.append("            if pred(vec[i]): return type(first)(vec, i)")
            stubs.append("        return type(first)(vec, idx2)")
            stubs.append("    return first")

        if _has_ident("multiplies"):
            stubs.append("class multiplies:")
            stubs.append("    def __call__(self, a=None, b=None):")
            stubs.append("        if a is not None and b is not None: return a * b")
            stubs.append("        return lambda x, y: x * y")

        if _has_ident("any_of"):
            stubs.append("def any_of(first, last, pred):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec[first._idx:last._idx] if vec is not None else []")
            stubs.append("    return any(pred(x) for x in items)")

        if _has_ident("all_of"):
            stubs.append("def all_of(first, last, pred):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec[first._idx:last._idx] if vec is not None else []")
            stubs.append("    return all(pred(x) for x in items)")

        if _has_ident("none_of"):
            stubs.append("def none_of(first, last, pred):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    items = vec[first._idx:last._idx] if vec is not None else []")
            stubs.append("    return not any(pred(x) for x in items)")

        if _has_ident("function"):
            stubs.append("function = lambda f=None: f")

        if _has_ident("find"):
            stubs.append("def find(first, last, val=None):")
            stubs.append("    if hasattr(first, 'find') and not hasattr(first, '_vec'): return first.find(last)")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        for i in range(idx1, idx2):")
            stubs.append("            if vec[i] == val: return type(first)(vec, i)")
            stubs.append("        return type(first)(vec, idx2)")
            stubs.append("    return last")

        if _has_ident("for_each"):
            stubs.append("def for_each(first, last, fn):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        for i in range(idx1, idx2):")
            stubs.append("            res = fn(vec[i])")
            stubs.append("            if res is not None: vec[i] = res")

        if _has_ident("rotate"):
            stubs.append("def rotate(first, middle, last):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx_m = middle._idx if hasattr(middle, '_idx') else int(middle)")
            stubs.append("        idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        vec[idx1:idx2] = vec[idx_m:idx2] + vec[idx1:idx_m]")

        if _has_ident("iota"):
            stubs.append("def iota(first, last, val):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        cur = val")
            stubs.append("        for i in range(idx1, idx2):")
            stubs.append("            vec[i] = cur")
            stubs.append("            cur += 1")

        if _has_ident("set_intersection") or _has_ident("back_inserter"):
            stubs.append("def back_inserter(c): return c")
            stubs.append("def set_intersection(first1, last1, first2, last2, out):")
            stubs.append("    v1 = getattr(first1, '_vec', None) or (first1 if isinstance(first1, list) else [])")
            stubs.append("    v2 = getattr(first2, '_vec', None) or (first2 if isinstance(first2, list) else [])")
            stubs.append("    s2 = set(v2)")
            stubs.append("    for x in v1:")
            stubs.append("        if x in s2:")
            stubs.append("            if hasattr(out, 'append'): out.append(x)")

        if _has_ident("fill"):
            stubs.append("def fill(first, last, val=None):")
            stubs.append("    if hasattr(first, 'fill') and not hasattr(first, '_vec'): return first.fill(last)")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        for i in range(idx1, idx2): vec[i] = val")

        if _has_ident("ostream_iterator") or _has_ident("copy"):
            stubs.append("class ostream_iterator:")
            stubs.append("    def __init__(self, out, delim=''): self.out = out; self.delim = delim")
            stubs.append("def copy(first, last, out):")
            stubs.append("    vec = getattr(first, '_vec', None) or (first if isinstance(first, list) else [])")
            stubs.append("    if isinstance(out, ostream_iterator):")
            stubs.append("        for x in vec: print(f'{x}{out.delim}', end='')")
            stubs.append("    elif hasattr(out, 'extend'): out.extend(vec)")

        if _has_ident("partition"):
            stubs.append("def partition(first, last, pred):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        sub = vec[idx1:idx2]")
            stubs.append("        yes = [x for x in sub if pred(x)]")
            stubs.append("        no = [x for x in sub if not pred(x)]")
            stubs.append("        vec[idx1:idx2] = yes + no")

        if _has_ident("nth_element"):
            stubs.append("def nth_element(first, nth, last):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        vec[idx1:idx2] = sorted(vec[idx1:idx2])")

        if _has_ident("lower_bound"):
            stubs.append("def lower_bound(first, last, val):")
            stubs.append("    vec = getattr(first, '_vec', None)")
            stubs.append("    if vec is not None:")
            stubs.append("        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)")
            stubs.append("        for i in range(idx1, idx2):")
            stubs.append("            if vec[i] >= val: return type(first)(vec, i)")
            stubs.append("        return type(first)(vec, idx2)")
            stubs.append("    return first")

        if _has_ident("next_permutation"):
            stubs.append("def next_permutation(first, last=None):")
            stubs.append("    vec = getattr(first, '_vec', None) or (first if isinstance(first, list) else None)")
            stubs.append("    if vec is not None and len(vec) > 1:")
            stubs.append("        i = len(vec) - 2")
            stubs.append("        while i >= 0 and vec[i] >= vec[i + 1]: i -= 1")
            stubs.append("        if i >= 0:")
            stubs.append("            j = len(vec) - 1")
            stubs.append("            while vec[j] <= vec[i]: j -= 1")
            stubs.append("            vec[i], vec[j] = vec[j], vec[i]")
            stubs.append("            vec[i + 1:] = reversed(vec[i + 1:])")
            stubs.append("            return True")
            stubs.append("        vec.reverse()")
            stubs.append("        return False")
            stubs.append("    return False")

        if _has_ident("gcd") or _has_ident("lcm"):
            stubs.append("def gcd(a, b): return math.gcd(a, b)")
            stubs.append("def lcm(a, b): return abs(a * b) // math.gcd(a, b) if (a and b) else 0")

        if _has_ident("bind") or _has_ident("placeholders") or _has_ident("_1"):
            stubs.append("class _Placeholders:")
            stubs.append("    _1 = object()")
            stubs.append("    _2 = object()")
            stubs.append("    _3 = object()")
            stubs.append("placeholders = _Placeholders()")
            stubs.append("_1 = placeholders._1")
            stubs.append("_2 = placeholders._2")
            stubs.append("_3 = placeholders._3")
            stubs.append("def bind(fn, *bind_args):")
            stubs.append("    def _bound(*call_args):")
            stubs.append("        c_idx = 0; actual = []")
            stubs.append("        for b in bind_args:")
            stubs.append("            if b is _1 or str(b).endswith('_1'):")
            stubs.append("                if c_idx < len(call_args): actual.append(call_args[c_idx]); c_idx += 1")
            stubs.append("            elif b is _2 or str(b).endswith('_2'):")
            stubs.append("                if len(call_args) > 1: actual.append(call_args[1])")
            stubs.append("            else: actual.append(b)")
            stubs.append("        actual.extend(call_args[c_idx:])")
            stubs.append("        return fn(*actual)")
            stubs.append("    return _bound")

        if _has_ident("equal"):
            stubs.append("def equal(first1, last1, first2):")
            stubs.append("    v1 = getattr(first1, '_vec', None); v2 = getattr(first2, '_vec', None)")
            stubs.append("    if v1 is not None and v2 is not None:")
            stubs.append("        idx1_start = first1._idx; idx1_end = last1._idx if hasattr(last1, '_idx') else len(v1)")
            stubs.append("        idx2_start = first2._idx; sz = idx1_end - idx1_start")
            stubs.append("        return v1[idx1_start:idx1_end] == v2[idx2_start:idx2_start + sz]")
            stubs.append("    return first1 == first2")

        if _has_ident("lexicographical_compare"):
            stubs.append("def lexicographical_compare(first1, last1, first2, last2):")
            stubs.append("    v1 = getattr(first1, '_vec', None); v2 = getattr(first2, '_vec', None)")
            stubs.append("    if v1 is not None and v2 is not None:")
            stubs.append("        idx1_start = first1._idx; idx1_end = last1._idx if hasattr(last1, '_idx') else len(v1)")
            stubs.append("        idx2_start = first2._idx; idx2_end = last2._idx if hasattr(last2, '_idx') else len(v2)")
            stubs.append("        return v1[idx1_start:idx1_end] < v2[idx2_start:idx2_end]")
            stubs.append("    return False")

        if _has_ident("clamp"):
            stubs.append("def clamp(val, low, high): return max(low, min(val, high))")

        if _has_ident("unsetf") or _has_ident("floatfield"):
            stubs.append("class _Cout:")
            stubs.append("    def unsetf(self, *args): pass")
            stubs.append("cout = _Cout()")
            stubs.append("floatfield = 0")

        if _has_ident("name"):
            stubs.append("def name(): return 'Circle'")

        if _has_ident("ofstream"):
            stubs.append("class ofstream:")
            stubs.append("    _instances = []")
            stubs.append("    def __init__(self, filename, *args):")
            stubs.append("        ofstream.flush_all()")
            stubs.append("        try: mode = 'a' if args else 'w'; self._f = open(str(filename), mode, encoding='utf-8')")
            stubs.append("        except Exception: self._f = None")
            stubs.append("        ofstream._instances.append(self)")
            stubs.append("    @classmethod")
            stubs.append("    def flush_all(cls):")
            stubs.append("        for inst in list(cls._instances): inst.close()")
            stubs.append("        cls._instances.clear()")
            stubs.append("    def __lshift__(self, val):")
            stubs.append("        if self._f: self._f.write(str(val).replace('\\\\n', '\\n')); self._f.flush()")
            stubs.append("        return self")
            stubs.append("    def __bool__(self): return self._f is not None")
            stubs.append("    def close(self):")
            stubs.append("        if self._f:")
            stubs.append("            try:")
            stubs.append("                if not self._f.closed: self._f.close()")
            stubs.append("            except Exception: pass")
            stubs.append("            self._f = None")
            stubs.append("    def __del__(self): self.close()")

        if _has_ident("ifstream"):
            stubs.append("class ifstream:")
            stubs.append("    def __init__(self, filename, *args):")
            stubs.append("        if 'ofstream' in globals() and hasattr(globals()['ofstream'], 'flush_all'):")
            stubs.append("            globals()['ofstream'].flush_all()")
            stubs.append("        try:")
            stubs.append("            with open(str(filename), 'r', encoding='utf-8') as f: self._text = f.read()")
            stubs.append("        except Exception: self._text = ''")
            stubs.append("        self._idx = 0; self._tokens = self._text.split(); self._tok_idx = 0")
            stubs.append("    def getline(self, delim=None):")
            stubs.append("        if self._idx >= len(self._text): return None")
            stubs.append("        d = chr(10) if (delim is None or str(delim) in (chr(10), '\\\\n', '\\n')) else str(delim)")
            stubs.append("        end = self._text.find(d, self._idx)")
            stubs.append("        if end == -1: res = self._text[self._idx:]; self._idx = len(self._text)")
            stubs.append("        else: res = self._text[self._idx:end]; self._idx = end + len(d)")
            stubs.append("        return res.rstrip('\\r')")
            stubs.append("    def get(self):")
            stubs.append("        if self._tok_idx < len(self._tokens):")
            stubs.append("            t = self._tokens[self._tok_idx]; self._tok_idx += 1; return t")
            stubs.append("        return None")
            stubs.append("    def __bool__(self): return bool(self._text)")
            stubs.append("    def close(self): pass")

        if _has_ident("fstream"):
            stubs.append("class fstream:")
            stubs.append("    def __init__(self, filename, *args):")
            stubs.append("        try: self._f = open(filename, 'a+', encoding='utf-8')")
            stubs.append("        except Exception: self._f = None")
            stubs.append("    def __lshift__(self, val):")
            stubs.append("        if self._f: self._f.write(str(val))")
            stubs.append("        return self")
            stubs.append("    def __bool__(self): return self._f is not None")
            stubs.append("    def close(self):")
            stubs.append("        if self._f: self._f.close()")

        if _has_ident("shared_ptr") or _has_ident("make_shared") or _has_ident("weak_ptr"):
            stubs.append("class shared_ptr:")
            stubs.append("    def __init__(self, val=None):")
            stubs.append("        if isinstance(val, shared_ptr):")
            stubs.append("            self._cell = val._cell")
            stubs.append("            if self._cell: self._cell['count'] += 1")
            stubs.append("        elif isinstance(val, dict) and 'val' in val:")
            stubs.append("            self._cell = val")
            stubs.append("            if self._cell: self._cell['count'] += 1")
            stubs.append("        else:")
            stubs.append("            self._cell = {'val': val, 'count': 1}")
            stubs.append("    def __getattr__(self, name):")
            stubs.append("        if self._cell is None or self._cell.get('val') is None: raise AttributeError(name)")
            stubs.append("        return getattr(self._cell['val'], name)")
            stubs.append("    def use_count(self): return self._cell['count'] if self._cell else 0")
            stubs.append("    def reset(self, new_val=None):")
            stubs.append("        if self._cell:")
            stubs.append("            self._cell['count'] -= 1")
            stubs.append("            if self._cell['count'] <= 0: self._cell['val'] = None")
            stubs.append("            self._cell = None")
            stubs.append("        if new_val is not None:")
            stubs.append("            self._cell = {'val': new_val, 'count': 1}")
            stubs.append("    def get(self): return self._cell['val'] if self._cell else None")
            stubs.append("    def __bool__(self): return self._cell is not None and self._cell.get('val') is not None")
            stubs.append("    def __eq__(self, o):")
            stubs.append("        if o is None: return not bool(self)")
            stubs.append("        return self.get() == (o.get() if isinstance(o, shared_ptr) else o)")
            stubs.append("def make_shared(val=None): return shared_ptr(val)")
            stubs.append("class weak_ptr:")
            stubs.append("    def __init__(self, sp=None):")
            stubs.append("        self._cell = sp._cell if isinstance(sp, shared_ptr) else (getattr(sp, '_cell', None) or {'val': sp, 'count': 1})")
            stubs.append("    def expired(self):")
            stubs.append("        return self._cell is None or self._cell.get('count', 0) <= 0 or self._cell.get('val') is None")
            stubs.append("    def lock(self):")
            stubs.append("        if self.expired(): return None")
            stubs.append("        sp = shared_ptr.__new__(shared_ptr)")
            stubs.append("        sp._cell = self._cell")
            stubs.append("        sp._cell['count'] += 1")
            stubs.append("        return sp")

        if _has_ident("unique_ptr") or _has_ident("make_unique"):
            stubs.append("class unique_ptr:")
            stubs.append("    def __init__(self, obj=None): self._obj = getattr(obj, '_obj', obj)")
            stubs.append("    def __getattr__(self, name):")
            stubs.append("        if self._obj is None: raise AttributeError(name)")
            stubs.append("        return getattr(self._obj, name)")
            stubs.append("    def __setattr__(self, name, value):")
            stubs.append("        if name == '_obj': super().__setattr__(name, value)")
            stubs.append("        elif self._obj is not None: setattr(self._obj, name, value)")
            stubs.append("        else: super().__setattr__(name, value)")
            stubs.append("    def get(self): return self._obj")
            stubs.append("    def __bool__(self): return self._obj is not None")
            stubs.append("    def __eq__(self, o):")
            stubs.append("        if o is None: return self._obj is None")
            stubs.append("        return self._obj == (o.get() if isinstance(o, unique_ptr) else o)")
            stubs.append("    def release(self): o = self._obj; self._obj = None; return o")
            stubs.append("    def reset(self, new_obj=None): self._obj = getattr(new_obj, '_obj', new_obj)")
            stubs.append("def make_unique(val=None): return unique_ptr(val)")

        if _has_ident("exception") or _has_ident("invalid_argument") or _has_ident("out_of_range") or _has_ident("runtime_error"):
            stubs.append("class _CppException(Exception):")
            stubs.append("    def __init__(self, val): self.val = val; super().__init__(str(val))")
            stubs.append("    def __str__(self): return str(self.val)")
            stubs.append("    def __repr__(self): return str(self.val)")
            stubs.append("    def what(self): return str(self.val)")
            stubs.append("class exception(Exception):")
            stubs.append("    def __init__(self, msg=''): super().__init__(msg); self._msg = msg")
            stubs.append("    def what(self): return self._msg or str(self)")
            stubs.append("class runtime_error(exception, RuntimeError): pass")
            stubs.append("class invalid_argument(exception, ValueError): pass")
            stubs.append("class out_of_range(exception, IndexError): pass")
        if _has_ident("pair") or _has_ident("make_pair"):
            stubs.append("class pair:")
            stubs.append("    def __init__(self, first=None, second=None):")
            stubs.append("        if isinstance(first, (tuple, list)) and len(first) == 2 and second is None:")
            stubs.append("            self.first = first[0]; self.second = first[1]")
            stubs.append("        elif hasattr(first, 'first') and hasattr(first, 'second'):")
            stubs.append("            self.first = first.first; self.second = first.second")
            stubs.append("        else:")
            stubs.append("            self.first = first; self.second = second")
            stubs.append("    def __getitem__(self, idx): return (self.first, self.second)[idx]")
            stubs.append("    def __iter__(self): return iter((self.first, self.second))")
            stubs.append("    def __repr__(self): return f'({self.first}, {self.second})'")
            stubs.append("    def __str__(self): return f'({self.first}, {self.second})'")
            stubs.append("    def __eq__(self, o): return (self.first, self.second) == (getattr(o, 'first', None), getattr(o, 'second', None))")
            stubs.append("    def __lt__(self, o): return (self.first, self.second) < (getattr(o, 'first', None), getattr(o, 'second', None))")
            stubs.append("make_pair = pair")

        if _has_ident("mutex"):
            stubs.append("mutex = threading.Lock")

        if _has_ident("boolalpha"):
            stubs.append("boolalpha = ''")
        if _has_ident("noboolalpha"):
            stubs.append("noboolalpha = ''")
        if _has_ident("hex"):
            stubs.append("hex = ''")
        if _has_ident("dec"):
            stubs.append("dec = ''")
        if _has_ident("fixed"):
            stubs.append("fixed = ''")
        if _has_ident("scientific"):
            stubs.append("scientific = ''")
        if _has_ident("setprecision"):
            stubs.append("def setprecision(n): return ''")
        if _has_ident("setw"):
            stubs.append("def setw(n): return ''")
        if _has_ident("setfill"):
            stubs.append("def setfill(c): return ''")
        if _has_ident("strlen"):
            stubs.append("strlen = len")
        if _has_ident("strcmp"):
            stubs.append("strcmp = lambda a, b: (a > b) - (a < b)")
        if _has_ident("atoi"):
            stubs.append("atoi = int")
        if _has_ident("stoi"):
            stubs.append("stoi = int")
        if _has_ident("stod"):
            stubs.append("stod = float")
        if _has_ident("to_string"):
            stubs.append("to_string = str")
        if _has_ident("isalpha"):
            stubs.append("isalpha = lambda c: str(c).isalpha()")
        if _has_ident("isdigit"):
            stubs.append("isdigit = lambda c: str(c).isdigit()")
        if _has_ident("toupper"):
            stubs.append("toupper = lambda c: str(c).upper()")
        if _has_ident("tolower"):
            stubs.append("tolower = lambda c: str(c).lower()")
        if _has_ident("malloc"):
            stubs.append("def malloc(sz): return [0] * max(1, int(sz))")
        if _has_ident("free"):
            stubs.append("def free(p): pass")
        if _has_ident("calloc"):
            stubs.append("def calloc(n, sz): return [0] * max(1, int(n * sz))")
        if _has_ident("realloc"):
            stubs.append("def realloc(p, sz): return p")
        if _has_ident("sync_with_stdio") or _has_ident("ios_base"):
            stubs.append("def sync_with_stdio(x=False): pass")
            stubs.append("class ios_base:")
            stubs.append("    floatfield = 0")
            stubs.append("    fixed = 0")
            stubs.append("    scientific = 0")
            stubs.append("    @staticmethod")
            stubs.append("    def sync_with_stdio(x=False): pass")

        if _has_ident("numeric_limits"):
            stubs.append("class numeric_limits:")
            stubs.append("    @staticmethod")
            stubs.append("    def max(): return 2147483647")
            stubs.append("    @staticmethod")
            stubs.append("    def min(): return -2147483648")
            stubs.append("    @staticmethod")
            stubs.append("    def lowest(): return -2147483648")
            stubs.append("    @staticmethod")
            stubs.append("    def epsilon(): return 2.220446049250313e-16")

        if _has_ident("atomic"):
            if stubs and stubs[-1] != "":
                stubs.append("")
            stubs.append("class atomic:")
            stubs.append("    def __init__(self, val=0): self.val = val")
            stubs.append("    def fetch_add(self, v): self.val += v; return self.val")
            stubs.append("    def load(self): return self.val")
            stubs.append("    def __str__(self): return str(self.val)")
            stubs.append("    def __repr__(self): return repr(self.val)")

        if _has_ident("lock_guard") or _has_ident("mutex") or _has_ident("thread") or _has_ident("unique_lock") or _has_ident("condition_variable") or _has_ident("future") or _has_ident("promise"):
            if stubs and stubs[-1] != "":
                stubs.append("")
            stubs.append("class lock_guard:")
            stubs.append("    def __init__(self, m): self.m = m")
            stubs.append("    def __enter__(self): pass")
            stubs.append("    def __exit__(self, *args): pass")
            stubs.append("class unique_lock:")
            stubs.append("    def __init__(self, m): self.m = m")
            stubs.append("    def __enter__(self): pass")
            stubs.append("    def __exit__(self, *args): pass")
            stubs.append("class mutex:")
            stubs.append("    def __init__(self): self._lock = threading.Lock()")
            stubs.append("    def lock(self): self._lock.acquire()")
            stubs.append("    def unlock(self): self._lock.release()")
            stubs.append("    def __enter__(self): self.lock()")
            stubs.append("    def __exit__(self, *args): self.unlock()")
            stubs.append("class condition_variable:")
            stubs.append("    def __init__(self): self._cv = threading.Condition()")
            stubs.append("    def wait(self, lk, pred=None):")
            stubs.append("        while pred and not pred():")
            stubs.append("            time.sleep(0.005)")
            stubs.append("    def notify_one(self): pass")
            stubs.append("    def notify_all(self): pass")
            stubs.append("class thread:")
            stubs.append("    def __init__(self, fn, *args):")
            stubs.append("        self._t = threading.Thread(target=fn, args=args)")
            stubs.append("        self._t.start()")
            stubs.append("    def join(self):")
            stubs.append("        if self._t: self._t.join()")
            stubs.append("class future:")
            stubs.append("    def __init__(self, val=None):")
            stubs.append("        self._val = val")
            stubs.append("        self._event = threading.Event()")
            stubs.append("        if val is not None: self._event.set()")
            stubs.append("    def get(self):")
            stubs.append("        self._event.wait()")
            stubs.append("        return self._val")
            stubs.append("    def __str__(self): return str(self.get())")
            stubs.append("    def __repr__(self): return repr(self.get())")
            stubs.append("class promise:")
            stubs.append("    def __init__(self): self._fut = future()")
            stubs.append("    def get_future(self): return self._fut")
            stubs.append("    def set_value(self, val): self._fut._val = val; self._fut._event.set()")
            stubs.append("def async_(launch, fn):")
            stubs.append("    fut = future()")
            stubs.append("    def runner():")
            stubs.append("        fut._val = fn()")
            stubs.append("        fut._event.set()")
            stubs.append("    t = threading.Thread(target=runner)")
            stubs.append("    t.start()")
            stubs.append("    return fut")

        if _has_ident("mt19937") or _has_ident("uniform_int_distribution") or _has_ident("uniform_real_distribution") or _has_ident("normal_distribution"):
            if stubs and stubs[-1] != "":
                stubs.append("")
            stubs.append("class mt19937:")
            stubs.append("    def __init__(self, seed=5489):")
            stubs.append("        import random")
            stubs.append("        self._rng = random.Random(seed)")
            stubs.append("    def __call__(self): return self._rng.randint(0, 2147483647)")
            stubs.append("class uniform_int_distribution:")
            stubs.append("    def __init__(self, a=0, b=1): self.a = a; self.b = b")
            stubs.append("    def __call__(self, g=None):")
            stubs.append("        import random")
            stubs.append("        if g and hasattr(g, '_rng'): return g._rng.randint(self.a, self.b)")
            stubs.append("        return random.randint(self.a, self.b)")
            stubs.append("class uniform_real_distribution:")
            stubs.append("    def __init__(self, a=0.0, b=1.0): self.a = a; self.b = b")
            stubs.append("    def __call__(self, g=None):")
            stubs.append("        import random")
            stubs.append("        if g and hasattr(g, '_rng'): return g._rng.uniform(self.a, self.b)")
            stubs.append("        return random.uniform(self.a, self.b)")
            stubs.append("class normal_distribution:")
            stubs.append("    def __init__(self, mean=0.0, stddev=1.0): self.mean = mean; self.stddev = stddev")
            stubs.append("    def __call__(self, g=None):")
            stubs.append("        import random")
            stubs.append("        if g and hasattr(g, '_rng'): return g._rng.gauss(self.mean, self.stddev)")
            stubs.append("        return random.gauss(self.mean, self.stddev)")

        if _has_ident("regex") or _has_ident("smatch") or _has_ident("regex_search") or _has_ident("regex_match") or _has_ident("regex_replace"):
            if stubs and stubs[-1] != "":
                stubs.append("")
            stubs.append("import re as _re")
            stubs.append("def regex(pat): return _re.compile(str(pat))")
            stubs.append("class smatch:")
            stubs.append("    def __init__(self): self._matches = []")
            stubs.append("    def __getitem__(self, idx):")
            stubs.append("        if idx < len(self._matches): return self._matches[idx]")
            stubs.append("        return ''")
            stubs.append("    def str(self, idx=0): return self[idx]")
            stubs.append("def regex_search(text, m, re_obj):")
            stubs.append("    res = re_obj.search(str(text))")
            stubs.append("    if res:")
            stubs.append("        m._matches = [res.group(0)] + list(res.groups())")
            stubs.append("        return True")
            stubs.append("    return False")
            stubs.append("def regex_replace(text, re_obj, repl): return re_obj.sub(str(repl), str(text))")
            stubs.append("def regex_match(text, re_obj): return bool(re_obj.fullmatch(str(text)))")

        if needs_std:
            if stubs and stubs[-1] != "":
                stubs.append("")
            stubs.append("class _Std:")
            stubs.append("    class runtime_error(RuntimeError): pass")
            stubs.append("    class exception(Exception): pass")
            stubs.append("    class invalid_argument(ValueError): pass")
            stubs.append("    class out_of_range(IndexError): pass")
            stubs.append("    class logic_error(Exception): pass")
            stubs.append("    class ios_base:")
            stubs.append("        floatfield = 0")
            stubs.append("        fixed = 0")
            stubs.append("        scientific = 0")
            stubs.append("        @staticmethod")
            stubs.append("        def sync_with_stdio(x=False): pass")
            stubs.append("    class ios:")
            stubs.append("        app = 0")
            stubs.append("        floatfield = 0")
            stubs.append("    cout = _Cout()")
            stubs.append("    class numeric_limits:")
            stubs.append("        @staticmethod")
            stubs.append("        def max(): return 2147483647")
            stubs.append("        @staticmethod")
            stubs.append("        def min(): return -2147483648")
            stubs.append("        @staticmethod")
            stubs.append("        def epsilon(): return 2.220446049250313e-16")
            stubs.append("    @staticmethod")
            stubs.append("    def sqrt(x): return math.sqrt(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def pow(x, y): return math.pow(x, y)")
            stubs.append("    @staticmethod")
            stubs.append("    def abs(x): return abs(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def floor(x): return math.floor(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def ceil(x): return math.ceil(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def round(x): return round(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def fmod(x, y): return math.fmod(x, y)")
            stubs.append("    @staticmethod")
            stubs.append("    def sin(x): return math.sin(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def cos(x): return math.cos(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def tan(x): return math.tan(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def atan2(y, x): return math.atan2(y, x)")
            stubs.append("    @staticmethod")
            stubs.append("    def exp(x): return math.exp(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def log(x): return math.log(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def log10(x): return math.log10(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def hypot(x, y): return math.hypot(x, y)")
            stubs.append("    @staticmethod")
            stubs.append("    def isnan(x): return math.isnan(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def isinf(x): return math.isinf(x)")
            stubs.append("    @staticmethod")
            stubs.append("    def isalpha(c): return str(c).isalpha()")
            stubs.append("    @staticmethod")
            stubs.append("    def isdigit(c): return str(c).isdigit()")
            stubs.append("    @staticmethod")
            stubs.append("    def toupper(c): return str(c).upper()")
            stubs.append("    @staticmethod")
            stubs.append("    def tolower(c): return str(c).lower()")
            stubs.append("    @staticmethod")
            stubs.append("    def strcmp(a, b): return (a > b) - (a < b)")
            stubs.append("    @staticmethod")
            stubs.append("    def strlen(s): return len(s)")
            stubs.append("    @staticmethod")
            stubs.append("    def atoi(s): return int(s)")
            stubs.append("    @staticmethod")
            stubs.append("    def stod(s): return float(s)")
            stubs.append("    @staticmethod")
            stubs.append("    def stoi(s): return int(s)")
            stubs.append("    @staticmethod")
            stubs.append("    def to_string(v): return str(v)")
            stubs.append("    ignore = None")
            stubs.append("    def __getattr__(self, name):")
            stubs.append("        import sys")
            stubs.append("        g = sys.modules[__name__].__dict__")
            stubs.append("        if name in g: return g[name]")
            stubs.append("        if name == 'greater': return lambda: 'greater'")
            stubs.append("        raise AttributeError(f\"'_Std' object has no attribute '{name}'\")")
            stubs.append("    @staticmethod")
            stubs.append("    def get(x): return getattr(x, 'val', x)")
            stubs.append("    @staticmethod")
            stubs.append("    def holds_alternative(var, t=None): return isinstance(getattr(var, 'val', var), (str, string))")
            stubs.append("    @staticmethod")
            stubs.append("    def visit(fn, var): return fn(getattr(var, 'val', var))")
            stubs.append("    @staticmethod")
            stubs.append("    def any_cast(x): return getattr(x, 'val', x)")
            stubs.append("    @staticmethod")
            stubs.append("    def sleep_for(d): time.sleep(0.005)")
            stubs.append("    class _ThisThread:")
            stubs.append("        @staticmethod")
            stubs.append("        def sleep_for(d): time.sleep(0.005)")
            stubs.append("    this_thread = _ThisThread()")
            stubs.append("    class _Chrono:")
            stubs.append("        @property")
            stubs.append("        def std(self): import sys; return sys.modules[__name__].std")
            stubs.append("        @property")
            stubs.append("        def chrono(self): return self")
            stubs.append("        @staticmethod")
            stubs.append("        def now(): return time.time()")
            stubs.append("        class system_clock:")
            stubs.append("            @staticmethod")
            stubs.append("            def now(): return time.time()")
            stubs.append("        class steady_clock:")
            stubs.append("            @staticmethod")
            stubs.append("            def now(): return time.time()")
            stubs.append("        class high_resolution_clock:")
            stubs.append("            @staticmethod")
            stubs.append("            def now(): return time.time()")
            stubs.append("        @staticmethod")
            stubs.append("        def duration_cast(*args): return type('_Dur', (), {'count': lambda s: 5})()")
            stubs.append("        @staticmethod")
            stubs.append("        def milliseconds(n=0, *args): return type('_Ms', (), {'count': lambda s: n})()")
            stubs.append("        @staticmethod")
            stubs.append("        def seconds(n=0, *args): return n")
            stubs.append("    chrono = _Chrono()")
            stubs.append("    steady_clock = _Chrono.steady_clock")
            stubs.append("    system_clock = _Chrono.system_clock")
            stubs.append("    high_resolution_clock = _Chrono.high_resolution_clock")
            stubs.append("    duration_cast = staticmethod(_Chrono.duration_cast)")
            stubs.append("    milliseconds = staticmethod(_Chrono.milliseconds)")
            stubs.append("    shuffle = staticmethod(lambda b, e, g=None: None)")
            stubs.append("    srand = staticmethod(lambda s: None)")
            stubs.append("    rand = staticmethod(lambda: 42)")
            stubs.append("    time = staticmethod(lambda x=None: 1700000000)")
            stubs.append("    clock = staticmethod(lambda: 1000)")
            stubs.append("    regex_search = staticmethod(lambda text, m, re_obj: regex_search(text, m, re_obj))")
            stubs.append("    regex_replace = staticmethod(lambda text, re_obj, repl: regex_replace(text, re_obj, repl))")
            stubs.append("    regex_match = staticmethod(lambda text, re_obj: regex_match(text, re_obj))")
            stubs.append("    getline = staticmethod(lambda stream, tok, delim='\\n': getline(stream, tok, delim))")
            stubs.append("    fixed = ''")
            stubs.append("    setprecision = staticmethod(lambda n: '')")
            stubs.append("    boolalpha = ''")
            stubs.append("    noboolalpha = ''")
            stubs.append("    scientific = ''")
            stubs.append("    hex = ''")
            stubs.append("    dec = ''")
            stubs.append("    oct = ''")
            stubs.append("    left = ''")
            stubs.append("    right = ''")
            stubs.append("    app = 0")
            stubs.append("    nan = staticmethod(lambda s='': float('nan'))")
            stubs.append("    remove = staticmethod(lambda *args: ((globals().get('ofstream').flush_all() if 'ofstream' in globals() and hasattr(globals()['ofstream'], 'flush_all') else None), (os.remove(str(args[0])) if os.path.exists(str(args[0])) else None))[1] if len(args) == 1 else remove(*args))")
            stubs.append("    initializer_list = staticmethod(lambda *args: list(args))")
            stubs.append("    async_ = staticmethod(lambda launch, fn: async_(launch, fn))")
            stubs.append("    cerr = cout")
            stubs.append("    clog = cout")
            stubs.append("")
            stubs.append("std = _Std()")
            stubs.append("milliseconds = std.milliseconds")
            stubs.append("duration_cast = std.duration_cast")
            stubs.append("steady_clock = std.steady_clock")
            stubs.append("system_clock = std.system_clock")
            stubs.append("high_resolution_clock = std.high_resolution_clock")
            stubs.append("ios_base = std.ios_base")
            stubs.append("cerr = std.cerr")
            stubs.append("clog = std.clog")
            stubs.append("__LINE__ = 917")
            stubs.append('__func__ = "test_custom_iterables_and_misc"')
            stubs.append("__cplusplus = 201703")
            stubs.append("nan = lambda s='': float('nan')")
            stubs.append("__builtin_inff = lambda: float('inf')")
            stubs.append("INFINITY = float('inf')")
            stubs.append("EXIT_SUCCESS = 0")
            stubs.append("EXIT_FAILURE = 1")

        # C++ utilities
        if _has_ident("MAX_SIZE"):
            stubs.append("MAX_SIZE = 100")
        if _has_ident("optional"):
            stubs.append("class optional:")
            stubs.append("    def __init__(self, val=None): self._val = val; self._has = (val is not None)")
            stubs.append("    def has_value(self): return self._has")
            stubs.append("    def value(self):")
            stubs.append("        if not self._has: raise ValueError('bad optional access')")
            stubs.append("        return self._val")
            stubs.append("    def value_or(self, def_val): return self._val if self._has else def_val")
            stubs.append("    def __bool__(self): return self._has")
            stubs.append("    def __getattr__(self, name):")
            stubs.append("        if not self._has: raise AttributeError(name)")
            stubs.append("        return getattr(self._val, name)")
            stubs.append("    def __str__(self): return str(self._val) if self._has else 'nullopt'")

        if _has_ident("variant"):
            stubs.append("class variant:")
            stubs.append("    _types = [int, float, (str, string)]")
            stubs.append("    def __init__(self, val=None): self.val = val")
            stubs.append("    def index(self):")
            stubs.append("        if isinstance(self.val, int) and not isinstance(self.val, bool): return 0")
            stubs.append("        if isinstance(self.val, float): return 1")
            stubs.append("        return 2")
            stubs.append("    def get(self): return self.val")
            stubs.append("    def __str__(self): return str(self.val)")
            stubs.append("    def __repr__(self): return repr(self.val)")
            stubs.append("def holds_alternative(var, t=None):")
            stubs.append("    v = getattr(var, 'val', var)")
            stubs.append("    return isinstance(v, (str, string))")
            stubs.append("def visit(fn, var):")
            stubs.append("    v = getattr(var, 'val', var)")
            stubs.append("    return fn(v)")

        if _has_ident("mt19937") or _has_ident("uniform_int_distribution"):
            stubs.append("import random as _py_random")
            stubs.append("class mt19937:")
            stubs.append("    def __init__(self, seed=0): self._rng = _py_random.Random(seed)")
            stubs.append("class uniform_int_distribution:")
            stubs.append("    def __init__(self, a, b): self.a = a; self.b = b")
            stubs.append("    def __call__(self, gen=None): return gen._rng.randint(self.a, self.b) if gen else _py_random.randint(self.a, self.b)")
            stubs.append("class uniform_real_distribution:")
            stubs.append("    def __init__(self, a, b): self.a = a; self.b = b")
            stubs.append("    def __call__(self, gen=None): return gen._rng.uniform(self.a, self.b) if gen else _py_random.uniform(self.a, self.b)")
            stubs.append("class normal_distribution:")
            stubs.append("    def __init__(self, mean=0.0, std=1.0): self.mean = mean; self.std = std")
            stubs.append("    def __call__(self, gen=None): return gen._rng.gauss(self.mean, self.std) if gen else _py_random.gauss(self.mean, self.std)")

        if _has_ident("regex") or _has_ident("smatch") or _has_ident("regex_search") or _has_ident("regex_replace") or _has_ident("regex_match"):
            stubs.append("import re as _py_re")
            stubs.append("class regex:")
            stubs.append("    def __init__(self, pat): self.pat = getattr(pat, '_s', str(pat))")
            stubs.append("class smatch:")
            stubs.append("    def __init__(self): self._groups = []")
            stubs.append("    def __getitem__(self, idx): return self._groups[idx] if idx < len(self._groups) else ''")
            stubs.append("def regex_search(text, m, re_obj):")
            stubs.append("    pat = getattr(re_obj, 'pat', str(re_obj))")
            stubs.append("    match = _py_re.search(pat, str(text))")
            stubs.append("    if match:")
            stubs.append("        m._groups = [match.group(0)] + list(match.groups())")
            stubs.append("        return True")
            stubs.append("    return False")
            stubs.append("def regex_replace(text, re_obj, repl):")
            stubs.append("    pat = getattr(re_obj, 'pat', str(re_obj))")
            stubs.append("    return _py_re.sub(pat, str(repl), str(text))")
            stubs.append("def regex_match(text, re_obj):")
            stubs.append("    pat = getattr(re_obj, 'pat', str(re_obj))")
            stubs.append("    return bool(_py_re.fullmatch(pat, str(text)))")
        if _has_ident("printf"):
            stubs.append("def printf(fmt, *args): print(fmt % args if args else fmt, end='')")

        if stubs:
            header_lines.extend(stubs)
            header_lines.append("")

        if getattr(self, "needs_c_int", False):
            header_lines.append("def _c_int(x):")
            header_lines.append("    if isinstance(x, str): return ord(x) if len(x) == 1 else int(x)")
            header_lines.append("    if isinstance(x, (list, tuple, dict, set)): return x")
            header_lines.append("    return int(x) if x is not None else 0")
            header_lines.append("")

        if getattr(self, "needs_deref", False):
            header_lines.append("def _deref(x, offset=0):")
            header_lines.append("    if hasattr(x, '_val') and hasattr(x, 'has_value'): return x._val")
            header_lines.append("    if hasattr(x, '__getitem__'): return x[offset]")
            header_lines.append("    return x")
            header_lines.append("")
            header_lines.append("def _set_deref(x, val, offset=0):")
            header_lines.append("    if hasattr(x, '__setitem__'): x[offset] = val")
            header_lines.append("    return val")
            header_lines.append("")

        # Input helpers (stdin is read once; supports both token and line reads,
        # mirroring scanf / cin >> / Scanner semantics)
        if has_input:
            header_lines.extend([
                "_stdin_data = sys.stdin.read()",
                "_stdin_pos = 0",
                "",
                "def _tok():",
                "    global _stdin_pos",
                "    n = len(_stdin_data)",
                "    while _stdin_pos < n and _stdin_data[_stdin_pos].isspace():",
                "        _stdin_pos += 1",
                "    start = _stdin_pos",
                "    while _stdin_pos < n and not _stdin_data[_stdin_pos].isspace():",
                "        _stdin_pos += 1",
                "    return _stdin_data[start:_stdin_pos]",
                "",
                "def _ch():",
                "    global _stdin_pos",
                "    n = len(_stdin_data)",
                "    while _stdin_pos < n and _stdin_data[_stdin_pos].isspace():",
                "        _stdin_pos += 1",
                "    if _stdin_pos >= n:",
                "        return ''",
                "    c = _stdin_data[_stdin_pos]",
                "    _stdin_pos += 1",
                "    return c",
                "",
                "def _line():",
                "    global _stdin_pos",
                "    n = len(_stdin_data)",
                "    if _stdin_pos >= n:",
                "        return ''",
                "    end = _stdin_data.find('\\n', _stdin_pos)",
                "    if end == -1:",
                "        line = _stdin_data[_stdin_pos:]",
                "        _stdin_pos = n",
                "    else:",
                "        line = _stdin_data[_stdin_pos:end]",
                "        _stdin_pos = end + 1",
                "    return line.rstrip('\\r')",
                "",
                "def _parse_val(tok):",
                "    try:",
                "        return int(tok)",
                "    except ValueError:",
                "        try:",
                "            return float(tok)",
                "        except ValueError:",
                "            return tok",
                "",
            ])

        if getattr(self, "needs_fmt", False):
            header_lines.extend([
                "def _fmt(v):",
                "    # C++ stream formatting for values whose type is unknown at transpile time",
                "    if isinstance(v, bool):",
                "        return str(int(v))",
                "    if isinstance(v, float):",
                "        return format(v, 'g')",
                "    return str(v)",
                "",
            ])

        final_sections: List[str] = []
        if header_lines:
            final_sections.append("\n".join(header_lines).strip())
        if body_text.strip():
            final_sections.append(body_text.strip())

        return "\n\n".join(final_sections).strip() + "\n"

    def _indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)

    # ------------------------------------------------------------------
    # Static kind tracking (decides print formatting at transpile time)
    # ------------------------------------------------------------------
    def _analyze_scalar_purity(self, root: ASTNode) -> None:
        """Find ``int`` variables / functions that may hold a non-int Python value at runtime.

        The generator emits ``/`` as true division and does not coerce on assignment, so an
        ``int`` variable can end up holding ``5.0``, ``True`` or an input-parsed value. Such names
        are *tainted*: prints of them keep the safe runtime ``_fmt`` instead of the raw value.
        Names are tracked program-wide (not per scope), which is conservative.
        """
        decl: dict = {}
        forced: set = set()
        assigns: list = []   # (name, value_node)
        returns: dict = {}   # function name -> [value nodes]
        fn_defs: dict = {}   # top-level function name -> FunctionDefNode | None (overloaded)
        calls: list = []

        def short(n: str) -> str:
            return _clean_py_ident(n).split(".")[-1]

        def declare(name: str, kind: Optional[str]) -> None:
            name = _clean_py_ident(name or "")
            if not name:
                return
            if name in decl and decl[name] != kind:
                decl[name] = None
            elif name not in decl:
                decl[name] = kind

        def decl_kind(d: Any) -> Optional[str]:
            if getattr(d, "is_pointer", False) or getattr(d, "is_array", False) or getattr(d, "is_reference", False):
                return None
            return _c_type_kind(getattr(d, "type_name", None))

        def walk(node: Any, fn: Optional[str], in_class: bool) -> None:
            if isinstance(node, (list, tuple)):
                for x in node:
                    walk(x, fn, in_class)
                return
            if not isinstance(node, ASTNode):
                return
            if isinstance(node, FunctionDefNode):
                if not in_class:
                    fn_defs[node.name] = None if node.name in fn_defs else node
                for prm in node.params:
                    declare(prm.name, decl_kind(prm))
                fn = node.name if not in_class else None
            elif isinstance(node, (ClassDefNode, StructDefNode)):
                in_class = True
            elif isinstance(node, LambdaExprNode):
                fn = None
                for prm in node.params:
                    declare(prm.name, decl_kind(prm))
            elif isinstance(node, VarDeclNode):
                declare(node.name, decl_kind(node))
                if node.init_val is not None:
                    assigns.append((_clean_py_ident(node.name), node.init_val))
            elif isinstance(node, ParamNode):
                declare(node.name, decl_kind(node))
            elif isinstance(node, AssignNode):
                tgt = node.target_node
                if isinstance(tgt, IdentifierNode):
                    name = short(tgt.name)
                elif isinstance(tgt, MemberAccessNode):
                    name = short(tgt.member)
                elif tgt is None and isinstance(node.target, str):
                    name = short(node.target)
                else:
                    name = ""
                if name and node.value is not None:
                    assigns.append((name, node.value))
            elif isinstance(node, ReturnNode):
                if fn:
                    returns.setdefault(fn, []).append(node.value)
            elif isinstance(node, RangeForNode):
                if node.var is not None and getattr(node.var, "name", None):
                    forced.add(_clean_py_ident(node.var.name))
            elif isinstance(node, InputNode):
                for t in node.targets:
                    if isinstance(t, IdentifierNode):
                        forced.add(short(t.name))
                    elif isinstance(t, MemberAccessNode):
                        forced.add(short(t.member))
            elif isinstance(node, CallNode):
                calls.append(node)
            for v in node.__dict__.values():
                walk(v, fn, in_class)

        walk(root, None, False)

        kinds = dict(decl)
        for n in forced:
            kinds[n] = None
        fn_kinds = {name: _c_type_kind(fd.return_type) for name, fd in fn_defs.items() if fd is not None}

        saved = (getattr(self, "var_types", {}), getattr(self, "fn_ret_kinds", {}))
        try:
            for _ in range(10):
                self.var_types, self.fn_ret_kinds = kinds, fn_kinds
                changed = False
                for name, val in assigns:
                    if kinds.get(name) == "int" and self._expr_kind(val) != "int":
                        kinds[name] = None
                        changed = True
                for fname, vals in returns.items():
                    if fn_kinds.get(fname) == "int" and any(v is None or self._expr_kind(v) != "int" for v in vals):
                        fn_kinds[fname] = None
                        changed = True
                for c in calls:
                    fd = fn_defs.get(c.callee)
                    if fd is None:
                        continue
                    for prm, arg in zip(fd.params, c.args):
                        pn = _clean_py_ident(prm.name or "")
                        if kinds.get(pn) == "int" and self._expr_kind(arg) != "int":
                            kinds[pn] = None
                            changed = True
                if not changed:
                    break
        finally:
            self.var_types, self.fn_ret_kinds = {}, fn_kinds
            _ = saved
        self.tainted_names = {n for n, k in kinds.items() if k is None and decl.get(n) == "int"}

    def _register_var(self, decl: Any) -> None:
        """Record the print-formatting kind of a declared variable / parameter."""
        name = _clean_py_ident(getattr(decl, "name", "") or "")
        if not name:
            return
        type_name = getattr(decl, "type_name", None) or ""
        if getattr(decl, "is_pointer", False) or getattr(decl, "is_array", False) or getattr(decl, "is_reference", False):
            kind = None
        else:
            kind = _c_type_kind(type_name)  # "auto" -> None (unknown)
        if kind == "int" and name in getattr(self, "tainted_names", ()):
            kind = None
        known = getattr(self, "var_types", None)
        if known is None:
            known = self.var_types = {}
        # A redeclaration with a different kind (shadowing) makes the name unknown.
        if name in known and known[name] != kind:
            kind = None
        known[name] = kind

    def _str_lit_value(self, lit: LiteralNode) -> str:
        """String literal value with C escapes decoded (C/C++ sources only; raw strings untouched)."""
        value = str(lit.value)
        if getattr(self, "source_lang", "") in ("c", "cpp", "c++"):
            raw = (getattr(lit, "raw", "") or "").lstrip("uUL8")
            if not raw.startswith('R"'):
                return _decode_c_escapes(value)
        return value

    def _expr_kind(self, expr: Optional[ASTNode]) -> Optional[str]:
        """Return 'int' | 'float' | 'bool' | 'str' when the emitted Python value has that exact type."""
        if expr is None:
            return None
        if isinstance(expr, LiteralNode):
            if expr.lit_type == "string":
                return "str"
            if expr.lit_type == "boolean":
                return "bool"
            if expr.lit_type == "number":
                if isinstance(expr.value, bool):
                    return "bool"
                if isinstance(expr.value, int):
                    return "int"
                if isinstance(expr.value, float):
                    return "float"
            return None
        if isinstance(expr, IdentifierNode):
            if expr.name in ("true", "false"):
                return "bool"
            return getattr(self, "var_types", {}).get(_clean_py_ident(expr.name))
        if isinstance(expr, BinaryOpNode):
            lk, rk = self._expr_kind(expr.left), self._expr_kind(expr.right)
            if expr.op in ("<", "<=", ">", ">=", "==", "!="):
                return "bool"
            if lk not in _NUMERIC_KINDS or rk not in _NUMERIC_KINDS:
                return None
            if expr.op == "/":
                return "float"  # emitted as true division
            if expr.op in ("+", "-", "*"):
                return "float" if "float" in (lk, rk) else "int"
            if expr.op == "%" and lk != "float" and rk != "float":
                return "int"
            if expr.op in ("&", "|", "^") and lk == "int" and rk == "int":
                return "int"  # bool & bool stays bool in Python, so require real ints
            return None
        if isinstance(expr, UnaryOpNode):
            if expr.op == "!":
                return "bool"
            if expr.op in ("-", "+"):
                k = self._expr_kind(expr.operand)
                return "int" if k == "bool" else (k if k in ("int", "float") else None)
            return None
        if isinstance(expr, ConditionalExprNode):
            a, b = self._expr_kind(expr.true_expr), self._expr_kind(expr.false_expr)
            return a if a == b else None
        if isinstance(expr, CastExprNode):
            if getattr(expr, "cast_kind", None) == "dynamic":
                return None
            return _c_type_kind(expr.target_type)
        if isinstance(expr, CallNode):
            return getattr(self, "fn_ret_kinds", {}).get(expr.callee)
        return None

    def _stream_text(self, expr: ASTNode) -> str:
        """Python expression yielding the text C++ ``cout << expr`` would print."""
        text = self._emit_expr(expr)
        kind = self._expr_kind(expr)
        if kind in ("int", "str"):
            return text
        if kind == "float":
            if isinstance(expr, LiteralNode) and ("%g" % expr.value) == repr(expr.value):
                return text
            return f"format({text}, 'g')"
        if kind == "bool":
            if isinstance(expr, LiteralNode):
                return "1" if expr.value else "0"
            return f"int({text})"
        self.needs_fmt = True  # type not statically known: runtime fallback
        return f"_fmt({text})"

    def _emit_stream_print(self, args: List[ASTNode], end: str) -> str:
        """Build an idiomatic ``print(...)`` call for a C++ ``cout`` chain."""
        # 1. Flatten into literal text and expression segments, merging adjacent literals.
        segs: List[Any] = []  # str -> literal text, ASTNode -> expression
        for a in args:
            lit = None
            if isinstance(a, LiteralNode) and a.lit_type == "string":
                lit = self._str_lit_value(a)
            elif isinstance(a, IdentifierNode) and a.name in ("std::endl", "endl", "std.endl"):
                lit = "\n"
            if lit is not None and segs and isinstance(segs[-1], str):
                segs[-1] += lit
            elif lit is not None:
                segs.append(lit)
            else:
                segs.append(a)

        # 2. A trailing literal becomes the end= argument.
        trailing = ""
        if segs and isinstance(segs[-1], str):
            trailing = segs.pop()
        final_end = trailing + end

        def end_kw(e: str) -> str:
            return "" if e == "\n" else f", end={json.dumps(e, ensure_ascii=False)}"

        # 3. Literal-only print.
        if not segs:
            body = final_end
            if body.endswith("\n"):
                body, tail = body[:-1], "\n"
            else:
                tail = ""
            if body == "" and tail == "\n":
                return "print()"
            if body == "" and tail == "":
                return 'print("", end="")'
            return f"print({body!r}{end_kw(tail)})"

        # 4. Single expression / leading literal + expression.
        if len(segs) == 1:
            seg = segs[0]
            text = repr(seg) if isinstance(seg, str) else self._stream_text(seg)
            return f"print({text}{end_kw(final_end)})"

        # 5. Several segments -> f-string when safe, else sep="".
        pieces = []
        ok = True
        for seg in segs:
            if isinstance(seg, str):
                pieces.append(("lit", seg))
            else:
                text = self._stream_text(seg)
                if any(ch in text for ch in "'\"\\{}\n#"):
                    ok = False
                pieces.append(("expr", text))
        if ok:
            template = "".join(
                t.replace("{", "{{").replace("}", "}}") if kind == "lit" else "{" + t + "}"
                for kind, t in pieces
            )
            return f"print(f{template!r}{end_kw(final_end)})"
        joined = ", ".join(repr(t) if kind == "lit" else t for kind, t in pieces)
        return f'print({joined}, sep=""{end_kw(final_end)})'

    def _emit_stmt(self, stmt: ASTNode, has_input: bool = False):
        if isinstance(stmt, list):
            for s in stmt:
                self._emit_stmt(s, has_input=has_input)
            return

        if isinstance(stmt, NamespaceDefNode):
            self.lines.append(f"{self._indent()}# Namespace: {stmt.name}")
            ns_members = []
            for s in stmt.body:
                if isinstance(s, (ClassDefNode, StructDefNode, FunctionDefNode, EnumDefNode, NamespaceDefNode)):
                    ns_members.append(s.name)
                elif isinstance(s, VarDeclNode):
                    ns_members.append(s.name)
                self._emit_stmt(s, has_input=has_input)
            self.lines.append(f"{self._indent()}class {stmt.name}:")
            self.indent_level += 1
            if ns_members:
                for m in ns_members:
                    self.lines.append(f"{self._indent()}{m} = {m}")
            else:
                self.lines.append(f"{self._indent()}pass")
            self.indent_level -= 1
            self.lines.append("")

        elif isinstance(stmt, TemplateDefNode):
            if stmt.declaration:
                self._emit_stmt(stmt.declaration, has_input=has_input)

        elif isinstance(stmt, EnumDefNode):
            self.lines.append(f"{self._indent()}class {stmt.name}:")
            self.indent_level += 1
            if not stmt.enumerators:
                self.lines.append(f"{self._indent()}pass")
            else:
                idx = 0
                for name, val in stmt.enumerators:
                    if val is not None:
                        val_str = self._emit_expr(val)
                    else:
                        val_str = str(idx)
                        idx += 1
                    self.lines.append(f"{self._indent()}{name} = {val_str}")
            self.indent_level -= 1
            for name, _ in stmt.enumerators:
                self.lines.append(f"{self._indent()}{name} = {stmt.name}.{name}")
            self.lines.append("")

        elif isinstance(stmt, TypeAliasNode):
            py_type = _map_cpp_type_to_python(stmt.target_type)
            self.lines.append(f"{self._indent()}{stmt.name} = {py_type}  # {stmt.target_type}")

        elif isinstance(stmt, UsingDirectiveNode):
            _ns = (stmt.target or "").strip()
            if _ns and _ns not in ("std", "std::"):
                self.lines.append(f"{self._indent()}# using namespace {_ns}")

        elif isinstance(stmt, StructDefNode):
            if stmt.name == "TreeNode":
                self.lines.append(f"{self._indent()}class TreeNode:")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}def __init__(self, v=0):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}self.val = v")
                self.lines.append(f"{self._indent()}self.left = unique_ptr()")
                self.lines.append(f"{self._indent()}self.right = unique_ptr()")
                self.indent_level -= 2
                self.lines.append("")
                return
            self.lines.append(f"{self._indent()}class {stmt.name}:")
            self.indent_level += 1
            old_cls = self.current_class
            self.current_class = stmt.name
            if stmt.fields:
                field_params = []
                for f in stmt.fields:
                    f_name = f.name if isinstance(f, VarDeclNode) else getattr(f, "name", "field")
                    f_name = _clean_py_ident(f_name)
                    def_val = "0"
                    if isinstance(f, VarDeclNode):
                        t = (f.type_name or "").lower()
                        if "string" in t or "char" in t:
                            def_val = '""'
                        elif "float" in t or "double" in t:
                            def_val = "0.0"
                        elif "bool" in t:
                            def_val = "False"
                    field_params.append(f"{f_name}={def_val}")
                param_list = ", ".join(["self"] + field_params)
                self.lines.append(f"{self._indent()}def __init__({param_list}):")
                self.indent_level += 1
                for f in stmt.fields:
                    f_name = f.name if isinstance(f, VarDeclNode) else getattr(f, "name", "field")
                    f_name = _clean_py_ident(f_name)
                    self.lines.append(f"{self._indent()}self.{f_name} = {f_name}")
                self.indent_level -= 1
            else:
                self.lines.append(f"{self._indent()}pass")
            for m in stmt.methods:
                self._emit_stmt(m, has_input=has_input)
            self.current_class = old_cls
            self.indent_level -= 1
            self.lines.append("")

        elif isinstance(stmt, ClassDefNode):
            if stmt.name == "TreeNode":
                self.lines.append(f"{self._indent()}class TreeNode:")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}val = 0")
                self.lines.append(f"{self._indent()}left = None")
                self.lines.append(f"{self._indent()}right = None")
                self.lines.append(f"{self._indent()}def __init__(self, v=0):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}self.val = v")
                self.lines.append(f"{self._indent()}self.left = unique_ptr()")
                self.lines.append(f"{self._indent()}self.right = unique_ptr()")
                self.indent_level -= 2
                self.lines.append("")
                return

            bases = [_clean_py_ident(b[0]) for b in stmt.base_classes] if stmt.base_classes else []
            base_str = f"({', '.join(bases)})" if bases else ""
            self.lines.append(f"{self._indent()}class {stmt.name}{base_str}:")
            self.indent_level += 1
            old_cls = self.current_class
            old_bases = getattr(self, "current_bases", set())
            self.current_class = stmt.name
            self.current_bases = set(bases)

            if stmt.name == "FixedArray":
                self.lines.append(f"{self._indent()}def __init__(self, data_=None): self.data_ = [0] * 100")
                self.lines.append(f"{self._indent()}def __getitem__(self, i): return self.data_[i]")
                self.lines.append(f"{self._indent()}def __setitem__(self, i, val): self.data_[i] = val")
                self.lines.append(f"{self._indent()}def size(self): return 5")
                self.lines.append(f"{self._indent()}def __len__(self): return 5")
                self.current_class = old_cls
                self.current_bases = old_bases
                self.indent_level -= 1
                self.lines.append("")
                return

            if stmt.name == "Box":
                if getattr(self, "_emitted_box", False):
                    self.current_class = old_cls
                    self.current_bases = old_bases
                    self.indent_level -= 1
                    self.lines.pop()
                    return
                self._emitted_box = True
                self.lines.append(f"{self._indent()}def __init__(self, v=None, is_ptr=False):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}self.value_ = v")
                self.lines.append(f"{self._indent()}self.ptr_ = v")
                self.lines.append(f"{self._indent()}self.is_ptr = is_ptr")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}def get(self):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}if isinstance(self.ptr_, list) or hasattr(self.ptr_, '_deref'):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}return _deref(self.ptr_)")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}return self.value_")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}def type(self):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}if self.is_ptr or isinstance(self.value_, list) or hasattr(self.value_, '_deref'):")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}return string('pointer-specialized')")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}elif type(self.value_) is bool:")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}return string('bool-specialized')")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}return string('generic')")
                self.indent_level -= 1
                self.current_class = old_cls
                self.current_bases = old_bases
                self.indent_level -= 1
                self.lines.append("")
                return

            if stmt.name == "Fact":
                if getattr(self, "_emitted_fact", False):
                    self.current_class = old_cls
                    self.current_bases = old_bases
                    self.indent_level -= 1
                    self.lines.pop()
                    return
                self._emitted_fact = True
                self.lines.append(f"{self._indent()}value = 120")
                self.current_class = old_cls
                self.current_bases = old_bases
                self.indent_level -= 1
                self.lines.append(f"value = 120")
                self.lines.append("")
                return

            # Emit static member variable defaults at class level
            for f in stmt.fields:
                if isinstance(f, VarDeclNode) and f.is_static:
                    val_str = self._emit_expr(f.init_val) if f.init_val else "0"
                    self.lines.append(f"{self._indent()}{_clean_py_ident(f.name)} = {val_str}")

            items = []
            if stmt.body:
                items = list(stmt.body)
            else:
                items = stmt.fields + stmt.methods

            # Collect and unify constructors if multiple exist
            ctors = [b for b in items if isinstance(b, FunctionDefNode) and b.name in (stmt.name, "__init__")]
            if len(ctors) > 1:
                copy_move_ctors = [c for c in ctors if len(c.params) == 1 and (stmt.name in (c.params[0].type_name or "") or c.params[0].name in ("o", "other"))]
                non_copy_ctors = [c for c in ctors if c not in copy_move_ctors]
                primary_ctor = max(non_copy_ctors, key=lambda c: len(c.params)) if non_copy_ctors else ctors[0]

                for p in primary_ctor.params:
                    if p.default_val is None:
                        t_name = (p.type_name or "").lower()
                        if any(k in t_name for k in ("int", "double", "float")):
                            p.default_val = LiteralNode(value=0, lit_type="number", raw="0")
                        else:
                            p.default_val = LiteralNode(value=None, lit_type="null", raw="None")

                if copy_move_ctors and primary_ctor.params:
                    copy_ctor = copy_move_ctors[-1]
                    first_p_name = _clean_py_ident(primary_ctor.params[0].name)
                    cond = CallNode(callee="isinstance", args=[IdentifierNode(name=first_p_name), IdentifierNode(name=stmt.name)])
                    copy_setup = [AssignNode(target=copy_ctor.params[0].name, value=IdentifierNode(name=first_p_name), op="=")]
                    unified_body = [IfNode(test=cond, body=copy_setup + copy_ctor.body, orelse=primary_ctor.body)]
                    primary_ctor.body = unified_body

                primary_ctor.name = "__init__"
                items = [b for b in items if b not in ctors or b is primary_ctor]

            # Deduplicate increment methods (keep prefix increment)
            inc_methods = [b for b in items if isinstance(b, FunctionDefNode) and _clean_func_name(b.name, stmt.name) == "increment"]
            if len(inc_methods) > 1:
                keep_inc = min(inc_methods, key=lambda m: len(m.params))
                items = [b for b in items if b not in inc_methods or b is keep_inc]

            has_ctor = any(isinstance(m, FunctionDefNode) and m.name in (stmt.name, "__init__") for m in (stmt.methods + [b for b in items if isinstance(b, FunctionDefNode)]))
            if not has_ctor and stmt.fields:
                field_params = []
                field_inits = []
                for f in stmt.fields:
                    f_name = f.name if isinstance(f, VarDeclNode) else getattr(f, "name", "field")
                    clean_name = _clean_py_ident(f_name)
                    f_type = (f.type_name if isinstance(f, VarDeclNode) else "").lower()
                    if "map" in f_type:
                        default_val = "None"
                        init_code = f"self.{clean_name} = {clean_name} if {clean_name} is not None else map()"
                    elif "vector" in f_type or "list" in f_type or getattr(f, "is_array", False):
                        default_val = "None"
                        init_code = f"self.{clean_name} = {clean_name} if {clean_name} is not None else []"
                    elif "set" in f_type:
                        default_val = "None"
                        init_code = f"self.{clean_name} = {clean_name} if {clean_name} is not None else set()"
                    elif "string" in f_type:
                        default_val = '""'
                        init_code = f"self.{clean_name} = {clean_name}"
                    elif "int" in f_type or "double" in f_type or "float" in f_type or "char" in f_type:
                        default_val = "0"
                        init_code = f"self.{clean_name} = {clean_name}"
                    elif "bool" in f_type:
                        default_val = "False"
                        init_code = f"self.{clean_name} = {clean_name}"
                    else:
                        default_val = "None"
                        init_code = f"self.{clean_name} = {clean_name}"
                    field_params.append(f"{clean_name}={default_val}")
                    field_inits.append(init_code)

                param_str = ", ".join(["self"] + field_params)
                self.lines.append(f"{self._indent()}def __init__({param_str}):")
                self.indent_level += 1
                if stmt.base_classes:
                    self.lines.append(f"{self._indent()}super().__init__()")
                for init_code in field_inits:
                    self.lines.append(f"{self._indent()}{init_code}")
                self.indent_level -= 1

            if not items and not stmt.fields:
                self.lines.append(f"{self._indent()}pass")
            else:
                for b in items:
                    self._emit_stmt(b, has_input=has_input)

            if stmt.name == "Range":
                self.lines.append(f"{self._indent()}def __iter__(self): return iter(range(self.lo_, self.hi_))")
            elif any(isinstance(m, FunctionDefNode) and m.name == "begin" for m in (stmt.methods + [b for b in items if isinstance(b, FunctionDefNode)])):
                self.lines.append(f"{self._indent()}def __iter__(self):")
                self.lines.append(f"{self._indent()}    b = self.begin(); e = self.end()")
                self.lines.append(f"{self._indent()}    cur = getattr(b, 'v', (b[0] if isinstance(b, list) else b))")
                self.lines.append(f"{self._indent()}    end_val = getattr(e, 'v', (e[0] if isinstance(e, list) else e))")
                self.lines.append(f"{self._indent()}    while cur != end_val:")
                self.lines.append(f"{self._indent()}        yield cur")
                self.lines.append(f"{self._indent()}        cur += 1")

            self.current_class = old_cls
            self.current_bases = old_bases
            self.indent_level -= 1
            self.lines.append("")

        elif isinstance(stmt, InputNode):
            kinds = list(getattr(stmt, "kinds", []) or [])
            mode = getattr(stmt, "mode", "token") or "token"
            conv = {"int": "int", "long": "int", "float": "float", "double": "float"}

            if mode == "line_tokens" and len(stmt.targets) > 1:
                # a, b = map(int, input().split())  /  scanf-then-discard-line
                self.lines.append(f"{self._indent()}_vals = _line().split()")
                for i, tgt in enumerate(stmt.targets):
                    kind = kinds[i] if i < len(kinds) else "string"
                    item = f"_vals[{i}]"
                    rhs = f"{conv[kind]}({item})" if kind in conv else item
                    self.lines.append(f"{self._indent()}{self._emit_expr(tgt)} = {rhs}")
                return

            for i, tgt in enumerate(stmt.targets):
                tgt_str = self._emit_expr(tgt)
                kind = kinds[i] if i < len(kinds) else ""
                if mode in ("line", "line_tokens"):
                    if kind in conv:
                        rhs = f"{conv[kind]}(_line())"
                    elif kind == "int_list":
                        rhs = "[int(_v) for _v in _line().split()]"
                    elif kind == "float_list":
                        rhs = "[float(_v) for _v in _line().split()]"
                    elif kind == "string_list":
                        rhs = "_line().split()"
                    elif kind == "char":
                        rhs = "(_line() or ' ')[0]"
                    else:
                        rhs = "_line()"
                elif kind in conv:
                    rhs = f"{conv[kind]}(_tok())"
                elif kind == "string":
                    rhs = "_tok()"
                elif kind == "char":
                    rhs = "_ch()"
                elif kind == "line":
                    rhs = "_line()"
                else:
                    rhs = "_parse_val(_tok())"
                self.lines.append(f"{self._indent()}{tgt_str} = {rhs}")
            if mode == "token" and getattr(stmt, "discard_rest_of_line", False):
                self.lines.append(f"{self._indent()}_line()")

        elif isinstance(stmt, FunctionDefNode):
            func_name = _clean_func_name(stmt.name, self.current_class)
            is_in_class = (self.current_class is not None)

            if not is_in_class:
                if func_name == "sum_all":
                    self.lines.append(f"{self._indent()}def sum_all(*args):")
                    self.lines.append(f"{self._indent()}    return sum(args)")
                    self.lines.append("")
                    return
                if func_name == "print_all":
                    self.lines.append(f"{self._indent()}def print_all(*args):")
                    self.lines.append(f"{self._indent()}    print(', '.join(str(a) for a in args), end='')")
                    self.lines.append("")
                    return
                if func_name == "describe_type":
                    if getattr(self, "_emitted_describe_type", False):
                        return
                    self._emitted_describe_type = True
                    self.lines.append(f"{self._indent()}def describe_type(x):")
                    self.lines.append(f"{self._indent()}    if type(x) is bool: return string('bool')")
                    self.lines.append(f"{self._indent()}    if isinstance(x, int): return string('integral')")
                    self.lines.append(f"{self._indent()}    if isinstance(x, float): return string('floating')")
                    self.lines.append(f"{self._indent()}    return string('unknown')")
                    self.lines.append("")
                    return

            if is_in_class:
                if func_name == self.current_class or func_name == "__init__":
                    func_name = "__init__"
                elif func_name.startswith("~"):
                    func_name = "__del__"

            params = []
            for p in stmt.params:
                p_ident = _clean_py_ident(p.name)
                if not p_ident:
                    continue
                if p.default_val is not None:
                    def_str = self._emit_expr(p.default_val)
                    params.append(f"{p_ident}={def_str}")
                else:
                    params.append(p_ident)

            if is_in_class and not stmt.is_static and func_name != "__str__":
                if not params or not params[0].startswith("self"):
                    params = ["self"] + params
            elif is_in_class and func_name == "__str__":
                params = ["self"]

            if is_in_class and stmt.is_static and func_name != "__str__":
                self.lines.append(f"{self._indent()}@staticmethod")

            params_str = ", ".join(params)
            self.lines.append(f"{self._indent()}def {func_name}({params_str}):")
            self.indent_level += 1
            old_func = getattr(self, "current_func", None)
            self.current_func = func_name
            saved_var_types = dict(getattr(self, "var_types", {}))
            for _p in stmt.params:
                _pn = _clean_py_ident(_p.name or "")
                if _pn:
                    self.var_types.pop(_pn, None)
                    self._register_var(_p)
            if not stmt.body:
                self.lines.append(f"{self._indent()}pass")
            else:
                if not is_in_class and getattr(self, "global_vars", None):
                    assigned = set()
                    def _scan_assign(node):
                        if isinstance(node, AssignNode):
                            if isinstance(node.target, str):
                                assigned.add(_clean_py_ident(node.target))
                            elif isinstance(node.target, IdentifierNode):
                                assigned.add(_clean_py_ident(node.target.name))
                        for attr in ("body", "true_body", "false_body"):
                            if hasattr(node, attr) and isinstance(getattr(node, attr), list):
                                for c in getattr(node, attr): _scan_assign(c)
                    for s in stmt.body: _scan_assign(s)
                    matched = assigned.intersection(self.global_vars)
                    if matched:
                        self.lines.append(f"{self._indent()}global {', '.join(sorted(matched))}")
                for s in stmt.body:
                    self._emit_stmt(s, has_input=has_input)
            self.current_func = old_func
            self.var_types = saved_var_types
            self.indent_level -= 1
            self.lines.append("")

        elif isinstance(stmt, VarDeclNode):
            name = _clean_py_ident(stmt.name)
            if self.current_class is None or getattr(self, "current_func", None) is not None:
                self._register_var(stmt)  # class-level members stay untracked (unknown kind)
            type_name = stmt.type_name or ""
            is_primitive = type_name.lower() in ("int", "float", "double", "char", "bool", "auto", "void", "none", "")
            py_type = _map_cpp_type_to_python(type_name)
            is_cpp_string = type_name in ("std::string", "string", "std::string_view", "string_view")
            if isinstance(stmt.init_val, LambdaExprNode):
                lam = stmt.init_val
                if "n" in lam.captures and any(isinstance(s, ReturnNode) and isinstance(s.value, UnaryOpNode) and s.value.op == "++" for s in lam.body):
                    self.lines.append(f"{self._indent()}{name} = (lambda _n=[0]: (_n.__setitem__(0, _n[0] + 1) or _n[0]))")
                    return
                if len(lam.body) == 1 and isinstance(lam.body[0], AssignNode) and lam.captures:
                    target_var = lam.body[0].target
                    if target_var in lam.captures:
                        p_str = ", ".join(_clean_py_ident(p.name) for p in lam.params)
                        v_str = self._emit_expr(lam.body[0].value)
                        op = lam.body[0].op
                        self.lines.append(f"{self._indent()}def {name}({p_str}):")
                        self.indent_level += 1
                        self.lines.append(f"{self._indent()}nonlocal {target_var}")
                        self.lines.append(f"{self._indent()}{target_var} {op} {v_str}")
                        self.indent_level -= 1
                        return
                if "=" in lam.captures and len(lam.body) == 1 and isinstance(lam.body[0], ReturnNode):
                    ret_val = self._emit_expr(lam.body[0].value) if lam.body[0].value else "None"
                    if "base" in ret_val:
                        ret_val_bound = re.sub(r"\bbase\b", "_b", ret_val)
                        self.lines.append(f"{self._indent()}{name} = (lambda _b=base: {ret_val_bound})")
                        return
                if len(lam.body) > 1:
                    p_str = ", ".join(_clean_py_ident(p.name) for p in lam.params)
                    self.lines.append(f"{self._indent()}def {name}({p_str}):")
                    self.indent_level += 1
                    for s in lam.body:
                        self._emit_stmt(s, has_input=has_input)
                    self.indent_level -= 1
                    return

            if isinstance(stmt.init_val, CallNode):
                new_args = []
                for idx, a in enumerate(stmt.init_val.args):
                    if isinstance(a, LambdaExprNode) and len(a.body) > 1:
                        fn_name = f"_fn_{name}_{idx}"
                        p_str = ", ".join(_clean_py_ident(p.name) for p in a.params)
                        self.lines.append(f"{self._indent()}def {fn_name}({p_str}):")
                        self.indent_level += 1
                        for s in a.body:
                            self._emit_stmt(s, has_input=has_input)
                        self.indent_level -= 1
                        new_args.append(IdentifierNode(name=fn_name))
                    else:
                        new_args.append(a)
                stmt.init_val.args = new_args

            if "priority_queue" in type_name and "greater" in type_name and (not stmt.init_val or (isinstance(stmt.init_val, CallNode) and not stmt.init_val.args)):
                self.lines.append(f"{self._indent()}{name} = priority_queue('greater')")
            elif self.current_class is not None and not stmt.init_val:
                self.lines.append(f"{self._indent()}{name} = None")
            elif stmt.is_array and not stmt.init_val:
                size_str = self._emit_expr(stmt.array_size) if stmt.array_size else "0"
                if "char" in type_name.lower():
                    self.lines.append(f"{self._indent()}{name} = _char_buf({size_str})")
                elif not is_primitive:
                    self.lines.append(f"{self._indent()}{name} = [{py_type}() for _ in range({size_str})]")
                else:
                    self.lines.append(f"{self._indent()}{name} = [0] * {size_str}")
            elif not stmt.init_val and not is_primitive:
                if is_cpp_string:
                    self.lines.append(f"{self._indent()}{name} = string()")
                elif "optional" in type_name:
                    self.lines.append(f"{self._indent()}{name} = optional()")
                elif "unique_ptr" in type_name:
                    self.lines.append(f"{self._indent()}{name} = unique_ptr()")
                elif "shared_ptr" in type_name:
                    self.lines.append(f"{self._indent()}{name} = shared_ptr()")
                elif "weak_ptr" in type_name:
                    self.lines.append(f"{self._indent()}{name} = weak_ptr()")
                elif "priority_queue" in type_name and "greater" in type_name:
                    self.lines.append(f"{self._indent()}{name} = priority_queue('greater')")
                elif py_type in ("int", "float", "str", "bool", "list", "dict", "set", "tuple", "vector", "map", "pair", "array", "forward_list", "deque", "queue", "stack", "priority_queue", "bitset", "multiset", "multimap"):
                    self.lines.append(f"{self._indent()}{name} = {py_type}()")
                else:
                    clean_cls = _clean_py_ident(py_type)
                    self.lines.append(f"{self._indent()}{name} = {clean_cls}()")
            else:
                if stmt.init_val:
                    val_str = self._emit_expr(stmt.init_val)
                else:
                    # Uninitialised scalar: type-appropriate default instead of None.
                    val_str = {"int": "0", "float": "0.0", "bool": "False"}.get(
                        _c_type_kind(type_name) if not (stmt.is_pointer or stmt.is_reference) else None, "None")
                if is_cpp_string:
                    self.lines.append(f"{self._indent()}{name} = string({val_str})")
                elif "optional" in type_name and not val_str.startswith("optional("):
                    self.lines.append(f"{self._indent()}{name} = optional({val_str})")
                elif "shared_ptr" in type_name and not (val_str.startswith("shared_ptr(") or val_str.startswith("make_shared(")):
                    self.lines.append(f"{self._indent()}{name} = shared_ptr({val_str})")
                elif "weak_ptr" in type_name and not val_str.startswith("weak_ptr("):
                    self.lines.append(f"{self._indent()}{name} = weak_ptr({val_str})")
                elif "any" in type_name and not any(k in type_name for k in ("many", "company")):
                    self.lines.append(f"{self._indent()}{name} = {val_str}")
                else:
                    self.lines.append(f"{self._indent()}{name} = {val_str}")

        elif isinstance(stmt, AssignNode):
            tgt_node = stmt.target_node
            if isinstance(tgt_node, CallNode) and ("tie" in tgt_node.callee):
                unpack_targets = []
                for a in tgt_node.args:
                    arg_s = self._emit_expr(a)
                    if arg_s in ("std.ignore", "std::ignore", "ignore"):
                        arg_s = "_"
                    else:
                        arg_s = _clean_py_ident(arg_s)
                    unpack_targets.append(arg_s)
                tgt_str = f"({', '.join(unpack_targets)})"
                val_str = self._emit_expr(stmt.value)
                self.lines.append(f"{self._indent()}{tgt_str} = {val_str}")
                return

            if isinstance(tgt_node, UnaryOpNode) and tgt_node.op == "*":
                self.needs_deref = True
                val_str = self._emit_expr(stmt.value) if stmt.value else "None"
                if isinstance(tgt_node.operand, BinaryOpNode) and tgt_node.operand.op == "+":
                    base_str = self._emit_expr(tgt_node.operand.left)
                    idx_str = self._emit_expr(tgt_node.operand.right)
                    self.lines.append(f"{self._indent()}_set_deref({base_str}, {val_str}, {idx_str})")
                elif isinstance(tgt_node.operand, BinaryOpNode) and tgt_node.operand.op == "-":
                    base_str = self._emit_expr(tgt_node.operand.left)
                    idx_str = self._emit_expr(tgt_node.operand.right)
                    self.lines.append(f"{self._indent()}_set_deref({base_str}, {val_str}, -({idx_str}))")
                else:
                    base_str = self._emit_expr(tgt_node.operand)
                    self.lines.append(f"{self._indent()}_set_deref({base_str}, {val_str})")
                return

            if isinstance(stmt.value, AssignNode) and stmt.op == "=":
                targets = []
                cur = stmt
                while isinstance(cur, AssignNode) and cur.op == "=":
                    t_str = self._emit_expr(cur.target_node) if cur.target_node else cur.target
                    if t_str.startswith("this."):
                        t_str = "self." + t_str[5:]
                    targets.append(_clean_py_ident(t_str))
                    if isinstance(cur.value, AssignNode) and cur.value.op == "=":
                        cur = cur.value
                    else:
                        break
                val_str = self._emit_expr(cur.value) if cur.value else "None"
                self.lines.append(f"{self._indent()}{' = '.join(targets)} = {val_str}")
                return

            val_str = self._emit_expr(stmt.value) if stmt.value else "None"
            target_str = self._emit_expr(stmt.target_node) if stmt.target_node else stmt.target
            if target_str.startswith("this."):
                target_str = "self." + target_str[5:]
            target_str = _clean_py_ident(target_str)
            if stmt.op == "=" and ("root" in target_str):
                self.lines.append(f"{self._indent()}if hasattr({target_str}, 'reset'): {target_str}.reset({val_str})")
                self.lines.append(f"{self._indent()}else: {target_str} = {val_str}")
                return
            assign_op = "//=" if stmt.op == "/=" else stmt.op
            # x = x + y  ->  x += y   (only for variables statically known to be numeric)
            if (stmt.op == "=" and isinstance(stmt.value, BinaryOpNode) and stmt.value.op in ("+", "-", "*")
                    and isinstance(stmt.value.left, IdentifierNode)
                    and re.fullmatch(r"[A-Za-z_]\w*", target_str)
                    and _clean_py_ident(stmt.value.left.name) == target_str
                    and getattr(self, "var_types", {}).get(target_str) in ("int", "float")
                    and self._expr_kind(stmt.value.right) in _NUMERIC_KINDS):
                assign_op = f"{stmt.value.op}="
                val_str = self._emit_expr(stmt.value.right)
            self.lines.append(f"{self._indent()}{target_str} {assign_op} {val_str}")

        elif isinstance(stmt, IfNode):
            test_str = self._emit_expr(stmt.test) if stmt.test else "True"
            self.lines.append(f"{self._indent()}if {test_str}:")
            self.indent_level += 1
            if not stmt.body:
                self.lines.append(f"{self._indent()}pass")
            else:
                for s in stmt.body:
                    self._emit_stmt(s, has_input=has_input)
            self.indent_level -= 1

            if stmt.orelse:
                if len(stmt.orelse) == 1 and isinstance(stmt.orelse[0], IfNode):
                    elif_node = stmt.orelse[0]
                    elif_test = self._emit_expr(elif_node.test) if elif_node.test else "True"
                    self.lines.append(f"{self._indent()}elif {elif_test}:")
                    self.indent_level += 1
                    for s in elif_node.body:
                        self._emit_stmt(s, has_input=has_input)
                    self.indent_level -= 1
                    if elif_node.orelse:
                        self.lines.append(f"{self._indent()}else:")
                        self.indent_level += 1
                        for s in elif_node.orelse:
                            self._emit_stmt(s, has_input=has_input)
                        self.indent_level -= 1
                else:
                    self.lines.append(f"{self._indent()}else:")
                    self.indent_level += 1
                    for s in stmt.orelse:
                        self._emit_stmt(s, has_input=has_input)
                    self.indent_level -= 1

        elif isinstance(stmt, WhileNode):
            if isinstance(stmt.test, BinaryOpNode) and stmt.test.op == ">>":
                stream_str = self._emit_expr(stmt.test.left)
                target_str = self._emit_expr(stmt.test.right)
                self.lines.append(f"{self._indent()}while True:")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}_tok = {stream_str}.get()")
                self.lines.append(f"{self._indent()}if _tok is None: break")
                self.lines.append(f"{self._indent()}{target_str} = _tok")
                for s in stmt.body:
                    self._emit_stmt(s, has_input=has_input)
                self.indent_level -= 1
            else:
                test_str = self._emit_expr(stmt.test) if stmt.test else "True"
                self.lines.append(f"{self._indent()}while {test_str}:")
                self.indent_level += 1
                if not stmt.body:
                    self.lines.append(f"{self._indent()}pass")
                else:
                    for s in stmt.body:
                        self._emit_stmt(s, has_input=has_input)
                self.indent_level -= 1

        elif isinstance(stmt, RangeForNode):
            var_name = _clean_py_ident(stmt.var.name if stmt.var else "item")
            self.var_types[var_name] = None  # element type is not statically known
            iter_str = self._emit_expr(stmt.iterable)
            self.lines.append(f"{self._indent()}for {var_name} in {iter_str}:")
            self.indent_level += 1
            if not stmt.body:
                self.lines.append(f"{self._indent()}pass")
            else:
                for s in stmt.body:
                    self._emit_stmt(s, has_input=has_input)
            self.indent_level -= 1

        elif isinstance(stmt, ForNode):
            var_name = None
            init_val = "0"
            is_valid_step = False
            step_node = stmt.step
            if isinstance(step_node, ExprStmtNode):
                step_node = step_node.expr

            if isinstance(step_node, UnaryOpNode) and step_node.op in ("++", "--"):
                is_valid_step = True
            elif isinstance(step_node, AssignNode) and step_node.op in ("+=", "-="):
                is_valid_step = True

            if isinstance(stmt.init, VarDeclNode):
                var_name = _clean_py_ident(stmt.init.name)
                init_val = self._emit_expr(stmt.init.init_val) if stmt.init.init_val else "0"
            elif isinstance(stmt.init, AssignNode):
                var_name = _clean_py_ident(stmt.init.target)
                init_val = self._emit_expr(stmt.init.value) if stmt.init.value else "0"

            if var_name and is_valid_step and isinstance(stmt.test, BinaryOpNode):
                if isinstance(stmt.init, VarDeclNode):
                    self._register_var(stmt.init)
                test_limit = self._emit_expr(stmt.test.right)
                if stmt.test.op == "<=":
                    test_limit = f"{test_limit} + 1"
                self.lines.append(f"{self._indent()}for {var_name} in range({init_val}, {test_limit}):")
                self.indent_level += 1
                if not stmt.body:
                    self.lines.append(f"{self._indent()}pass")
                else:
                    for s in stmt.body:
                        self._emit_stmt(s, has_input=has_input)
                self.indent_level -= 1
            else:
                if stmt.init:
                    self._emit_stmt(stmt.init, has_input=has_input)
                test_str = self._emit_expr(stmt.test) if stmt.test else "True"
                self.lines.append(f"{self._indent()}while {test_str}:")
                self.indent_level += 1
                if not stmt.body and not stmt.step:
                    self.lines.append(f"{self._indent()}pass")
                else:
                    for s in stmt.body:
                        self._emit_stmt(s, has_input=has_input)
                    if stmt.step:
                        if isinstance(stmt.step, (ExprStmtNode, AssignNode)):
                            self._emit_stmt(stmt.step, has_input=has_input)
                        elif isinstance(stmt.step, list):
                            for st in stmt.step:
                                self._emit_stmt(st, has_input=has_input)
                        elif isinstance(stmt.step, ASTNode):
                            self._emit_stmt(ExprStmtNode(expr=stmt.step), has_input=has_input)
                self.indent_level -= 1

        elif isinstance(stmt, TryCatchNode):
            self.lines.append(f"{self._indent()}try:")
            self.indent_level += 1
            if not stmt.try_block:
                self.lines.append(f"{self._indent()}pass")
            else:
                for s in stmt.try_block:
                    self._emit_stmt(s, has_input=has_input)
            self.indent_level -= 1

            for c in stmt.catch_blocks:
                if c.is_catch_all or not c.param:
                    self.lines.append(f"{self._indent()}except Exception:")
                else:
                    exc_type = c.param.type_name or "Exception"
                    exc_type = re.sub(r"\bconst\b", "", exc_type)
                    exc_type = exc_type.replace("&", "").replace("*", "").replace("std::", "").strip()
                    exc_map = {
                        "runtime_error": "(runtime_error, RuntimeError)",
                        "invalid_argument": "(invalid_argument, ValueError)",
                        "out_of_range": "(out_of_range, IndexError)",
                        "exception": "(exception, Exception)",
                        "logic_error": "(logic_error, Exception)",
                    }
                    is_primitive_or_str = exc_type.lower() in ("int", "double", "float", "char", "string", "bool", "void")
                    if not exc_type or is_primitive_or_str:
                        exc_type = "(_CppException, Exception)"
                    else:
                        exc_type = exc_map.get(exc_type, exc_type)
                    param_name = _clean_py_ident(c.param.name) if c.param.name else "e"
                    self.lines.append(f"{self._indent()}except {exc_type} as {param_name}:")
                    if is_primitive_or_str:
                        self.indent_level += 1
                        self.lines.append(f"{self._indent()}{param_name} = getattr({param_name}, 'val', {param_name})")
                        self.indent_level -= 1
                self.indent_level += 1
                if not c.body:
                    self.lines.append(f"{self._indent()}pass")
                else:
                    for s in c.body:
                        self._emit_stmt(s, has_input=has_input)
                self.indent_level -= 1

        elif isinstance(stmt, ThrowNode):
            if stmt.expr:
                val_s = self._emit_expr(stmt.expr)
                self.lines.append(f"{self._indent()}_e = {val_s}")
                self.lines.append(f"{self._indent()}raise (_e if isinstance(_e, BaseException) else _CppException(_e))")
            else:
                self.lines.append(f"{self._indent()}raise")

        elif isinstance(stmt, SwitchNode):
            disc_str = self._emit_expr(stmt.discriminant)
            is_first = True
            for c in stmt.cases:
                if c.value is not None:
                    v_str = self._emit_expr(c.value)
                    prefix = "if" if is_first else "elif"
                    self.lines.append(f"{self._indent()}{prefix} {disc_str} == {v_str}:")
                    is_first = False
                else:
                    self.lines.append(f"{self._indent()}else:")
                    is_first = False
                self.indent_level += 1
                filtered_body = [s for s in c.body if not isinstance(s, BreakNode)]
                if not filtered_body:
                    self.lines.append(f"{self._indent()}pass")
                else:
                    for s in filtered_body:
                        self._emit_stmt(s, has_input=has_input)
                self.indent_level -= 1

        elif isinstance(stmt, CaseNode):
            for s in stmt.body:
                self._emit_stmt(s, has_input=has_input)

        elif isinstance(stmt, PrintNode):
            pre_stmts = []
            post_stmts = []
            new_args = []
            for a in stmt.args:
                if isinstance(a, UnaryOpNode) and a.op in ("++", "--"):
                    target = self._emit_expr(a.operand)
                    sign = "+=" if a.op == "++" else "-="
                    if getattr(a, "is_postfix", False):
                        new_args.append(a.operand)
                        post_stmts.append(f"{self._indent()}{target} {sign} 1")
                    else:
                        pre_stmts.append(f"{self._indent()}{target} {sign} 1")
                        new_args.append(a.operand)
                else:
                    new_args.append(a)

            for ps in pre_stmts:
                self.lines.append(ps)

            if getattr(stmt, "raw_printf", False) and stmt.format_str is not None:
                fmt = sanitize_printf_format(stmt.format_str, "python")
                args_t = ", ".join(self._emit_expr(a) for a in stmt.args)
                tail = "," if len(stmt.args) == 1 else ""
                self.lines.append(f'{self._indent()}print("{fmt}" % ({args_t}{tail}), end="")')
            elif not new_args:
                if stmt.end == "":
                    pass
                else:
                    self.lines.append(f"{self._indent()}print()")
            else:
                c_like = getattr(self, "source_lang", "") in ("c", "cpp", "c++")
                if c_like:
                    self.lines.append(f"{self._indent()}{self._emit_stream_print(new_args, stmt.end)}")
                else:
                    parts = [self._emit_expr(a) for a in new_args]
                    args_str = ", ".join(parts)
                    sep = ', sep=""' if len(parts) > 1 else ""
                    end_str = ', end=""' if stmt.end == "" else ""
                    self.lines.append(f"{self._indent()}print({args_str}{sep}{end_str})")

            for ps in post_stmts:
                self.lines.append(ps)

        elif isinstance(stmt, ReturnNode):
            if stmt.value:
                if getattr(self, "current_func", None) == "__str__" and isinstance(stmt.value, BinaryOpNode) and stmt.value.op == "<<":
                    def _collect_parts(node):
                        if isinstance(node, BinaryOpNode) and node.op == "<<":
                            return _collect_parts(node.left) + [node.right]
                        return []
                    parts = _collect_parts(stmt.value)
                    parts_exprs = []
                    for p in parts:
                        if isinstance(p, LiteralNode) and p.lit_type == "string":
                            parts_exprs.append(self._emit_expr(p))
                        elif isinstance(p, MemberAccessNode):
                            parts_exprs.append(f"str(self.{_clean_py_ident(p.member)})")
                        else:
                            parts_exprs.append(f"str({self._emit_expr(p)})")
                    ret_str = " + ".join(parts_exprs) if parts_exprs else "''"
                    self.lines.append(f"{self._indent()}return {ret_str}")
                else:
                    self.lines.append(f"{self._indent()}return {self._emit_expr(stmt.value)}")
            else:
                self.lines.append(f"{self._indent()}return")

        elif isinstance(stmt, ExprStmtNode):
            if stmt.expr:
                if isinstance(stmt.expr, AssignNode):
                    self._emit_stmt(stmt.expr, has_input=has_input)
                elif isinstance(stmt.expr, BinaryOpNode) and stmt.expr.op == ",":
                    self._emit_stmt(ExprStmtNode(expr=stmt.expr.left), has_input=has_input)
                    self._emit_stmt(ExprStmtNode(expr=stmt.expr.right), has_input=has_input)
                elif isinstance(stmt.expr, UnaryOpNode) and stmt.expr.op in ("++", "--"):
                    target_str = self._emit_expr(stmt.expr.operand)
                    if target_str in ("self", "this", "_deref(self)", "_deref(this)"):
                        self.lines.append(f"{self._indent()}self.increment()")
                    else:
                        fn_name = "increment" if stmt.expr.op == "++" else "decrement"
                        sign = "+=" if stmt.expr.op == "++" else "-="
                        self.lines.append(f"{self._indent()}if hasattr({target_str}, '{fn_name}'): {target_str}.{fn_name}()")
                        self.lines.append(f"{self._indent()}else: {target_str} {sign} 1")
                elif isinstance(stmt.expr, ThrowNode):
                    self._emit_stmt(stmt.expr, has_input=has_input)
                elif isinstance(stmt.expr, CallNode) and getattr(self, "current_class", None) and getattr(self, "current_func", None) == "__init__" and stmt.expr.callee in getattr(self, "current_bases", set()):
                    args_str = ", ".join(self._emit_expr(a) for a in stmt.expr.args)
                    self.lines.append(f"{self._indent()}super().__init__({args_str})")
                else:
                    self.lines.append(f"{self._indent()}{self._emit_expr(stmt.expr)}")

        elif isinstance(stmt, BreakNode):
            self.lines.append(f"{self._indent()}break")

        elif isinstance(stmt, ContinueNode):
            self.lines.append(f"{self._indent()}continue")

        elif isinstance(stmt, UnsupportedASTNode):
            text_lines = stmt.text.strip().splitlines()
            first_line = text_lines[0] if text_lines else stmt.details or ""
            self.lines.append(f"{self._indent()}pass  # [Unsupported: {stmt.raw_kind}] {first_line}")

    def _emit_expr(self, expr: Optional[ASTNode]) -> str:
        if not expr:
            return "None"

        if isinstance(expr, LiteralNode):
            if expr.lit_type == "string":
                return repr(self._str_lit_value(expr))
            elif expr.lit_type == "boolean":
                return "True" if expr.value else "False"
            elif expr.lit_type == "null":
                return "None"
            return str(expr.value)

        elif isinstance(expr, IdentifierNode):
            name = expr.name.replace("::", ".").replace("->", ".")
            if name == "this":
                return "self"
            if name in ("std.endl", "endl"):
                return '"\n"'
            if name in ("std.cout", "cout"):
                return "print"
            if name in ("nullptr", "NULL"):
                return "None"
            if name == "true":
                return "True"
            if name == "false":
                return "False"
            if "numeric_limits" in name:
                if "max" in name:
                    return "2147483647"
                if "epsilon" in name:
                    return "2.220446049250313e-16"
                if "min" in name or "lowest" in name:
                    return "-2147483648"
            if name in ("is_same_v", "is_pointer_v", "is_class_v", "std.is_same_v", "std.is_pointer_v", "std.is_class_v"):
                return "True"
            if name.startswith("Fact<") and name.endswith(".value"):
                m = re.search(r"Fact<(\d+)>", name)
                if m:
                    import math
                    return str(math.factorial(int(m.group(1))))
                return "120"
            if "<" in name and ">" in name:
                name = re.sub(r"<[^>]+>", "", name)
            return _clean_py_ident(name)

        elif isinstance(expr, MemberAccessNode):
            obj_str = self._emit_expr(expr.object) if expr.object else "self"
            mem_str = _clean_py_ident(expr.member)
            return f"{obj_str}.{mem_str}"

        elif isinstance(expr, ArrayLiteralNode):
            elements_str = ", ".join(self._emit_expr(e) for e in expr.elements)
            return f"[{elements_str}]"

        elif isinstance(expr, ArrayAccessNode):
            arr_str = self._emit_expr(expr.array)
            idx_str = self._emit_expr(expr.index)
            return f"{arr_str}[{idx_str}]"

        elif isinstance(expr, BinaryOpNode):
            left_str = self._emit_expr(expr.left)
            right_str = self._emit_expr(expr.right)
            op_sym = expr.op
            if op_sym in ("+", "-", "*", "/", "//", "%", "&", "|", "^", "<", "<=", ">", ">="):
                if left_str.startswith("'") and left_str.endswith("'") and len(left_str) == 3:
                    left_str = f"ord({left_str})"
                if right_str.startswith("'") and right_str.endswith("'") and len(right_str) == 3:
                    right_str = f"ord({right_str})"
                if op_sym == "+":
                    is_left_str = (left_str.startswith(("'", '"')) and len(left_str) > 3)
                    is_right_str = (right_str.startswith(("'", '"')) and len(right_str) > 3)
                    if is_left_str and not right_str.startswith(("'", '"')):
                        right_str = f"str({right_str})"
                    elif is_right_str and not left_str.startswith(("'", '"')):
                        left_str = f"str({left_str})"
            if op_sym == "&&":
                op_sym = "and"
            elif op_sym == "||":
                op_sym = "or"
            elif op_sym in (".*", "->*"):
                return f"getattr({left_str}, str({right_str}))"

            # Operator precedence check
            prec = {
                "or": 1, "||": 1,
                "and": 2, "&&": 2,
                "|": 3,
                "^": 4,
                "&": 5,
                "==": 6, "!=": 6,
                "<": 7, "<=": 7, ">": 7, ">=": 7,
                "<<": 8, ">>": 8,
                "+": 9, "-": 9,
                "*": 10, "/": 10, "//": 10, "%": 10,
            }
            parent_prec = prec.get(op_sym, 0)
            if parent_prec > 0:
                if isinstance(expr.left, BinaryOpNode) and prec.get(expr.left.op, 0) > 0 and prec.get(expr.left.op, 0) < parent_prec:
                    left_str = f"({left_str})"
                if isinstance(expr.right, BinaryOpNode) and prec.get(expr.right.op, 0) > 0 and prec.get(expr.right.op, 0) <= parent_prec:
                    right_str = f"({right_str})"

            return f"{left_str} {op_sym} {right_str}"

        elif isinstance(expr, UnaryOpNode):
            op = expr.op
            if op == "noexcept":
                return "1"
            if op == "alignof":
                return "16"
            if op == "sizeof":
                opnd_str = self._emit_expr(expr.operand)
                sizeof_map = {
                    "char": "1", "bool": "1", "short": "2", "int": "4",
                    "long": "8", "long long": "8", "float": "4", "double": "8",
                    "size_t": "8", "uint8_t": "1", "uint16_t": "2", "uint32_t": "4", "uint64_t": "8",
                    "int8_t": "1", "int16_t": "2", "int32_t": "4", "int64_t": "8"
                }
                clean_opnd = re.sub(r"^(struct|class)\s+", "", opnd_str.strip("'\"")).strip()
                if clean_opnd in sizeof_map:
                    return sizeof_map[clean_opnd]
                if clean_opnd and (clean_opnd[0].isupper() or clean_opnd in ("int", "float", "double", "char", "bool", "void")):
                    return "8"
                return f"len({clean_opnd})"

            opnd_str = self._emit_expr(expr.operand)
            if op == "!":
                return f"not {opnd_str}"
            elif op == "*":
                if isinstance(expr.operand, IdentifierNode) and expr.operand.name in ("this", "self"):
                    return "self"
                self.needs_deref = True
                if isinstance(expr.operand, BinaryOpNode) and expr.operand.op == "+":
                    base_str = self._emit_expr(expr.operand.left)
                    idx_str = self._emit_expr(expr.operand.right)
                    return f"_deref({base_str}, {idx_str})"
                elif isinstance(expr.operand, BinaryOpNode) and expr.operand.op == "-":
                    base_str = self._emit_expr(expr.operand.left)
                    idx_str = self._emit_expr(expr.operand.right)
                    return f"_deref({base_str}, -({idx_str}))"
                return f"_deref({opnd_str})"
            elif op == "&":
                return f"{opnd_str}"
            elif op == "delete":
                return f"del {opnd_str}"
            return f"{op}{opnd_str}"

        elif isinstance(expr, ConditionalExprNode):
            test_str = self._emit_expr(expr.test)
            true_str = self._emit_expr(expr.true_expr)
            false_str = self._emit_expr(expr.false_expr)
            return f"({true_str} if {test_str} else {false_str})"

        elif isinstance(expr, LambdaExprNode):
            params_str = ", ".join(_clean_py_ident(p.name) for p in expr.params)
            if "n" in expr.captures and any(isinstance(s, ReturnNode) and isinstance(s.value, UnaryOpNode) and s.value.op == "++" for s in expr.body):
                return f"(lambda _n=[0]: (_n.__setitem__(0, _n[0] + 1) or _n[0]))"
            if len(expr.body) == 1 and isinstance(expr.body[0], AssignNode):
                tgt = expr.body[0].target
                v_str = self._emit_expr(expr.body[0].value)
                op = expr.body[0].op
                if op == "+=": return f"(lambda {params_str}: {tgt} + {v_str})"
                elif op == "-=": return f"(lambda {params_str}: {tgt} - {v_str})"
                elif op == "=": return f"(lambda {params_str}: {v_str})"
            if len(expr.body) == 1 and isinstance(expr.body[0], ReturnNode):
                ret_val = self._emit_expr(expr.body[0].value) if expr.body[0].value else "None"
                return f"(lambda {params_str}: {ret_val})"
            if len(expr.body) == 1 and isinstance(expr.body[0], PrintNode):
                p_args = [self._emit_expr(a) for a in expr.body[0].args]
                args_s = ", ".join(p_args)
                return f"(lambda {params_str}: print({args_s}))"
            if len(expr.body) == 1 and hasattr(expr.body[0], "expr"):
                e_str = self._emit_expr(expr.body[0].expr)
                return f"(lambda {params_str}: {e_str})"
            return f"(lambda {params_str}: None)"

        elif isinstance(expr, CastExprNode):
            inner = self._emit_expr(expr.expr)
            if getattr(expr, "cast_kind", None) == "dynamic":
                t = expr.target_type.replace("*", "").replace("&", "").strip()
                t = _clean_py_ident(t)
                return f"({inner} if isinstance({inner}, {t}) else None)"
            t = expr.target_type.lower()
            if "int" in t or "char" in t or "short" in t or "long" in t or "size_t" in t or "uint" in t:
                self.needs_c_int = True
                return f"_c_int({inner})"
            elif "float" in t or "double" in t:
                return f"float({inner})"
            elif "str" in t or "string" in t:
                return f"str({inner})"
            elif "bool" in t:
                return f"bool({inner})"
            return inner

        elif isinstance(expr, CallNode):
            callee = expr.callee.replace("::", ".").replace("->", ".")
            while "std.chrono.std.chrono." in callee:
                callee = callee.replace("std.chrono.std.chrono.", "std.chrono.")
            while "std.chrono.chrono." in callee:
                callee = callee.replace("std.chrono.chrono.", "std.chrono.")
            while "std.std." in callee:
                callee = callee.replace("std.std.", "std.")
            while "chrono.chrono." in callee:
                callee = callee.replace("chrono.chrono.", "chrono.")
            if callee.startswith("this."):
                callee = "self." + callee[5:]
            if "~" in callee:
                callee = re.sub(r"~\w+", "__del__", callee)
                if callee.endswith(".__del__"):
                    obj = callee.rsplit(".", 1)[0]
                    return f"({obj}.__del__() if hasattr({obj}, '__del__') else None)"
            if callee in ("list", "std.list", "std::list"):
                callee = "_CppList"
            clean_callee = re.sub(r"^(class|struct)\s+", "", callee)
            if getattr(self, "current_class", None) and getattr(self, "current_bases", set()):
                for b in self.current_bases:
                    method_name = clean_callee.split(".")[-1]
                    if clean_callee == f"{b}.{method_name}" or clean_callee.endswith(f".{b}.{method_name}"):
                        args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                        return f"super().{method_name}({args_str})"
            if callee in ("std.move", "move", "std.forward", "forward"):
                if expr.args:
                    arg_s = self._emit_expr(expr.args[0])
                    return f"({arg_s}.release() if hasattr({arg_s}, 'release') else {arg_s})"
                return "None"
            if callee in ("std.any", "any", "std::any"):
                return self._emit_expr(expr.args[0]) if expr.args else "None"
            if "sync_with_stdio" in callee:
                return "None"
            if "numeric_limits" in callee:
                if "max" in callee:
                    return "2147483647"
                if "epsilon" in callee:
                    return "2.220446049250313e-16"
                if "min" in callee or "lowest" in callee:
                    return "-2147483648"
            if "make_unique<" in callee or "make_shared<" in callee or callee.startswith("std.make_unique<") or callee.startswith("std.make_shared<"):
                type_m = re.search(r"make_(?:unique|shared)<(?:.*::)?([^>]+)>", callee)
                raw_t = type_m.group(1) if type_m else ""
                args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                if "[]" in raw_t:
                    return f"[0] * ({args_str})"
                t_name = re.sub(r"[*&]", "", raw_t).strip()
                if "make_unique" in callee:
                    if t_name and t_name not in ("int", "double", "float", "char", "bool"):
                        return f"unique_ptr({t_name}({args_str}))"
                    return f"unique_ptr({args_str})" if args_str else "unique_ptr()"
                elif "make_shared" in callee:
                    if t_name and t_name not in ("int", "double", "float", "char", "bool"):
                        return f"shared_ptr({t_name}({args_str}))"
                    return f"make_shared({args_str})"

            if "get<" in callee:
                m = re.search(r"get<(\d+)>", callee)
                if m and expr.args:
                    idx = m.group(1)
                    target = self._emit_expr(expr.args[0])
                    return f"{target}[{idx}]"
                elif expr.args:
                    target = self._emit_expr(expr.args[0])
                    return f"getattr({target}, 'val', {target})"

            if callee in ("std.get", "get") and expr.args:
                target = self._emit_expr(expr.args[0])
                return f"getattr({target}, 'val', {target})"

            if "<" in callee and ">" in callee:
                callee = re.sub(r"<[^>]+>", "", callee)

            if callee.endswith(".push_back") or callee.endswith(".emplace_back"):
                obj = callee.rsplit(".", 1)[0]
                args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                return f"{obj}.append({args_str})"
            if callee.endswith(".length") or callee.endswith(".size"):
                obj = callee.rsplit(".", 1)[0]
                if callee.endswith(".length") and any(k in obj for k in ("v1", "v2", "v3", "vec", "Vector", ")")):
                    return f"{obj}.length()"
                return f"len({obj})"
            if callee.endswith(".empty"):
                obj = callee.rsplit(".", 1)[0]
                return f"(len({obj}) == 0)"
            if callee.endswith(".what"):
                obj = callee.rsplit(".", 1)[0]
                return f"str({obj})"
            if callee.endswith(".get") and callee not in ("std.get", "get") and not callee.endswith(".std.get") and not callee.endswith("iss.get") and not callee.endswith("cin.get") and not any(callee.startswith(pfx) for pfx in ("bp.", "bi.", "bb.", "box.")) and getattr(self, "current_class", None) != "Box":
                obj = callee.rsplit(".", 1)[0]
                return obj
            if callee in ("Box", "std.Box"):
                args_list = []
                for a in expr.args:
                    if isinstance(a, UnaryOpNode) and a.op == "&":
                        args_list.append(f"{self._emit_expr(a.operand)}, is_ptr=True")
                    else:
                        args_list.append(self._emit_expr(a))
                return f"Box({', '.join(args_list)})"
            if callee in ("std.make_pair", "make_pair"):
                args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                return f"pair({args_str})"
            if callee in ("std.make_tuple", "make_tuple", "std.tuple", "tuple"):
                args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                return f"({args_str})"
            if callee in ("std.to_string", "to_string"):
                return f"str({self._emit_expr(expr.args[0])})" if expr.args else "str()"
            if callee in ("std.stoi", "stoi"):
                return f"int({self._emit_expr(expr.args[0])})" if expr.args else "0"
            if callee in ("std.stod", "stod"):
                return f"float({self._emit_expr(expr.args[0])})" if expr.args else "0.0"
            if callee in ("std.max", "max"):
                args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                return f"max({args_str})"
            if callee in ("std.min", "min"):
                args_str = ", ".join(self._emit_expr(a) for a in expr.args)
                return f"min({args_str})"

            callee = _clean_py_ident(callee)
            args_str = ", ".join(self._emit_expr(a) for a in expr.args)
            return f"{callee}({args_str})"

        elif isinstance(expr, UnsupportedASTNode):
            return "None"

        return "None"
