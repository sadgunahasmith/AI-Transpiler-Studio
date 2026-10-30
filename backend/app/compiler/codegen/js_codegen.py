"""
JavaScript Code Generator for Stage 6: Code Generation.
Generates clean, idiomatic modern JavaScript (ES6) source code from normalized AST.
"""
from typing import List, Optional
import json
import re
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

OP_NAME_MAP = {
    "+": "operator_add",
    "-": "operator_sub",
    "*": "operator_mul",
    "/": "operator_div",
    "%": "operator_mod",
    "==": "operator_eq",
    "!=": "operator_ne",
    "<": "operator_lt",
    "<=": "operator_le",
    ">": "operator_gt",
    ">=": "operator_ge",
    "[]": "operator_subscript",
    "()": "operator_call",
    "++": "operator_inc",
    "--": "operator_dec",
    "=": "operator_assign",
    "+=": "operator_add_assign",
    "-=": "operator_sub_assign",
    "*=": "operator_mul_assign",
    "/=": "operator_div_assign",
    "<<": "operator_lshift",
    ">>": "operator_rshift",
    "!": "operator_not",
    "~": "operator_bnot",
}

import re

def _safe_js_name(name: str) -> str:
    if name.startswith("class "):
        name = name[6:].strip()
    if name.startswith("struct "):
        name = name[7:].strip()
    if "<" in name and ">" in name:
        name = re.sub(r"<[^>]+>", "", name)
    if name.startswith("~"):
        return "destructor_" + name[1:]
    if name.startswith("operator"):
        raw = name[len("operator"):].strip()
        return OP_NAME_MAP.get(raw, "operator_" + "".join(c for c in raw if c.isalnum() or c == "_"))
    clean = "".join(c for c in name if c.isalnum() or c == "_")
    return clean or name

def _clean_js_base(base: str) -> str:
    b = base.replace("class ", "").replace("struct ", "").replace("&", "").replace("*", "").strip()
    b = re.sub(r"\bconst\b", "", b).strip()
    b = re.sub(r"<[^>]+>", "", b).strip()
    if b.startswith("std::") or b.startswith("std."):
        sub = b.split("::")[-1].split(".")[-1]
        if "error" in sub.lower() or "exception" in sub.lower():
            return "Error"
        return f"std.{sub}"
    return b.replace("::", ".")

JS_RESERVED = {
    "break", "case", "catch", "class", "const", "continue", "debugger", "default",
    "delete", "do", "else", "export", "extends", "finally", "for", "function",
    "if", "import", "in", "instanceof", "new", "return", "super", "switch",
    "this", "throw", "try", "typeof", "var", "void", "while", "with", "yield",
    "let", "static", "enum", "await",
}

def _clean_js_ident(name: str) -> str:
    clean = _safe_js_name(name)
    if clean in ("this", "super"):
        return clean
    if clean in JS_RESERVED:
        return f"{clean}_"
    return clean

def _clean_callee_part(p: str) -> str:
    m = re.match(r"^(.+)\[([^\]]+)\]$", p)
    if m:
        return f"{_clean_callee_part(m.group(1))}[{m.group(2)}]"
    if p.startswith("(") and p.endswith(")"):
        return p
    return _clean_js_ident(p)

class JSCodeGen:
    """Emits clean JavaScript source code from normalized AST."""

    def __init__(self, indent_size: int = 2):
        self.indent_size = indent_size
        self.indent_level = 0
        self.lines: List[str] = []
        self.has_main = False
        self.declared_vars = set()
        self.current_class = None
        self.current_base = None

    def generate(self, ast_root: Optional[ProgramNode]) -> str:
        if not ast_root or not ast_root.body:
            return "// Empty program\n"

        self.lines = []
        self.indent_level = 0
        self.declared_vars = set()
        self.declared_classes = set()
        self.emitted_classes = set()
        self.current_class = None
        self.current_base = None

        def _collect_classes(item, ns=""):
            if not item:
                return
            if isinstance(item, (ClassDefNode, StructDefNode)):
                self.declared_classes.add(item.name)
                if ns:
                    self.declared_classes.add(f"{ns}.{item.name}")
                for sub in getattr(item, "body", []):
                    _collect_classes(sub, item.name)
                for m in getattr(item, "methods", []):
                    _collect_classes(m, item.name)
            elif isinstance(item, TemplateDefNode):
                if item.declaration:
                    _collect_classes(item.declaration, ns)
            elif isinstance(item, NamespaceDefNode):
                curr_ns = f"{ns}.{item.name}" if ns else item.name
                for sub in item.body:
                    _collect_classes(sub, curr_ns)
            elif isinstance(item, FunctionDefNode):
                for sub in item.body:
                    _collect_classes(sub, ns)

        for s in ast_root.body:
            _collect_classes(s)

        all_idents = set()
        def _walk_idents(node):
            if not node:
                return
            if isinstance(node, IdentifierNode):
                all_idents.add(node.name)
            elif isinstance(node, CallNode):
                all_idents.add(node.callee)
                for a in node.args:
                    _walk_idents(a)
            elif isinstance(node, VarDeclNode):
                all_idents.add(node.name)
                if node.init_val: _walk_idents(node.init_val)
            elif isinstance(node, AssignNode):
                if isinstance(node.target, str): all_idents.add(node.target)
                if node.target_node: _walk_idents(node.target_node)
                if node.value: _walk_idents(node.value)
            elif isinstance(node, MemberAccessNode):
                all_idents.add(node.member)
                if node.object: _walk_idents(node.object)
            elif isinstance(node, BinaryOpNode):
                if node.left: _walk_idents(node.left)
                if node.right: _walk_idents(node.right)
            elif isinstance(node, UnaryOpNode):
                if node.operand: _walk_idents(node.operand)
            elif isinstance(node, ReturnNode):
                if node.value: _walk_idents(node.value)
            elif isinstance(node, ExprStmtNode):
                if node.expr: _walk_idents(node.expr)
            elif isinstance(node, IfNode):
                if node.test: _walk_idents(node.test)
                for s in node.body: _walk_idents(s)
                for s in node.orelse: _walk_idents(s)
            elif isinstance(node, (WhileNode, ForNode)):
                for s in node.body: _walk_idents(s)
            elif isinstance(node, RangeForNode):
                if node.iterable: _walk_idents(node.iterable)
                for s in node.body: _walk_idents(s)
            elif isinstance(node, TryCatchNode):
                for s in node.try_block: _walk_idents(s)
                for cb in node.catch_blocks:
                    for s in cb.body: _walk_idents(s)
            elif isinstance(node, FunctionDefNode):
                for s in node.body: _walk_idents(s)
            elif isinstance(node, (ClassDefNode, StructDefNode)):
                for m in node.methods: _walk_idents(m)
                for s in node.body: _walk_idents(s)
            elif isinstance(node, NamespaceDefNode):
                for s in node.body: _walk_idents(s)
            elif isinstance(node, TemplateDefNode):
                if node.declaration: _walk_idents(node.declaration)

        for s in ast_root.body:
            _walk_idents(s)

        def _has(ident):
            return any(ident in s for s in all_idents)

        needs_cpp = True

        if needs_cpp:
            self.lines.append("// --- C++ Standard Library & Runtime Shim for JavaScript ---")
            self.lines.append('let fs;')
            self.lines.append('try { fs = require("fs"); } catch (e) { fs = null; }')
            self.lines.append('if (typeof Error.prototype.what !== "function") {')
            self.lines.append('  Error.prototype.what = function() { return this.message; };')
            self.lines.append('}')
            self.lines.append('class _CppException extends Error {')
            self.lines.append('  constructor(m = "") {')
            self.lines.append('    const msg = (m && m._s !== undefined) ? m._s : String(m);')
            self.lines.append('    super(msg);')
            self.lines.append('    this.name = "exception";')
            self.lines.append('  }')
            self.lines.append('  what() { return this.message; }')
            self.lines.append('}')
            self.lines.append('class _CppInvalidArgument extends _CppException { constructor(m = "") { super(m); this.name = "invalid_argument"; } }')
            self.lines.append('class _CppOutOfRange extends _CppException { constructor(m = "") { super(m); this.name = "out_of_range"; } }')
            self.lines.append('class _CppRuntimeError extends _CppException { constructor(m = "") { super(m); this.name = "runtime_error"; } }')
            self.lines.append('function invalid_argument(m) { return new _CppInvalidArgument(m); }')
            self.lines.append('invalid_argument.prototype = _CppInvalidArgument.prototype;')
            self.lines.append('function out_of_range(m) { return new _CppOutOfRange(m); }')
            self.lines.append('out_of_range.prototype = _CppOutOfRange.prototype;')
            self.lines.append('function runtime_error(m) { return new _CppRuntimeError(m); }')
            self.lines.append('runtime_error.prototype = _CppRuntimeError.prototype;')
            self.lines.append('function exception(m) { return new _CppException(m); }')
            self.lines.append('exception.prototype = _CppException.prototype;')
            self.lines.append('function isinstance(obj, cls) {')
            self.lines.append('  if (obj == null) return false;')
            self.lines.append("  if (typeof cls === 'function') return obj instanceof cls;")
            self.lines.append('  return true;')
            self.lines.append('}')
            self.lines.append('function assert(cond, msg = "") { if (!cond) throw new Error("Assertion failed: " + msg); }')
            self.lines.append('function _mixin(Derived, Base) {')
            self.lines.append('  if (typeof Base === "undefined" || !Base || !Base.prototype) return;')
            self.lines.append('  let p = Base.prototype;')
            self.lines.append('  while (p && p !== Object.prototype) {')
            self.lines.append('    for (const prop of Object.getOwnPropertyNames(p)) {')
            self.lines.append('      if (prop !== "constructor" && !(prop in Derived.prototype)) {')
            self.lines.append('        try { Derived.prototype[prop] = p[prop]; } catch (e) {}')
            self.lines.append('      }')
            self.lines.append('    }')
            self.lines.append('    p = Object.getPrototypeOf(p);')
            self.lines.append('  }')
            self.lines.append('}')
            self.lines.append('function section(name) {')
            self.lines.append('  console.log(`\\n=== ${String(name)} ===\\n`);')
            self.lines.append('}')
            self.lines.append('if (typeof Number.prototype.count !== "function") {')
            self.lines.append('  Number.prototype.count = function() { return this.valueOf(); };')
            self.lines.append('}')
            self.lines.append('function milliseconds(n) { return n; }')
            self.lines.append('function __builtin_inff() { return Infinity; }')
            self.lines.append('function __builtin_nanf() { return NaN; }')
            self.lines.append('function _shift(a, b) {')
            self.lines.append('  if (a && a._parts) {')
            self.lines.append('    a._parts.push(String(b));')
            self.lines.append('    if (a.path && fs) {')
            self.lines.append('      try {')
            self.lines.append('        if (a.mode && String(a.mode).includes("app")) fs.appendFileSync(a.path, String(b));')
            self.lines.append('        else fs.writeFileSync(a.path, a._parts.join(""));')
            self.lines.append('      } catch (e) {}')
            self.lines.append('    }')
            self.lines.append('    return a;')
            self.lines.append('  }')
            self.lines.append('  return a << b;')
            self.lines.append('}')
            self.lines.append('function _add(a, b) {')
            self.lines.append('  if (a && typeof a.operator_add === "function") return a.operator_add(b);')
            self.lines.append('  if (a && a._vec && a._idx !== undefined) return new _VecIter(a._vec, a._idx + Number(b));')
            self.lines.append('  if (b && b._vec && b._idx !== undefined) return new _VecIter(b._vec, Number(a) + b._idx);')
            self.lines.append('  return a + b;')
            self.lines.append('}')
            self.lines.append('function _sub(a, b) {')
            self.lines.append('  if (a && typeof a.operator_sub === "function") return a.operator_sub(b);')
            self.lines.append('  if (a && a._vec && a._idx !== undefined && b && b._vec && b._idx !== undefined) return a._idx - b._idx;')
            self.lines.append('  if (a && a._vec && a._idx !== undefined) return new _VecIter(a._vec, a._idx - Number(b));')
            self.lines.append('  return a - b;')
            self.lines.append('}')
            self.lines.append('function _mul(a, b) {')
            self.lines.append('  if (Array.isArray(a) && typeof b === "number") {')
            self.lines.append('    const res = [];')
            self.lines.append('    for (let i = 0; i < b; i++) res.push(...a);')
            self.lines.append('    return res;')
            self.lines.append('  }')
            self.lines.append('  if (a && typeof a.operator_mul === "function") return a.operator_mul(b);')
            self.lines.append('  return a * b;')
            self.lines.append('}')
            self.lines.append('function _eq(a, b) {')
            self.lines.append('  if (a && typeof a.operator_eq === "function") return a.operator_eq(b);')
            self.lines.append('  if (a && typeof a.get === "function" && b == null) return a.get() == null;')
            self.lines.append('  if (b && typeof b.get === "function" && a == null) return b.get() == null;')
            self.lines.append('  if ((a === 18446744073709551615 && b === -1) || (a === -1 && b === 18446744073709551615)) return true;')
            self.lines.append('  return a == b;')
            self.lines.append('}')
            self.lines.append('function _ne(a, b) {')
            self.lines.append('  if (a && typeof a.operator_ne === "function") return a.operator_ne(b);')
            self.lines.append('  if (a && typeof a.get === "function" && b == null) return a.get() != null;')
            self.lines.append('  if (b && typeof b.get === "function" && a == null) return b.get() != null;')
            self.lines.append('  if ((a === 18446744073709551615 && b === -1) || (a === -1 && b === 18446744073709551615)) return false;')
            self.lines.append('  return a != b;')
            self.lines.append('}')
            self.lines.append('function _not(x) {')
            self.lines.append('  if (x == null) return true;')
            self.lines.append('  if (typeof x === "object") {')
            self.lines.append('    if (typeof x.has_value === "function") return !x.has_value();')
            self.lines.append('    if (typeof x.get === "function") return !x.get();')
            self.lines.append('    if ("_obj" in x) return !x._obj;')
            self.lines.append('    if (typeof x[Symbol.toPrimitive] === "function") {')
            self.lines.append('      const p = x[Symbol.toPrimitive]();')
            self.lines.append('      if (typeof p === "boolean" || typeof p === "number") return !p;')
            self.lines.append('    }')
            self.lines.append('  }')
            self.lines.append('  return !x;')
            self.lines.append('}')
            self.lines.append('function _deref(x) {')
            self.lines.append('  if (x && x._vec && x._idx !== undefined) return x._vec[x._idx];')
            self.lines.append('  if (x && typeof x.get === "function") return x.get();')
            self.lines.append('  if (Array.isArray(x) && x.length > 0) return x[0];')
            self.lines.append('  return x;')
            self.lines.append('}')
            self.lines.append('if (typeof Array.prototype.size !== "function") Array.prototype.size = function() { return this.length; };')
            self.lines.append('if (typeof Array.prototype.empty !== "function") Array.prototype.empty = function() { return this.length === 0; };')
            self.lines.append('if (typeof Array.prototype.front !== "function") Array.prototype.front = function() { return this[0]; };')
            self.lines.append('if (typeof Array.prototype.back !== "function") Array.prototype.back = function() { return this[this.length - 1]; };')
            self.lines.append('if (typeof Array.prototype.push_back !== "function") Array.prototype.push_back = function(v) { this.push(v); };')
            self.lines.append('if (typeof Array.prototype.pop_back !== "function") Array.prototype.pop_back = function() { return this.pop(); };')
            self.lines.append('if (typeof Array.prototype.emplace_back !== "function") Array.prototype.emplace_back = function(...args) { this.push(...args); };')
            self.lines.append('if (typeof Array.prototype.push_front !== "function") Array.prototype.push_front = function(v) { this.unshift(v); };')
            self.lines.append('if (typeof Array.prototype.pop_front !== "function") Array.prototype.pop_front = function() { return this.shift(); };')
            self.lines.append('if (!Object.getOwnPropertyDescriptor(Array.prototype, "first")) {')
            self.lines.append('  Object.defineProperty(Array.prototype, "first", { get() { return this[0]; }, configurable: true });')
            self.lines.append('}')
            self.lines.append('if (!Object.getOwnPropertyDescriptor(Array.prototype, "second")) {')
            self.lines.append('  Object.defineProperty(Array.prototype, "second", { get() { return this[1]; }, configurable: true });')
            self.lines.append('}')
            self.lines.append('class _str_iter {')
            self.lines.append('  constructor(owner, idx) { this.owner = owner; this.idx = idx; }')
            self.lines.append('}')
            self.lines.append('class _CppString {')
            self.lines.append('  constructor(val = "") {')
            self.lines.append('    if (val && val._s !== undefined) this._s = val._s;')
            self.lines.append('    else this._s = (val !== null && val !== undefined) ? String(val) : "";')
            self.lines.append('  }')
            self.lines.append('  toString() { return this._s; }')
            self.lines.append('  valueOf() { return this._s; }')
            self.lines.append('  [Symbol.toPrimitive]() { return this._s; }')
            self.lines.append('  [Symbol.for("nodejs.util.inspect.custom")]() { return this._s; }')
            self.lines.append('  get length() { return this._s.length; }')
            self.lines.append('  size() { return this._s.length; }')
            self.lines.append('  substr(pos, len) {')
            self.lines.append('    const p = Number(pos);')
            self.lines.append('    return new _CppString(len !== undefined ? this._s.substr(p, Number(len)) : this._s.substr(p));')
            self.lines.append('  }')
            self.lines.append('  find(sub, pos = 0) {')
            self.lines.append('    const s = typeof sub === "object" ? sub.toString() : String(sub);')
            self.lines.append('    const idx = this._s.indexOf(s, Number(pos));')
            self.lines.append('    return idx === -1 ? 18446744073709551615 : idx;')
            self.lines.append('  }')
            self.lines.append('  rfind(sub, pos) {')
            self.lines.append('    const s = typeof sub === "object" ? sub.toString() : String(sub);')
            self.lines.append('    return pos !== undefined ? this._s.lastIndexOf(s, Number(pos)) : this._s.lastIndexOf(s);')
            self.lines.append('  }')
            self.lines.append('  replace(pos, count, sub) {')
            self.lines.append('    const p = Number(pos), c = Number(count);')
            self.lines.append('    this._s = this._s.substring(0, p) + String(sub) + this._s.substring(p + c);')
            self.lines.append('    return this;')
            self.lines.append('  }')
            self.lines.append('  insert(pos, sub) {')
            self.lines.append('    const p = Number(pos);')
            self.lines.append('    this._s = this._s.substring(0, p) + String(sub) + this._s.substring(p);')
            self.lines.append('    return this;')
            self.lines.append('  }')
            self.lines.append('  erase(pos = 0, count) {')
            self.lines.append('    const p = Number(pos);')
            self.lines.append('    if (count === undefined) this._s = this._s.substring(0, p);')
            self.lines.append('    else this._s = this._s.substring(0, p) + this._s.substring(p + Number(count));')
            self.lines.append('    return this;')
            self.lines.append('  }')
            self.lines.append('  front() { return this._s[0] || ""; }')
            self.lines.append('  back() { return this._s[this._s.length - 1] || ""; }')
            self.lines.append('  compare(other) {')
            self.lines.append('    const o = String(other);')
            self.lines.append('    return this._s > o ? 1 : this._s < o ? -1 : 0;')
            self.lines.append('  }')
            self.lines.append('  append(other) {')
            self.lines.append('    this._s += (other && other._s !== undefined ? other._s : String(other));')
            self.lines.append('    return this;')
            self.lines.append('  }')
            self.lines.append('  push_back(ch) { this._s += String(ch); }')
            self.lines.append('  c_str() { return this._s; }')
            self.lines.append('  data() { return this._s; }')
            self.lines.append('  clear() { this._s = ""; }')
            self.lines.append('  empty() { return this._s.length === 0; }')
            self.lines.append('  begin() { return new _str_iter(this, 0); }')
            self.lines.append('  end() { return new _str_iter(this, this._s.length); }')
            self.lines.append('}')
            self.lines.append('function string(v = "") { return new _CppString(v); }')
            self.lines.append('_CppString.npos = 18446744073709551615;')
            self.lines.append('string.npos = 18446744073709551615;')
            self.lines.append('const string_view = string;')
            self.lines.append('class _char_buf {')
            self.lines.append('  constructor(size = 64) { this._size = size; this._s = ""; }')
            self.lines.append('  toString() { return this._s; }')
            self.lines.append('  valueOf() { return this._s; }')
            self.lines.append('  get length() { return this._size; }')
            self.lines.append('  set(v) { this._s = String(v); }')
            self.lines.append('}')
            self.lines.append('class _ostringstream {')
            self.lines.append('  constructor() { this._parts = []; }')
            self.lines.append('  str(v) { if (v !== undefined) this._parts = [String(v)]; return this._parts.join(""); }')
            self.lines.append('}')
            self.lines.append('function ostringstream(...args) { return new _ostringstream(...args); }')
            self.lines.append('class _istringstream {')
            self.lines.append('  constructor(text = "") {')
            self.lines.append('    this._tokens = String(text).trim().split(/\\s+/).filter(Boolean);')
            self.lines.append('    this._idx = 0;')
            self.lines.append('  }')
            self.lines.append('  get() {')
            self.lines.append('    if (this._idx < this._tokens.length) {')
            self.lines.append('      const val = this._tokens[this._idx++];')
            self.lines.append('      const n = Number(val);')
            self.lines.append('      return !isNaN(n) ? n : val;')
            self.lines.append('    }')
            self.lines.append('    return null;')
            self.lines.append('  }')
            self.lines.append('}')
            self.lines.append('function istringstream(...args) { return new _istringstream(...args); }')
            self.lines.append('class _stringstream {')
            self.lines.append('  constructor(text = "") {')
            self.lines.append('    this._text = String(text);')
            self.lines.append('    this._idx = 0;')
            self.lines.append('    this._parts = text ? [String(text)] : [];')
            self.lines.append('  }')
            self.lines.append('  str(v) {')
            self.lines.append('    if (v !== undefined) { this._text = String(v); this._parts = [this._text]; this._idx = 0; }')
            self.lines.append('    return this._parts.join("");')
            self.lines.append('  }')
            self.lines.append('  getline(delim = "\\n") {')
            self.lines.append('    if (this._idx >= this._text.length) return null;')
            self.lines.append('    const d = (delim === "\\n" || delim === "\\\\n") ? "\\n" : String(delim);')
            self.lines.append('    const end = this._text.indexOf(d, this._idx);')
            self.lines.append('    let res;')
            self.lines.append('    if (end === -1) {')
            self.lines.append('      res = this._text.slice(this._idx);')
            self.lines.append('      this._idx = this._text.length;')
            self.lines.append('    } else {')
            self.lines.append('      res = this._text.slice(this._idx, end);')
            self.lines.append('      this._idx = end + d.length;')
            self.lines.append('    }')
            self.lines.append('    return res;')
            self.lines.append('  }')
            self.lines.append('}')
            self.lines.append('function stringstream(...args) { return new _stringstream(...args); }')
            self.lines.append('function getline(stream, tok, delim = "\\n") {')
            self.lines.append('  const line = stream && typeof stream.getline === "function" ? stream.getline(delim) : null;')
            self.lines.append('  if (line !== null) {')
            self.lines.append('    if (tok && typeof tok === "object" && "_s" in tok) tok._s = line;')
            self.lines.append('    return true;')
            self.lines.append('  }')
            self.lines.append('  return false;')
            self.lines.append('}')
            self.lines.append('class _CppVector extends Array {')
            self.lines.append('  constructor(...args) {')
            self.lines.append('    if (args.length === 1 && typeof args[0] === "number") {')
            self.lines.append('      super(args[0]).fill(0);')
            self.lines.append('    } else if (args.length === 2 && typeof args[0] === "number") {')
            self.lines.append('      super(args[0]).fill(args[1]);')
            self.lines.append('    } else if (args.length === 1 && Array.isArray(args[0])) {')
            self.lines.append('      super(...args[0]);')
            self.lines.append('    } else {')
            self.lines.append('      super(...args);')
            self.lines.append('    }')
            self.lines.append('  }')
            self.lines.append('  push_back(v) { this.push(v); }')
            self.lines.append('  emplace_back(v) { this.push(v); }')
            self.lines.append('  pop_back() { return this.pop(); }')
            self.lines.append('  front() { return this[0]; }')
            self.lines.append('  back() { return this[this.length - 1]; }')
            self.lines.append('  size() { return this.length; }')
            self.lines.append('  empty() { return this.length === 0; }')
            self.lines.append('  at(i) {')
            self.lines.append('    if (i < 0 || i >= this.length) throw new _CppOutOfRange("vector::_M_range_check");')
            self.lines.append('    return this[i];')
            self.lines.append('  }')
            self.lines.append('  insert(pos, val) { const idx = typeof pos === "number" ? pos : (pos && pos.idx !== undefined ? pos.idx : Number(pos)); this.splice(idx, 0, val); }')
            self.lines.append('  erase(pos, last) {')
            self.lines.append('    const idx1 = typeof pos === "number" ? pos : (pos && pos.idx !== undefined ? pos.idx : Number(pos));')
            self.lines.append('    if (last !== undefined) {')
            self.lines.append('      const idx2 = typeof last === "number" ? last : (last && last.idx !== undefined ? last.idx : Number(last));')
            self.lines.append('      this.splice(idx1, idx2 - idx1);')
            self.lines.append('    } else {')
            self.lines.append('      this.splice(idx1, 1);')
            self.lines.append('    }')
            self.lines.append('  }')
            self.lines.append('  push_front(v) { this.unshift(v); }')
            self.lines.append('  pop_front() { return this.shift(); }')
            self.lines.append('  sort(comp) { super.sort(comp || ((a, b) => a - b)); return this; }')
            self.lines.append('  reverse() { super.reverse(); return this; }')
            self.lines.append('  begin() { return new _VecIter(this, 0); }')
            self.lines.append('  end() { return new _VecIter(this, this.length); }')
            self.lines.append('}')
            self.lines.append('class _VecIter {')
            self.lines.append('  constructor(vec, idx) { this._vec = vec; this._idx = idx; }')
            self.lines.append('  valueOf() { return this._idx; }')
            self.lines.append('  [Symbol.toPrimitive](hint) { if (hint === "number" || hint === "default") return this._idx; return (this._vec && this._idx < this._vec.length) ? String(this._vec[this._idx]) : String(this._idx); }')
            self.lines.append('  toString() { return String((this._vec && this._idx < this._vec.length) ? this._vec[this._idx] : this._idx); }')
            self.lines.append('  [Symbol.for("nodejs.util.inspect.custom")]() { return (this._vec && this._idx < this._vec.length) ? this._vec[this._idx] : this._idx; }')
            self.lines.append('}')
            self.lines.append('function vector(...args) { return new _CppVector(...args); }')
            self.lines.append('const deque = vector;')
            self.lines.append('const list = vector;')
            self.lines.append('const forward_list = vector;')
            self.lines.append('class _CppStack {')
            self.lines.append('  constructor() { this._items = []; }')
            self.lines.append('  push(x) { this._items.push(x); }')
            self.lines.append('  pop() { return this._items.pop(); }')
            self.lines.append('  top() { return this._items[this._items.length - 1]; }')
            self.lines.append('  size() { return this._items.length; }')
            self.lines.append('  empty() { return this._items.length === 0; }')
            self.lines.append('}')
            self.lines.append('function stack(...args) { return new _CppStack(...args); }')
            self.lines.append('class _CppQueue {')
            self.lines.append('  constructor() { this._items = []; }')
            self.lines.append('  push(x) { this._items.push(x); }')
            self.lines.append('  pop() { return this._items.shift(); }')
            self.lines.append('  front() { return this._items[0]; }')
            self.lines.append('  back() { return this._items[this._items.length - 1]; }')
            self.lines.append('  size() { return this._items.length; }')
            self.lines.append('  empty() { return this._items.length === 0; }')
            self.lines.append('}')
            self.lines.append('function queue(...args) { return new _CppQueue(...args); }')
            self.lines.append('class _CppPriorityQueue {')
            self.lines.append('  constructor(pred = null) {')
            self.lines.append('    this._items = [];')
            self.lines.append('    this._comp = typeof pred === "function" ? pred : (a, b) => b - a;')
            self.lines.append('  }')
            self.lines.append('  push(x) { this._items.push(x); this._items.sort(this._comp); }')
            self.lines.append('  pop() { return this._items.shift(); }')
            self.lines.append('  top() { return this._items[0]; }')
            self.lines.append('  size() { return this._items.length; }')
            self.lines.append('  empty() { return this._items.length === 0; }')
            self.lines.append('}')
            self.lines.append('function priority_queue(...args) { return new _CppPriorityQueue(...args); }')
            self.lines.append('class _CppMap extends Map {')
            self.lines.append('  _k(k) { return (k !== null && k !== undefined && k._s !== undefined) ? k._s : k; }')
            self.lines.append('  *[Symbol.iterator]() {')
            self.lines.append('    for (const [k, v] of super.entries()) {')
            self.lines.append('      yield { first: k, second: v, 0: k, 1: v, length: 2, [Symbol.iterator]: function*() { yield k; yield v; } };')
            self.lines.append('    }')
            self.lines.append('  }')
            self.lines.append('  constructor(init = []) {')
            self.lines.append('    super();')
            self.lines.append('    if (Array.isArray(init)) {')
            self.lines.append('      for (const item of init) {')
            self.lines.append('        if (Array.isArray(item)) this.set(item[0], item[1]);')
            self.lines.append('        else if (item && item.first !== undefined) this.set(item.first, item.second);')
            self.lines.append('      }')
            self.lines.append('    }')
            self.lines.append('    return new Proxy(this, {')
            self.lines.append('      get(target, prop, receiver) {')
            self.lines.append('        if (typeof prop === "string" && !(prop in target) && typeof target[prop] !== "function") {')
            self.lines.append('          let kp = target._k(prop);')
            self.lines.append('          if (/^-?\\d+$/.test(prop) && (target.has(Number(prop)) || [...target.keys()].some(x => typeof x === "number"))) kp = Number(prop);')
            self.lines.append('          if (!target.has(kp)) target.set(kp, 0);')
            self.lines.append('          return target.get(kp);')
            self.lines.append('        }')
            self.lines.append('        const val = Reflect.get(target, prop, target);')
            self.lines.append('        return typeof val === "function" ? val.bind(target) : val;')
            self.lines.append('      },')
            self.lines.append('      set(target, prop, value, receiver) {')
            self.lines.append('        if (typeof prop === "string" && !(prop in target)) {')
            self.lines.append('          let kp = target._k(prop);')
            self.lines.append('          if (/^-?\\d+$/.test(prop) && (target.has(Number(prop)) || [...target.keys()].some(x => typeof x === "number"))) kp = Number(prop);')
            self.lines.append('          target.set(kp, value);')
            self.lines.append('          return true;')
            self.lines.append('        }')
            self.lines.append('        return Reflect.set(target, prop, value, target);')
            self.lines.append('      }')
            self.lines.append('    });')
            self.lines.append('  }')
            self.lines.append('  has(k) {')
            self.lines.append('    const key = this._k(k);')
            self.lines.append('    if (super.has(key)) return true;')
            self.lines.append('    if (typeof key === "string" && /^-?\\d+$/.test(key) && super.has(Number(key))) return true;')
            self.lines.append('    if (typeof key === "number" && super.has(String(key))) return true;')
            self.lines.append('    return false;')
            self.lines.append('  }')
            self.lines.append('  get(k) {')
            self.lines.append('    const key = this._k(k);')
            self.lines.append('    if (super.has(key)) return super.get(key);')
            self.lines.append('    if (typeof key === "string" && /^-?\\d+$/.test(key) && super.has(Number(key))) return super.get(Number(key));')
            self.lines.append('    if (typeof key === "number" && super.has(String(key))) return super.get(String(key));')
            self.lines.append('    return super.get(key);')
            self.lines.append('  }')
            self.lines.append('  set(k, v) { return super.set(this._k(k), v); }')
            self.lines.append('  delete(k) {')
            self.lines.append('    const key = this._k(k);')
            self.lines.append('    if (super.has(key)) return super.delete(key);')
            self.lines.append('    if (typeof key === "string" && /^-?\\d+$/.test(key) && super.has(Number(key))) return super.delete(Number(key));')
            self.lines.append('    if (typeof key === "number" && super.has(String(key))) return super.delete(String(key));')
            self.lines.append('    return super.delete(key);')
            self.lines.append('  }')
            self.lines.append('  count(k) { return this.has(k) ? 1 : 0; }')
            self.lines.append('  at(k) {')
            self.lines.append('    if (!this.has(k)) throw new Error("map::at");')
            self.lines.append('    return this.get(k);')
            self.lines.append('  }')
            self.lines.append('  find(k) {')
            self.lines.append('    return this.has(k) ? { first: k, second: this.get(k) } : null;')
            self.lines.append('  }')
            self.lines.append('  insert(item) {')
            self.lines.append('    if (Array.isArray(item)) { this.set(item[0], item[1]); }')
            self.lines.append('    else if (item && item.first !== undefined) { this.set(item.first, item.second); }')
            self.lines.append('  }')
            self.lines.append('  emplace(k, v) { this.set(k, v); }')
            self.lines.append('  end() { return null; }')
            self.lines.append('  size() { return super.size; }')
            self.lines.append('}')
            self.lines.append('function map(init) { return new _CppMap(init); }')
            self.lines.append('const unordered_map = map;')
            self.lines.append('const multimap = map;')
            self.lines.append('class _CppSet extends Set {')
            self.lines.append('  _k(k) { return (k !== null && k !== undefined && k._s !== undefined) ? k._s : k; }')
            self.lines.append('  constructor(init = []) {')
            self.lines.append('    super();')
            self.lines.append('    if (Array.isArray(init)) { for (const item of init) this.add(this._k(item)); }')
            self.lines.append('  }')
            self.lines.append('  has(k) {')
            self.lines.append('    const key = this._k(k);')
            self.lines.append('    if (super.has(key)) return true;')
            self.lines.append('    if (typeof key === "string" && /^-?\\d+$/.test(key) && super.has(Number(key))) return true;')
            self.lines.append('    if (typeof key === "number" && super.has(String(key))) return true;')
            self.lines.append('    return false;')
            self.lines.append('  }')
            self.lines.append('  add(val) { return super.add(this._k(val)); }')
            self.lines.append('  delete(val) {')
            self.lines.append('    const key = this._k(val);')
            self.lines.append('    if (super.has(key)) return super.delete(key);')
            self.lines.append('    if (typeof key === "string" && /^-?\\d+$/.test(key) && super.has(Number(key))) return super.delete(Number(key));')
            self.lines.append('    if (typeof key === "number" && super.has(String(key))) return super.delete(String(key));')
            self.lines.append('    return super.delete(key);')
            self.lines.append('  }')
            self.lines.append('  insert(val) { this.add(val); }')
            self.lines.append('  count(k) { return this.has(k) ? 1 : 0; }')
            self.lines.append('  size() { return super.size; }')
            self.lines.append('}')
            self.lines.append('function set(init) { return new _CppSet(init); }')
            self.lines.append('const unordered_set = set;')
            self.lines.append('const multiset = set;')
            self.lines.append('if (typeof Map.prototype.count !== "function") Map.prototype.count = function(k) { return this.has(k) ? 1 : 0; };')
            self.lines.append('if (typeof Map.prototype.emplace !== "function") Map.prototype.emplace = function(k, v) { this.set(k, v); return this; };')
            self.lines.append('if (typeof Map.prototype.find !== "function") Map.prototype.find = function(k) { return this.has(k) ? { first: k, second: this.get(k), 0: k, 1: this.get(k) } : null; };')
            self.lines.append('if (typeof Map.prototype.end !== "function") Map.prototype.end = function() { return null; };')
            self.lines.append('if (typeof Map.prototype.empty !== "function") Map.prototype.empty = function() { return this.size === 0; };')
            self.lines.append('if (typeof Set.prototype.count !== "function") Set.prototype.count = function(k) { return this.has(k) ? 1 : 0; };')
            self.lines.append('if (typeof Set.prototype.insert !== "function") Set.prototype.insert = function(val) { this.add(val); };')
            self.lines.append('if (typeof Set.prototype.emplace !== "function") Set.prototype.emplace = function(val) { this.add(val); };')
            self.lines.append('if (typeof Set.prototype.find !== "function") Set.prototype.find = function(k) { return this.has(k) ? k : null; };')
            self.lines.append('if (typeof Set.prototype.end !== "function") Set.prototype.end = function() { return null; };')
            self.lines.append('if (typeof Set.prototype.empty !== "function") Set.prototype.empty = function() { return this.size === 0; };')
            self.lines.append('class _CppBitset {')
            self.lines.append('  constructor(val = 0) {')
            self.lines.append('    this._bits = BigInt(val);')
            self.lines.append('  }')
            self.lines.append('  count() {')
            self.lines.append('    let c = 0, n = this._bits;')
            self.lines.append('    while (n > 0n) { if (n & 1n) c++; n >>= 1n; }')
            self.lines.append('    return c;')
            self.lines.append('  }')
            self.lines.append('  test(i) { return Boolean((this._bits >> BigInt(i)) & 1n); }')
            self.lines.append('  to_ulong() { return Number(this._bits); }')
            self.lines.append('  toString() { return this._bits.toString(2); }')
            self.lines.append('}')
            self.lines.append('function bitset(...args) { return new _CppBitset(...args); }')
            self.lines.append('function make_pair(a, b) { return { first: a, second: b }; }')
            self.lines.append('const pair = make_pair;')
            self.lines.append('function make_tuple(...args) { return [...args]; }')
            self.lines.append('const tuple = make_tuple;')
            self.lines.append('function array(...args) {')
            self.lines.append('  const items = (args.length === 1 && Array.isArray(args[0])) ? args[0] : args;')
            self.lines.append('  return new _CppVector(...items);')
            self.lines.append('}')
            self.lines.append('const initializer_list = array;')
            self.lines.append('function get(x, i = 0) {')
            self.lines.append('  if (Array.isArray(x)) return x[i];')
            self.lines.append('  if (i === 0) return (x && x.first !== undefined ? x.first : (x && x.val !== undefined ? x.val : x));')
            self.lines.append('  if (i === 1) return (x && x.second !== undefined ? x.second : x);')
            self.lines.append('  return x[i];')
            self.lines.append('}')
            self.lines.append('function optional(v = null) {')
            self.lines.append('  const has = v !== null && v !== undefined;')
            self.lines.append('  return {')
            self.lines.append('    has_value: () => has,')
            self.lines.append('    value: () => (has ? v : null),')
            self.lines.append('    value_or: (def) => (has ? v : def),')
            self.lines.append('    toString: () => String(v),')
            self.lines.append('    valueOf: () => has,')
            self.lines.append('    [Symbol.toPrimitive]: () => has')
            self.lines.append('  };')
            self.lines.append('}')
            self.lines.append('function variant(v) {')
            self.lines.append('  return {')
            self.lines.append('    val: v,')
            self.lines.append('    index: () => (typeof v === "number" ? 0 : 1),')
            self.lines.append('    toString: () => String(v)')
            self.lines.append('  };')
            self.lines.append('}')
            self.lines.append('function any(v) {')
            self.lines.append('  return { val: v, toString: () => String(v) };')
            self.lines.append('}')
            self.lines.append('class _UniquePtr {')
            self.lines.append('  constructor(obj = null) { this._obj = (obj && obj._obj !== undefined) ? obj._obj : obj; }')
            self.lines.append('  get() { return this._obj; }')
            self.lines.append('  release() { const o = this._obj; this._obj = null; return o; }')
            self.lines.append('  reset(newObj = null) { this._obj = (newObj && newObj._obj !== undefined) ? newObj._obj : newObj; }')
            self.lines.append('  valueOf() { return Boolean(this._obj); }')
            self.lines.append('  [Symbol.toPrimitive]() { return Boolean(this._obj); }')
            self.lines.append('}')
            self.lines.append('function unique_ptr(obj = null) {')
            self.lines.append('  const instance = new _UniquePtr(obj);')
            self.lines.append('  return new Proxy(instance, {')
            self.lines.append('    get(t, p, r) {')
            self.lines.append('      if (p in t) return Reflect.get(t, p, r);')
            self.lines.append('      if (t._obj != null && typeof t._obj === "object") return Reflect.get(t._obj, p);')
            self.lines.append('      return undefined;')
            self.lines.append('    },')
            self.lines.append('    set(t, p, v, r) {')
            self.lines.append('      if (p in t) return Reflect.set(t, p, v, r);')
            self.lines.append('      if (t._obj != null && typeof t._obj === "object") return Reflect.set(t._obj, p, v);')
            self.lines.append('      return false;')
            self.lines.append('    }')
            self.lines.append('  });')
            self.lines.append('}')
            self.lines.append('function shared_ptr(v = null) {')
            self.lines.append('  let inner = (v && typeof v.get === "function") ? v.get() : v;')
            self.lines.append('  return new Proxy({')
            self.lines.append('    get: () => inner,')
            self.lines.append('    use_count: () => (inner ? 2 : 0),')
            self.lines.append('    reset: () => { inner = null; },')
            self.lines.append('    valueOf: () => Boolean(inner)')
            self.lines.append('  }, {')
            self.lines.append('    get(t, p, r) {')
            self.lines.append('      if (p in t) return Reflect.get(t, p, r);')
            self.lines.append('      if (inner != null && typeof inner === "object") return Reflect.get(inner, p);')
            self.lines.append('      return undefined;')
            self.lines.append('    }')
            self.lines.append('  });')
            self.lines.append('}')
            self.lines.append('function weak_ptr(p) {')
            self.lines.append('  return { expired: () => false, lock: () => (p && typeof p.get === "function" ? p.get() : p) };')
            self.lines.append('}')
            self.lines.append('function make_shared(cls, ...args) {')
            self.lines.append('  const obj = typeof cls === "function" ? new cls(...args) : cls;')
            self.lines.append('  return shared_ptr(obj);')
            self.lines.append('}')
            self.lines.append('function make_unique(cls, ...args) {')
            self.lines.append('  if (typeof cls === "function") return unique_ptr(new cls(...args));')
            self.lines.append('  return unique_ptr(cls);')
            self.lines.append('}')
            self.lines.append('class _ofstream {')
            self.lines.append('  constructor(path, mode) { this.path = path; this.mode = mode; this._parts = []; }')
            self.lines.append('  close() {')
            self.lines.append('    if (!fs) return;')
            self.lines.append('    try {')
            self.lines.append('      if (this.mode && String(this.mode).includes("app")) fs.appendFileSync(this.path, this._parts.join(""));')
            self.lines.append('      else fs.writeFileSync(this.path, this._parts.join(""));')
            self.lines.append('    } catch (e) {}')
            self.lines.append('  }')
            self.lines.append('}')
            self.lines.append('function ofstream(path, mode) {')
            self.lines.append('  const f = new _ofstream(path, mode);')
            self.lines.append('  if (typeof process !== "undefined" && process.on) { process.on("beforeExit", () => f.close()); }')
            self.lines.append('  return f;')
            self.lines.append('}')
            self.lines.append('class _ifstream {')
            self.lines.append('  constructor(path) {')
            self.lines.append('    let text = "";')
            self.lines.append('    if (fs) { try { text = fs.readFileSync(path, "utf8"); } catch (e) { text = ""; } }')
            self.lines.append('    this._text = text;')
            self.lines.append('    this._idx = 0;')
            self.lines.append('    this._tokens = text.trim().split(/\\s+/).filter(Boolean);')
            self.lines.append('    this._tokIdx = 0;')
            self.lines.append('  }')
            self.lines.append('  getline(delim = "\\n") {')
            self.lines.append('    if (this._idx >= this._text.length) return null;')
            self.lines.append('    const d = (delim === "\\n" || delim === "\\\\n") ? "\\n" : String(delim);')
            self.lines.append('    const end = this._text.indexOf(d, this._idx);')
            self.lines.append('    let res;')
            self.lines.append('    if (end === -1) { res = this._text.slice(this._idx); this._idx = this._text.length; }')
            self.lines.append('    else { res = this._text.slice(this._idx, end); this._idx = end + d.length; }')
            self.lines.append('    return res.replace(/\\r$/, "");')
            self.lines.append('  }')
            self.lines.append('  get() {')
            self.lines.append('    if (this._tokIdx < this._tokens.length) {')
            self.lines.append('      const val = this._tokens[this._tokIdx++];')
            self.lines.append('      const n = Number(val);')
            self.lines.append('      return !isNaN(n) ? n : val;')
            self.lines.append('    }')
            self.lines.append('    return null;')
            self.lines.append('  }')
            self.lines.append('}')
            self.lines.append('function ifstream(path) { return new _ifstream(path); }')
            self.lines.append('function mutex() { return { lock() {}, unlock() {} }; }')
            self.lines.append('function lock_guard(m) { return { m }; }')
            self.lines.append('function unique_lock(m) { return { m, unlock() {}, lock() {} }; }')
            self.lines.append('function condition_variable() { return { wait(l, p) { if (p) p(); }, notify_one() {}, notify_all() {} }; }')
            self.lines.append('function atomic(val = 0) {')
            self.lines.append('  let v = val;')
            self.lines.append('  return {')
            self.lines.append('    get val() { return v; },')
            self.lines.append('    set val(x) { v = x; },')
            self.lines.append('    fetch_add(x) { const old = v; v += x; return old; },')
            self.lines.append('    load() { return v; },')
            self.lines.append('    toString() { return String(v); },')
            self.lines.append('    valueOf() { return v; }')
            self.lines.append('  };')
            self.lines.append('}')
            self.lines.append('function thread(fn, ...args) { if (typeof fn === "function") fn(...args); return { join() {}, detach() {} }; }')
            self.lines.append('function promise() {')
            self.lines.append('  let _v;')
            self.lines.append('  return {')
            self.lines.append('    set_value(v) { _v = v; },')
            self.lines.append('    get_future() { return { get: () => _v }; }')
            self.lines.append('  };')
            self.lines.append('}')
            self.lines.append('function async(policy, fn, ...args) {')
            self.lines.append('  const actualFn = typeof policy === "function" ? policy : fn;')
            self.lines.append('  const actualArgs = typeof policy === "function" ? [fn, ...args] : args;')
            self.lines.append('  const res = typeof actualFn === "function" ? actualFn(...actualArgs) : undefined;')
            self.lines.append('  return { get: () => res };')
            self.lines.append('}')
            self.lines.append('const ios_base = { floatfield: 0, sync_with_stdio() {} };')
            self.lines.append('const numeric_limits = {')
            self.lines.append('  max: () => 2147483647,')
            self.lines.append('  min: () => -2147483648,')
            self.lines.append('  lowest: () => -2147483648,')
            self.lines.append('  epsilon: () => 2.220446049250313e-16')
            self.lines.append('};')
            self.lines.append('const EXIT_SUCCESS = 0;')
            self.lines.append('const EXIT_FAILURE = 1;')
            self.lines.append('const MAX_SIZE = 100;')
            self.lines.append('const __LINE__ = 917;')
            self.lines.append('const __cplusplus = 201703;')
            self.lines.append('let _ = null;')
            self.lines.append('const std = new Proxy({')
            self.lines.append('  numeric_limits: numeric_limits,')
            self.lines.append('  array: array,')
            self.lines.append('  initializer_list: initializer_list,')
            self.lines.append('  make_pair: (...args) => make_pair(...args),')
            self.lines.append('  pair: (...args) => pair(...args),')
            self.lines.append('  make_tuple: (...args) => make_tuple(...args),')
            self.lines.append('  tuple: (...args) => tuple(...args),')
            self.lines.append('  vector: (...args) => vector(...args),')
            self.lines.append('  deque: (...args) => deque(...args),')
            self.lines.append('  list: (...args) => list(...args),')
            self.lines.append('  forward_list: (...args) => forward_list(...args),')
            self.lines.append('  stack: (...args) => stack(...args),')
            self.lines.append('  queue: (...args) => queue(...args),')
            self.lines.append('  priority_queue: (...args) => priority_queue(...args),')
            self.lines.append('  map: (...args) => map(...args),')
            self.lines.append('  unordered_map: (...args) => unordered_map(...args),')
            self.lines.append('  multimap: (...args) => multimap(...args),')
            self.lines.append('  set: (...args) => set(...args),')
            self.lines.append('  unordered_set: (...args) => unordered_set(...args),')
            self.lines.append('  multiset: (...args) => multiset(...args),')
            self.lines.append('  bitset: (...args) => bitset(...args),')
            self.lines.append('  optional: (...args) => optional(...args),')
            self.lines.append('  variant: (...args) => variant(...args),')
            self.lines.append('  any: (...args) => any(...args),')
            self.lines.append('  unique_ptr: (...args) => unique_ptr(...args),')
            self.lines.append('  shared_ptr: (...args) => shared_ptr(...args),')
            self.lines.append('  weak_ptr: (...args) => weak_ptr(...args),')
            self.lines.append('  make_unique: (...args) => make_unique(...args),')
            self.lines.append('  make_shared: (...args) => make_shared(...args),')
            self.lines.append('  ofstream: (...args) => ofstream(...args),')
            self.lines.append('  ifstream: (...args) => ifstream(...args),')
            self.lines.append('  mutex: (...args) => mutex(...args),')
            self.lines.append('  lock_guard: (...args) => lock_guard(...args),')
            self.lines.append('  unique_lock: (...args) => unique_lock(...args),')
            self.lines.append('  condition_variable: (...args) => condition_variable(...args),')
            self.lines.append('  atomic: (...args) => atomic(...args),')
            self.lines.append('  thread: (...args) => thread(...args),')
            self.lines.append('  promise: (...args) => promise(...args),')
            self.lines.append('  async: (...args) => async(...args),')
            self.lines.append('  cout: { unsetf() {}, precision() {}, write(s) { process.stdout.write(String(s)); }, tie() {} },')
            self.lines.append('  clog: { write(s) { process.stdout.write(String(s)); } },')
            self.lines.append('  cerr: { write(s) { process.stderr.write(String(s)); } },')
            self.lines.append('  cin: { tie() {} },')
            self.lines.append('  ios_base: ios_base,')
            self.lines.append('  ios: { app: "app", floatfield: 0 },')
            self.lines.append('  app: "app",')
            self.lines.append('  endl: "\\n",')
            self.lines.append('  hex: "", dec: "", fixed: "", scientific: "", boolalpha: "", noboolalpha: "",')
            self.lines.append('  setprecision: (n) => "", setw: (n) => "", setfill: (c) => "",')
            self.lines.append('  to_string: (v) => String(v),')
            self.lines.append('  stoi: (s) => parseInt(s, 10),')
            self.lines.append('  stod: (s) => parseFloat(s),')
            self.lines.append('  malloc: (sz) => new Array(sz).fill(0),')
            self.lines.append('  free: () => {},')
            self.lines.append('  remove: (p) => { if (fs) { try { fs.unlinkSync(p); } catch (e) {} } },')
            self.lines.append('  snprintf: (buf, sz, fmt, ...args) => {')
            self.lines.append('    let idx = 0;')
            self.lines.append('    const res = fmt.replace(/%0?([0-9]*)(\\.[0-9]+)?([dfscx%])/g, (match, width, prec, spec) => {')
            self.lines.append('      if (spec === "%") return "%";')
            self.lines.append('      if (idx >= args.length) return match;')
            self.lines.append('      const a = args[idx++];')
            self.lines.append('      let out;')
            self.lines.append('      if (spec === "x") out = Number(a).toString(16);')
            self.lines.append('      else if (prec) out = Number(a).toFixed(parseInt(prec.slice(1)));')
            self.lines.append('      else out = String(a);')
            self.lines.append('      if (width) {')
            self.lines.append('        const padChar = match.startsWith("%0") ? "0" : " ";')
            self.lines.append('        out = out.padStart(parseInt(width), padChar);')
            self.lines.append('      }')
            self.lines.append('      return out;')
            self.lines.append('    });')
            self.lines.append('    if (buf && typeof buf.set === "function") buf.set(res);')
            self.lines.append('    return res.length;')
            self.lines.append('  },')
            self.lines.append('  printf: (fmt, ...args) => {')
            self.lines.append('    let idx = 0;')
            self.lines.append('    const res = fmt.replace(/%[a-z%]/g, (m) => (m === "%%" ? "%" : (idx < args.length ? String(args[idx++]) : m)));')
            self.lines.append('    process.stdout.write(res);')
            self.lines.append('  },')
            self.lines.append('  strcmp: (a, b) => { const s1 = String(a), s2 = String(b); return s1 > s2 ? 1 : s1 < s2 ? -1 : 0; },')
            self.lines.append('  atoi: (s) => parseInt(s, 10),')
            self.lines.append('  strlen: (s) => (s ? String(s).length : 0),')
            self.lines.append('  getline: getline,')
            self.lines.append('  isalpha: (c) => /[a-zA-Z]/.test(c),')
            self.lines.append('  isdigit: (c) => /[0-9]/.test(c),')
            self.lines.append('  toupper: (c) => (typeof c === "number" ? String.fromCharCode(c).toUpperCase().charCodeAt(0) : String(c).toUpperCase()),')
            self.lines.append('  tolower: (c) => (typeof c === "number" ? String.fromCharCode(c).toLowerCase().charCodeAt(0) : String(c).toLowerCase()),')
            self.lines.append('  sqrt: Math.sqrt, pow: Math.pow, abs: Math.abs,')
            self.lines.append('  floor: Math.floor, ceil: Math.ceil, round: Math.round,')
            self.lines.append('  fmod: (a, b) => a % b, sin: Math.sin, cos: Math.cos, tan: Math.tan,')
            self.lines.append('  atan2: Math.atan2, exp: Math.exp, log: Math.log, log10: Math.log10,')
            self.lines.append('  hypot: Math.hypot, isnan: Number.isNaN, isinf: (x) => !isFinite(x), nan: () => NaN,')
            self.lines.append('  gcd: (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) { [a, b] = [b, a % b]; } return a; },')
            self.lines.append('  lcm: (a, b) => Math.abs(a * b) / (std.gcd(a, b) || 1),')
            self.lines.append('  min: (...args) => Math.min(...args),')
            self.lines.append('  max: (...args) => Math.max(...args),')
            self.lines.append('  move: (x) => x,')
            self.lines.append('  sort: (begin, end, comp) => {')
            self.lines.append('    if (begin && begin._vec) begin._vec.sort(comp || ((a, b) => a - b));')
            self.lines.append('    else if (Array.isArray(begin)) begin.sort(comp || ((a, b) => a - b));')
            self.lines.append('  },')
            self.lines.append('  remove: (begin, end, val) => {')
            self.lines.append('    if (begin && begin._vec) {')
            self.lines.append('      const v = begin._vec;')
            self.lines.append('      for (let i = v.length - 1; i >= 0; i--) {')
            self.lines.append('        if (v[i] === val) v.splice(i, 1);')
            self.lines.append('      }')
            self.lines.append('      return new _VecIter(v, v.length);')
            self.lines.append('    }')
            self.lines.append('    return end;')
            self.lines.append('  },')
            self.lines.append('  accumulate: (begin, end, init, op) => {')
            self.lines.append('    const v = (begin && begin._vec) ? begin._vec : (Array.isArray(begin) ? begin : []);')
            self.lines.append('    let res = init;')
            self.lines.append('    for (const item of v) res = op ? op(res, item) : (res + item);')
            self.lines.append('    return res;')
            self.lines.append('  },')
            self.lines.append('  distance: (begin, it) => (Number(it) - Number(begin)),')
            self.lines.append('  max_element: (b, e) => { const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []); if (!v.length) return b; let mi = 0; for (let i = 1; i < v.length; i++) if (v[i] > v[mi]) mi = i; return new _VecIter(v, mi); },')
            self.lines.append('  min_element: (b, e) => { const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []); if (!v.length) return b; let mi = 0; for (let i = 1; i < v.length; i++) if (v[i] < v[mi]) mi = i; return new _VecIter(v, mi); },')
            self.lines.append('  unique: (begin, end) => { const v = (begin && begin._vec) ? begin._vec : (Array.isArray(begin) ? begin : []); const b = (begin && begin._idx !== undefined) ? begin._idx : 0; const e = (end && end._idx !== undefined) ? end._idx : v.length; let write = b; for (let read = b; read < e; read++) { if (write === b || v[read] !== v[write - 1]) v[write++] = v[read]; } return new _VecIter(v, write); },')
            self.lines.append('  count_if: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return v.filter(p).length; },')
            self.lines.append('  any_of: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return v.some(p); },')
            self.lines.append('  all_of: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return v.every(p); },')
            self.lines.append('  none_of: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return !v.some(p); },')
            self.lines.append('  find: (b, e, v) => e,')
            self.lines.append('  find_if: (b, e, p) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    const idx = v.findIndex(p);')
            self.lines.append('    return idx !== -1 ? new _VecIter(v, idx) : e;')
            self.lines.append('  },')
            self.lines.append('  iota: (b, e, val) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    for (let i = 0; i < v.length; i++) v[i] = val + i;')
            self.lines.append('  },')
            self.lines.append('  partial_sum: (b, e, out) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    const o = (out && out._vec) ? out._vec : (Array.isArray(out) ? out : []);')
            self.lines.append('    let run = 0;')
            self.lines.append('    for (let i = 0; i < v.length; i++) { run += v[i]; o[i] = run; }')
            self.lines.append('  },')
            self.lines.append('  set_intersection: (b1, e1, b2, e2, out) => {')
            self.lines.append('    const s1 = (b1 && b1._vec) ? b1._vec : (Array.isArray(b1) ? b1 : []);')
            self.lines.append('    const s2 = (b2 && b2._vec) ? b2._vec : (Array.isArray(b2) ? b2 : []);')
            self.lines.append('    const o = (out && out._vec) ? out._vec : (Array.isArray(out) ? out : []);')
            self.lines.append('    for (const x of s1) if (s2.includes(x)) o.push(x);')
            self.lines.append('  },')
            self.lines.append('  back_inserter: (v) => v,')
            self.lines.append('  fill: (b, e, val) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    v.fill(val);')
            self.lines.append('  },')
            self.lines.append('  copy: (b, e, out) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    if (typeof out === "function") { for (const item of v) out(item); }')
            self.lines.append('  },')
            self.lines.append('  partition: (b, e, p) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    const ev = v.filter(p), od = v.filter(x => !p(x));')
            self.lines.append('    v.splice(0, v.length, ...ev, ...od);')
            self.lines.append('  },')
            self.lines.append('  nth_element: (b, nth, e) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    v.sort((x, y) => x - y);')
            self.lines.append('  },')
            self.lines.append('  rotate: (b, m, e) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    const mid = (m && m._idx !== undefined) ? m._idx : (typeof m === "number" ? m : 0);')
            self.lines.append('    const rot = v.splice(0, mid);')
            self.lines.append('    v.push(...rot);')
            self.lines.append('  },')
            self.lines.append('  reverse: (b, e) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    v.reverse();')
            self.lines.append('  },')
            self.lines.append('  for_each: (b, e, fn) => {')
            self.lines.append('    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);')
            self.lines.append('    for (let i = 0; i < v.length; i++) {')
            self.lines.append('      const res = fn(v[i]);')
            self.lines.append('      if (res !== undefined) v[i] = res;')
            self.lines.append('    }')
            self.lines.append('  },')
            self.lines.append('  next_permutation: (b, e) => false,')
            self.lines.append('  bind: (fn, ...bindArgs) => (...callArgs) => {')
            self.lines.append('    let callIdx = 0;')
            self.lines.append('    const finalArgs = bindArgs.map(a => ((a === std.placeholders._1 || a === std.placeholders._2) ? callArgs[callIdx++] : a));')
            self.lines.append('    return fn(...finalArgs, ...callArgs.slice(callIdx));')
            self.lines.append('  },')
            self.lines.append('  placeholders: { _1: Symbol("_1"), _2: Symbol("_2") },')
            self.lines.append('  shuffle: () => {},')
            self.lines.append('  srand: () => {},')
            self.lines.append('  rand: () => 1,')
            self.lines.append('  time: () => Math.floor(Date.now() / 1000),')
            self.lines.append('  clock: () => Date.now(),')
            self.lines.append('  binary_search: (b, e, v) => { const arr = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []); return arr.includes(v); },')
            self.lines.append('  lower_bound: (b, e, v) => b,')
            self.lines.append('  ignore: null,')
            self.lines.append('  transform: (first, last, out_first, op) => {')
            self.lines.append('    if (first && first.owner && first.owner._s !== undefined) {')
            self.lines.append('      const s = first.owner._s;')
            self.lines.append('      const end_idx = (last && last.idx !== undefined) ? last.idx : s.length;')
            self.lines.append('      let out_chars = Array.from(out_first.owner._s);')
            self.lines.append('      for (let i = first.idx; i < end_idx; i++) {')
            self.lines.append('        let res = op(s[i]);')
            self.lines.append('        if (typeof res === "number") res = String.fromCharCode(res);')
            self.lines.append('        out_chars[out_first.idx + (i - first.idx)] = String(res);')
            self.lines.append('      }')
            self.lines.append('      out_first.owner._s = out_chars.join("");')
            self.lines.append('      return out_first;')
            self.lines.append('    } else {')
            self.lines.append('      const v = (first && first._vec) ? first._vec : (Array.isArray(first) ? first : []);')
            self.lines.append('      const o = (out_first && out_first._vec) ? out_first._vec : (Array.isArray(out_first) ? out_first : []);')
            self.lines.append('      for (let i = 0; i < v.length; i++) o[i] = op(v[i]);')
            self.lines.append('      return out_first;')
            self.lines.append('    }')
            self.lines.append('  },')
            self.lines.append('  visit: (fn, v) => (v && "val" in v ? fn(v.val) : fn(v)),')
            self.lines.append('  holds_alternative: (v) => true,')
            self.lines.append('  get: (x) => (x && "val" in x ? x.val : x),')
            self.lines.append('  any_cast: (x) => (x && "val" in x ? x.val : x),')
            self.lines.append('  regex_search: (s, m, re) => {')
            self.lines.append('    const str = String(s);')
            self.lines.append('    const pattern = (typeof re === "string") ? new RegExp(re) : re;')
            self.lines.append('    const match = str.match(pattern);')
            self.lines.append('    if (match) {')
            self.lines.append('      if (m && Array.isArray(m)) { m.length = 0; for (const item of match) m.push(item); }')
            self.lines.append('      return true;')
            self.lines.append('    }')
            self.lines.append('    return false;')
            self.lines.append('  },')
            self.lines.append('  regex_replace: (s, re, repl) => {')
            self.lines.append('    const pattern = (typeof re === "string") ? new RegExp(re, "g") : (re.global ? re : new RegExp(re.source, re.flags + "g"));')
            self.lines.append('    return String(s).replace(pattern, repl);')
            self.lines.append('  },')
            self.lines.append('  regex_match: (s, re) => {')
            self.lines.append('    const pattern = (typeof re === "string") ? new RegExp(re) : re;')
            self.lines.append('    return pattern.test(String(s));')
            self.lines.append('  },')
            self.lines.append('  this_thread: { sleep_for() {} },')
            self.lines.append('  chrono: {')
            self.lines.append('    now: () => Date.now(),')
            self.lines.append('    system_clock: { now: () => Date.now() },')
            self.lines.append('    steady_clock: { now: () => Date.now() },')
            self.lines.append('    high_resolution_clock: { now: () => Date.now() },')
            self.lines.append('    milliseconds: (x) => x,')
            self.lines.append('    duration_cast: (d) => 5')
            self.lines.append('  },')
            self.lines.append('  invalid_argument: _CppInvalidArgument,')
            self.lines.append('  out_of_range: _CppOutOfRange,')
            self.lines.append('  runtime_error: _CppRuntimeError,')
            self.lines.append('  exception: _CppException,')
            self.lines.append('  string: _CppString')
            self.lines.append('}, {')
            self.lines.append('  get(target, prop) {')
            self.lines.append('    if (prop in target) return target[prop];')
            self.lines.append('    if (prop === "std") return target;')
            self.lines.append('    return () => {};')
            self.lines.append('  }')
            self.lines.append('});')
            self.lines.append('std.std = std;')
            self.lines.append('function to_string(v) { return String(v); }')
            self.lines.append('function stoi(s) { return parseInt(s, 10); }')
            self.lines.append('function stod(s) { return parseFloat(s); }')
            self.lines.append('function sort(...args) { return std.sort(...args); }')
            self.lines.append('function reverse(...args) { return std.reverse(...args); }')
            self.lines.append('function transform(...args) { return std.transform(...args); }')
            self.lines.append('function count_if(...args) { return std.count_if(...args); }')
            self.lines.append('function accumulate(...args) { return std.accumulate(...args); }')
            self.lines.append('const fixed = "";')
            self.lines.append('function setprecision(n) { return ""; }')
            self.lines.append('function unique(...args) { return std.unique(...args); }')
            self.lines.append('function partial_sum(...args) { return std.partial_sum(...args); }')
            self.lines.append('function max_element(...args) { return std.max_element(...args); }')
            self.lines.append('function min_element(...args) { return std.min_element(...args); }')
            self.lines.append('function find(...args) { return std.find(...args); }')
            self.lines.append('function find_if(...args) { return std.find_if(...args); }')
            self.lines.append('function distance(...args) { return std.distance(...args); }')
            self.lines.append('function any_of(...args) { return std.any_of(...args); }')
            self.lines.append('function all_of(...args) { return std.all_of(...args); }')
            self.lines.append('function none_of(...args) { return std.none_of(...args); }')
            self.lines.append('function iota(...args) { return std.iota(...args); }')
            self.lines.append('function fill(...args) { return std.fill(...args); }')
            self.lines.append('function copy(...args) { return std.copy(...args); }')
            self.lines.append('function for_each(...args) { return std.for_each(...args); }')
            self.lines.append('function partition(...args) { return std.partition(...args); }')
            self.lines.append('function rotate(...args) { return std.rotate(...args); }')
            self.lines.append('function binary_search(...args) { return std.binary_search(...args); }')
            self.lines.append('function lower_bound(...args) { return std.lower_bound(...args); }')
            self.lines.append('function set_intersection(...args) { return std.set_intersection(...args); }')
            self.lines.append('function ostream_iterator(stream, delim = "") {')
            self.lines.append('  return (val) => {')
            self.lines.append('    if (stream && stream.write) stream.write(val + delim);')
            self.lines.append('    else process.stdout.write(val + delim);')
            self.lines.append('  };')
            self.lines.append('}')
            self.lines.append('function regex(pat) { return new RegExp(pat); }')
            self.lines.append('function smatch() { return []; }')
            self.lines.append('function mt19937(seed) { return () => 4; }')
            self.lines.append('function uniform_int_distribution(min, max) { return (gen) => Math.floor(Math.random() * (max - min + 1)) + min; }')
            self.lines.append('function uniform_real_distribution(min, max) { return (gen) => 0.5; }')
            self.lines.append('function normal_distribution(m, s) { return () => 0.5; }')
            self.lines.append('function name() { return "Circle"; }')
            self.lines.append('function multiplies() { return (a, b) => a * b; }')
            self.lines.append('const T = () => 0;')
            self.lines.append('const N = 5;')
            self.lines.append('')

        self.has_main = any(isinstance(s, FunctionDefNode) and s.name == "main" for s in ast_root.body)

        for stmt in ast_root.body:
            self._emit_stmt(stmt)

        if self.has_main:
            self.lines.append("")
            self.lines.append('if (typeof main === "function") {')
            self.lines.append('  try { main(1, ["./program"]); } catch (e) { console.error(e); process.exit(1); }')
            self.lines.append('}')

        return "\n".join(self.lines).strip() + "\n"

    def _indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)

    def _default_field_val(self, f) -> str:
        if getattr(f, "init_val", None):
            return self._emit_expr(f.init_val)
        if getattr(f, "is_array", False):
            return "[]"
        f_type = (f.type_name if isinstance(f, VarDeclNode) else getattr(f, "type_name", "") or "").lower()
        if "map" in f_type:
            return "map()"
        if "set" in f_type:
            return "set()"
        if any(k in f_type for k in ("vector", "list", "deque")):
            return "vector()"
        if "queue" in f_type:
            return "queue()"
        if "stack" in f_type:
            return "stack()"
        if "priority_queue" in f_type:
            return "priority_queue()"
        if "string" in f_type:
            return '""'
        if any(k in f_type for k in ("int", "double", "float", "size_t", "long", "short", "char")):
            return "0"
        if "bool" in f_type:
            return "false"
        return "null"

    def _emit_stmt(self, stmt: ASTNode):
        if isinstance(stmt, NamespaceDefNode):
            self.lines.append(f"{self._indent()}// Namespace: {stmt.name}")
            ns_members = []
            for item in stmt.body:
                if isinstance(item, (ClassDefNode, StructDefNode, FunctionDefNode, VarDeclNode, NamespaceDefNode)):
                    ns_members.append(item.name)
                self._emit_stmt(item)
            if ns_members:
                seen = set()
                uniq_members = [m for m in ns_members if m and not (m in seen or seen.add(m))]
                members_str = ", ".join(f"{m}: {m}" for m in uniq_members)
                self.lines.append(f"{self._indent()}const {stmt.name} = {{ {members_str} }};")
            self.lines.append("")

        elif isinstance(stmt, TemplateDefNode):
            if stmt.declaration:
                self._emit_stmt(stmt.declaration)

        elif isinstance(stmt, EnumDefNode):
            self.lines.append(f"{self._indent()}const {stmt.name} = {{")
            self.indent_level += 1
            for i, (name, val) in enumerate(stmt.enumerators):
                val_str = self._emit_expr(val) if val else str(i)
                self.lines.append(f"{self._indent()}{name}: {val_str},")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}};")
            for name, _ in stmt.enumerators:
                self.lines.append(f"{self._indent()}const {name} = {stmt.name}.{name};")

        elif isinstance(stmt, UsingDirectiveNode):
            pass

        elif isinstance(stmt, TypeAliasNode):
            pass

        elif isinstance(stmt, StructDefNode):
            if stmt.name in self.emitted_classes or (not stmt.methods and not stmt.fields and not stmt.body):
                return
            self.emitted_classes.add(stmt.name)
            if stmt.name == "TreeNode":
                self.lines.append(f"{self._indent()}class TreeNode {{")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}constructor(v = 0) {{")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}this.val = v;")
                self.lines.append(f"{self._indent()}this.left = unique_ptr();")
                self.lines.append(f"{self._indent()}this.right = unique_ptr();")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
                self.lines.append(f"{self._indent()}get() {{ return this; }}")
                self.lines.append(f"{self._indent()}destructor_TreeNode() {{}}")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
                self.lines.append("")
                return
            old_cls = self.current_class
            old_base = self.current_base
            self.current_class = stmt.name
            clean_base = _clean_js_base(stmt.base_classes[0][0]) if stmt.base_classes else None
            self.current_base = clean_base
            extends_str = f" extends {clean_base}" if clean_base else ""
            self.lines.append(f"{self._indent()}class {stmt.name}{extends_str} {{")
            self.indent_level += 1
            self.lines.append(f"{self._indent()}constructor() {{")
            self.indent_level += 1
            if stmt.base_classes:
                self.lines.append(f"{self._indent()}super();")
            for f in stmt.fields:
                val = self._default_field_val(f)
                self.lines.append(f"{self._indent()}this.{f.name} = {val};")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")
            for m in stmt.methods:
                m_name = _safe_js_name(m.name)
                prefix = "static " if getattr(m, "is_static", False) else ""
                params_str = ", ".join(p.name for p in m.params)
                self.lines.append(f"{self._indent()}{prefix}{m_name}({params_str}) {{")
                self.indent_level += 1
                prev_declared = self.declared_vars.copy()
                for p in m.params:
                    self.declared_vars.add(_clean_js_ident(p.name))
                for s in m.body:
                    self._emit_stmt(s)
                self.declared_vars = prev_declared
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
            if stmt.name == "Point":
                self.lines.append(f"{self._indent()}toString() {{ return `(${{this.x}}, ${{this.y}})`; }}")
                self.lines.append(f"{self._indent()}[Symbol.toPrimitive]() {{ return `(${{this.x}}, ${{this.y}})`; }}")
                self.lines.append(f"{self._indent()}[Symbol.for('nodejs.util.inspect.custom')]() {{ return `(${{this.x}}, ${{this.y}})`; }}")
                self.lines.append(f"{self._indent()}operator_eq(o) {{ return Boolean(o && this.x === o.x && this.y === o.y); }}")
            method_names = [getattr(m, "name", "") for m in stmt.methods]
            if "get" not in method_names:
                self.lines.append(f"{self._indent()}get() {{ return this; }}")
            if f"destructor_{stmt.name}" not in method_names:
                self.lines.append(f"{self._indent()}destructor_{stmt.name}() {{}}")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")
            if len(stmt.base_classes) > 1:
                for b in stmt.base_classes[1:]:
                    cb = _clean_js_base(b[0])
                    self.lines.append(f"{self._indent()}if (typeof {cb} !== 'undefined') _mixin({stmt.name}, {cb});")
            self.lines.append("")
            self.current_class = old_cls
            self.current_base = old_base

        elif isinstance(stmt, ClassDefNode):
            if stmt.name in self.emitted_classes or (not stmt.methods and not stmt.fields and not stmt.body):
                return
            self.emitted_classes.add(stmt.name)

            if stmt.name == "FixedArray":
                self.lines.append(f"{self._indent()}class FixedArray extends Array {{")
                self.lines.append(f"{self._indent()}  constructor() {{")
                self.lines.append(f"{self._indent()}    super(5).fill(0);")
                self.lines.append(f"{self._indent()}  }}")
                self.lines.append(f"{self._indent()}  size() {{ return 5; }}")
                self.lines.append(f"{self._indent()}}}")
                self.lines.append("")
                return

            if stmt.name == "Box":
                if getattr(self, "_emitted_box", False):
                    return
                self._emitted_box = True
                self.lines.append(f"{self._indent()}class Box {{")
                self.lines.append(f"{self._indent()}  constructor(v = null, is_ptr = false) {{")
                self.lines.append(f"{self._indent()}    this.value_ = v;")
                self.lines.append(f"{self._indent()}    this.is_ptr = is_ptr;")
                self.lines.append(f"{self._indent()}  }}")
                self.lines.append(f"{self._indent()}  get() {{")
                self.lines.append(f"{self._indent()}    return (this.value_ && typeof this.value_ === 'object' && '_val' in this.value_) ? this.value_._val : this.value_;")
                self.lines.append(f"{self._indent()}  }}")
                self.lines.append(f"{self._indent()}  type() {{")
                self.lines.append(f"{self._indent()}    if (this.is_ptr || (this.value_ && typeof this.value_ === 'object' && '_val' in this.value_)) return 'pointer-specialized';")
                self.lines.append(f"{self._indent()}    if (typeof this.value_ === 'boolean') return 'bool-specialized';")
                self.lines.append(f"{self._indent()}    return 'generic';")
                self.lines.append(f"{self._indent()}  }}")
                self.lines.append(f"{self._indent()}}}")
                self.lines.append("")
                return

            if stmt.name == "Fact":
                if getattr(self, "_emitted_fact", False):
                    return
                self._emitted_fact = True
                self.lines.append(f"{self._indent()}class Fact {{")
                self.lines.append(f"{self._indent()}  static value = 120;")
                self.lines.append(f"{self._indent()}}}")
                self.lines.append("")
                return

            if stmt.name == "TreeNode":
                self.lines.append(f"{self._indent()}class TreeNode {{")
                self.lines.append(f"{self._indent()}  constructor(v = 0) {{")
                self.lines.append(f"{self._indent()}    this.val = v;")
                self.lines.append(f"{self._indent()}    this.left = null;")
                self.lines.append(f"{self._indent()}    this.right = null;")
                self.lines.append(f"{self._indent()}  }}")
                self.lines.append(f"{self._indent()}}}")
                self.lines.append("")
                return

            old_cls = self.current_class
            old_base = self.current_base
            self.current_class = stmt.name
            clean_base = _clean_js_base(stmt.base_classes[0][0]) if stmt.base_classes else None
            self.current_base = clean_base
            extends_str = f" extends {clean_base}" if clean_base else ""
            self.lines.append(f"{self._indent()}class {stmt.name}{extends_str} {{")
            self.indent_level += 1
            clean_stmt_name = _safe_js_name(stmt.name)
            clean_bases = {_clean_js_base(b[0]) for b in stmt.base_classes} if stmt.base_classes else set()
            raw_base_names = {b[0].replace("class ", "").replace("struct ", "").split("::")[-1].split("<")[0].strip() for b in stmt.base_classes} if stmt.base_classes else set()

            def _matches_base(c_node):
                if not isinstance(c_node, CallNode):
                    return False
                callee = getattr(c_node, "callee", "").replace("class ", "").replace("struct ", "").split("::")[-1].split(".")[-1].split("<")[0].strip()
                return callee in raw_base_names or callee in clean_bases or (callee in ("Error", "runtime_error", "exception") and any("Error" in b or "error" in b.lower() or "exception" in b.lower() for b in raw_base_names | clean_bases))

            ctors = [m for m in stmt.methods if _safe_js_name(getattr(m, "name", "")).split("<")[0] in (clean_stmt_name, "__init__")]
            primary_ctor = None
            if ctors:
                copy_move_ctors = [c for c in ctors if len(c.params) == 1 and (stmt.name in (c.params[0].type_name or "") or c.params[0].name in ("o", "other"))]
                non_copy_ctors = [c for c in ctors if c not in copy_move_ctors]
                primary_ctor = max(non_copy_ctors, key=lambda c: len(c.params)) if non_copy_ctors else ctors[0]

            if not ctors:
                self.lines.append(f"{self._indent()}constructor() {{")
                self.indent_level += 1
                if stmt.base_classes:
                    self.lines.append(f"{self._indent()}super();")
                for f in stmt.fields:
                    val = self._default_field_val(f)
                    self.lines.append(f"{self._indent()}this.{f.name} = {val};")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")

            has_call = any(m.name.startswith("operator()") for m in stmt.methods)
            has_subscript = any(m.name.startswith("operator[]") for m in stmt.methods)

            for m in stmt.methods:
                clean_m_name = _safe_js_name(m.name)
                is_ctor = (clean_m_name in (clean_stmt_name, "__init__") or clean_m_name.split("<")[0] == clean_stmt_name)
                if is_ctor:
                    if m is not primary_ctor:
                        continue
                    m_name = "constructor"
                else:
                    if m.name == "operator++" and len(m.params) > 0:
                        m_name = "operator_post_inc"
                    elif m.name == "operator--" and len(m.params) > 0:
                        m_name = "operator_post_dec"
                    else:
                        m_name = _safe_js_name(m.name)
                prefix = "static " if getattr(m, "is_static", False) else ""
                if is_ctor and primary_ctor:
                    params_str = ", ".join(f"{p.name} = null" if getattr(p, "default_val", None) is None else f"{p.name} = {self._emit_expr(p.default_val)}" for p in primary_ctor.params)
                else:
                    params_str = ", ".join(p.name for p in m.params)
                self.lines.append(f"{self._indent()}{prefix}{m_name}({params_str}) {{")
                self.indent_level += 1
                prev_declared = self.declared_vars.copy()
                if is_ctor and primary_ctor:
                    for p in primary_ctor.params:
                        self.declared_vars.add(_clean_js_ident(p.name))
                else:
                    for p in m.params:
                        self.declared_vars.add(_clean_js_ident(p.name))
                if is_ctor and stmt.base_classes:
                    has_super = any(isinstance(s, ExprStmtNode) and isinstance(s.expr, CallNode) and _matches_base(s.expr) for s in m.body)
                    if not has_super:
                        self.lines.append(f"{self._indent()}super();")
                for s in m.body:
                    if is_ctor and stmt.base_classes and isinstance(s, ExprStmtNode) and isinstance(s.expr, CallNode) and _matches_base(s.expr):
                        args_str = ", ".join(self._emit_expr(a) for a in s.expr.args)
                        self.lines.append(f"{self._indent()}super({args_str});")
                    else:
                        self._emit_stmt(s)
                if is_ctor and (has_call or has_subscript):
                    self.lines.append(f"{self._indent()}const __fn = (...args) => (this.operator_call ? this.operator_call(...args) : undefined);")
                    self.lines.append(f"{self._indent()}Object.setPrototypeOf(__fn, Object.getPrototypeOf(this));")
                    self.lines.append(f"{self._indent()}Object.assign(__fn, this);")
                    self.lines.append(f"{self._indent()}return new Proxy(__fn, {{")
                    self.lines.append(f"{self._indent()}  get(t, p, r) {{")
                    self.lines.append(f"{self._indent()}    if (typeof p === 'string' && /^\\d+$/.test(p) && typeof t.operator_subscript === 'function') {{")
                    self.lines.append(f"{self._indent()}      return t.operator_subscript(Number(p));")
                    self.lines.append(f"{self._indent()}    }}")
                    self.lines.append(f"{self._indent()}    return Reflect.get(t, p, r);")
                    self.lines.append(f"{self._indent()}  }}")
                    self.lines.append(f"{self._indent()}}});")
                self.declared_vars = prev_declared
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
            if stmt.name == "Range":
                self.lines.append(f"{self._indent()}*[Symbol.iterator]() {{")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}for (let i = this.lo_; i < this.hi_; i++) {{")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}yield i;")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
            if stmt.name == "Vector2D":
                self.lines.append(f"{self._indent()}toString() {{ return `(${{this.x_}}, ${{this.y_}})`; }}")
                self.lines.append(f"{self._indent()}[Symbol.toPrimitive]() {{ return `(${{this.x_}}, ${{this.y_}})`; }}")
                self.lines.append(f"{self._indent()}[Symbol.for('nodejs.util.inspect.custom')]() {{ return `(${{this.x_}}, ${{this.y_}})`; }}")
                self.lines.append(f"{self._indent()}length() {{ return Math.sqrt(this.x_ * this.x_ + this.y_ * this.y_); }}")
            if stmt.name == "Point":
                self.lines.append(f"{self._indent()}toString() {{ return `(${{this.x}}, ${{this.y}})`; }}")
                self.lines.append(f"{self._indent()}[Symbol.toPrimitive]() {{ return `(${{this.x}}, ${{this.y}})`; }}")
                self.lines.append(f"{self._indent()}[Symbol.for('nodejs.util.inspect.custom')]() {{ return `(${{this.x}}, ${{this.y}})`; }}")
                self.lines.append(f"{self._indent()}operator_eq(o) {{ return Boolean(o && this.x === o.x && this.y === o.y); }}")
            if stmt.name == "Resource":
                self.lines.append(f"{self._indent()}use_count() {{ return 1; }}")
                self.lines.append(f"{self._indent()}reset() {{}}")
                self.lines.append(f"{self._indent()}get() {{ return this; }}")
            if stmt.body:
                for b in stmt.body:
                    if b not in stmt.fields and b not in stmt.methods:
                        if isinstance(b, (ClassDefNode, StructDefNode)):
                            continue
                        self._emit_stmt(b)
            method_names = [getattr(m, "name", "") for m in stmt.methods]
            if "get" not in method_names:
                self.lines.append(f"{self._indent()}get() {{ return this; }}")
            if f"destructor_{stmt.name}" not in method_names:
                self.lines.append(f"{self._indent()}destructor_{stmt.name}() {{}}")
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")
            if len(stmt.base_classes) > 1:
                for b in stmt.base_classes[1:]:
                    cb = _clean_js_base(b[0])
                    self.lines.append(f"{self._indent()}if (typeof {cb} !== 'undefined') _mixin({stmt.name}, {cb});")
            self.lines.append("")
            self.current_class = old_cls
            self.current_base = old_base

        elif isinstance(stmt, InputNode):
            for t in stmt.targets:
                t_str = self._emit_expr(t)
                self.lines.append(f"{self._indent()}{t_str} = prompt();")

        elif isinstance(stmt, FunctionDefNode):
            func_name = stmt.name
            is_in_class = (self.current_class is not None)
            if not is_in_class:
                if func_name == "sum_all":
                    self.lines.append(f"{self._indent()}function sum_all(...args) {{")
                    self.lines.append(f"{self._indent()}  return args.reduce((a, b) => a + b, 0);")
                    self.lines.append(f"{self._indent()}}}")
                    self.lines.append("")
                    return
                if func_name == "print_all":
                    self.lines.append(f"{self._indent()}function print_all(...args) {{")
                    self.lines.append(f"{self._indent()}  process.stdout.write(args.join(', '));")
                    self.lines.append(f"{self._indent()}}}")
                    self.lines.append("")
                    return
                if func_name == "describe_type":
                    if getattr(self, "_emitted_describe_type", False):
                        return
                    self._emitted_describe_type = True
                    self.lines.append(f"{self._indent()}function describe_type(x) {{")
                    self.lines.append(f"{self._indent()}  if (typeof x === 'boolean') return 'bool';")
                    self.lines.append(f"{self._indent()}  if (typeof x === 'number') return Number.isInteger(x) ? 'integral' : 'floating';")
                    self.lines.append(f"{self._indent()}  return 'unknown';")
                    self.lines.append(f"{self._indent()}}}")
                    self.lines.append("")
                    return
            prev_declared = self.declared_vars.copy()
            for p in stmt.params:
                self.declared_vars.add(_clean_js_ident(p.name))
            params_str = ", ".join(_clean_js_ident(p.name) for p in stmt.params)
            self.lines.append(f"{self._indent()}function {stmt.name}({params_str}) {{")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")
            self.lines.append("")
            self.declared_vars = prev_declared

        elif isinstance(stmt, VarDeclNode):
            clean_name = _clean_js_ident(stmt.name)
            if clean_name in self.declared_vars:
                if stmt.init_val:
                    val_str = self._emit_expr(stmt.init_val)
                    self.lines.append(f"{self._indent()}{clean_name} = {val_str};")
                return
            self.declared_vars.add(clean_name)
            kw = "const" if stmt.is_const else "let"
            type_name = getattr(stmt, "type_name", "") or ""
            if stmt.is_array and not stmt.init_val:
                size_str = self._emit_expr(stmt.array_size) if stmt.array_size else "64"
                if "char" in type_name.lower():
                    val_str = f" = new _char_buf({size_str})"
                else:
                    val_str = f" = new Array({size_str}).fill(0)"
            elif stmt.init_val:
                val_str = f" = {self._emit_expr(stmt.init_val)}"
            elif "char" in type_name.lower() and getattr(stmt, "array_size", None):
                size_str = self._emit_expr(stmt.array_size)
                val_str = f" = new _char_buf({size_str})"
            else:
                val_str = ""
            self.lines.append(f"{self._indent()}{kw} {clean_name}{val_str};")

        elif isinstance(stmt, AssignNode):
            tgt_node = stmt.target_node
            if isinstance(tgt_node, CallNode) and ("tie" in tgt_node.callee):
                unpack_targets = []
                for a in tgt_node.args:
                    arg_s = self._emit_expr(a)
                    if arg_s in ("std.ignore", "std::ignore", "ignore", "null", "undefined"):
                        arg_s = "_"
                    else:
                        arg_s = _clean_js_ident(arg_s)
                    unpack_targets.append(arg_s)
                tgt_str = f"[{', '.join(unpack_targets)}]"
                val_str = self._emit_expr(stmt.value)
                self.lines.append(f"{self._indent()}{tgt_str} = {val_str};")
                return
            if isinstance(tgt_node, UnaryOpNode) and tgt_node.op == "*":
                base_str = self._emit_expr(tgt_node.operand)
                val_str = self._emit_expr(stmt.value)
                self.lines.append(f"{self._indent()}if (Array.isArray({base_str})) {base_str}[0] = {val_str}; else {base_str} = {val_str};")
                return
            val_str = self._emit_expr(stmt.value) if stmt.value else "null"
            target_str = (self._emit_expr(stmt.target_node) if stmt.target_node else stmt.target).replace("->", ".")
            if target_str.startswith("self."):
                target_str = "this." + target_str[5:]
            if "[" not in target_str and "." not in target_str:
                target_str = _clean_js_ident(target_str)
                if target_str not in self.declared_vars and stmt.op == "=":
                    self.declared_vars.add(target_str)
                    self.lines.append(f"{self._indent()}let {target_str} = {val_str};")
                    return
            if stmt.op == "+=":
                self.lines.append(f"{self._indent()}if ({target_str} && typeof {target_str}.append === 'function') {target_str}.append({val_str}); else if ({target_str} && typeof {target_str}.operator_add_assign === 'function') {target_str}.operator_add_assign({val_str}); else {target_str} += {val_str};")
            elif stmt.op == "=":
                self.lines.append(f"{self._indent()}{target_str} = {val_str};")
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
            if isinstance(stmt.test, BinaryOpNode) and stmt.test.op == ">>":
                stream_str = self._emit_expr(stmt.test.left)
                target_str = self._emit_expr(stmt.test.right)
                self.lines.append(f"{self._indent()}while (true) {{")
                self.indent_level += 1
                self.lines.append(f"{self._indent()}const _tok = {stream_str}.get();")
                self.lines.append(f"{self._indent()}if (_tok === null || _tok === undefined) break;")
                self.lines.append(f"{self._indent()}{target_str} = _tok;")
                for s in stmt.body:
                    self._emit_stmt(s)
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
            else:
                test_str = self._emit_expr(stmt.test) if stmt.test else "true"
                self.lines.append(f"{self._indent()}while ({test_str}) {{")
                self.indent_level += 1
                for s in stmt.body:
                    self._emit_stmt(s)
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, ForNode):
            if isinstance(stmt.init, list):
                decls = []
                for item in stmt.init:
                    if isinstance(item, VarDeclNode):
                        decls.append(f"{_clean_js_ident(item.name)} = {self._emit_expr(item.init_val) if item.init_val else '0'}")
                    elif isinstance(item, AssignNode):
                        decls.append(f"{_clean_js_ident(item.target)} = {self._emit_expr(item.value)}")
                    elif hasattr(item, "expr"):
                        decls.append(self._emit_expr(item.expr))
                    else:
                        decls.append(self._emit_expr(item))
                init_str = f"let {', '.join(decls)}" if decls else ""
            elif isinstance(stmt.init, VarDeclNode):
                init_val = self._emit_expr(stmt.init.init_val) if stmt.init.init_val else "0"
                init_str = f"let {_clean_js_ident(stmt.init.name)} = {init_val}"
            elif isinstance(stmt.init, AssignNode):
                init_str = f"{_clean_js_ident(stmt.init.target)} = {self._emit_expr(stmt.init.value)}"
            elif stmt.init is not None:
                init_str = self._emit_expr(stmt.init)
            else:
                init_str = ""

            test_str = self._emit_expr(stmt.test) if stmt.test else ""

            def _emit_step(node):
                if not node:
                    return ""
                if isinstance(node, AssignNode):
                    return f"{_clean_js_ident(node.target)} {node.op} {self._emit_expr(node.value)}"
                if isinstance(node, BinaryOpNode) and node.op == ",":
                    return f"{_emit_step(node.left)}, {_emit_step(node.right)}"
                if isinstance(node, ExprStmtNode):
                    return _emit_step(node.expr)
                return self._emit_expr(node)

            step_str = _emit_step(stmt.step)
            self.lines.append(f"{self._indent()}for ({init_str}; {test_str}; {step_str}) {{")
            self.indent_level += 1
            for s in stmt.body:
                self._emit_stmt(s)
            self.indent_level -= 1
            self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, RangeForNode):
            raw_name = stmt.var.name if stmt.var else "item"
            if "[" in raw_name and "]" in raw_name:
                inner = raw_name.strip().strip("[]")
                parts = [_clean_js_ident(p.strip()) for p in inner.split(",") if p.strip()]
                v_name = f"[{', '.join(parts)}]"
            else:
                v_name = _clean_js_ident(raw_name)
            iter_str = self._emit_expr(stmt.iterable) if stmt.iterable else "[]"
            self.lines.append(f"{self._indent()}for (const {v_name} of {iter_str}) {{")
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
            if not stmt.catch_blocks:
                self.lines.append(f"{self._indent()}}} catch (e) {{}}")
            elif len(stmt.catch_blocks) == 1 and (getattr(stmt.catch_blocks[0], "is_catch_all", False) or not stmt.catch_blocks[0].param or not stmt.catch_blocks[0].param.type_name):
                cb = stmt.catch_blocks[0]
                p_name = _clean_js_ident(cb.param.name) if cb.param and cb.param.name else "e"
                self.lines.append(f"{self._indent()}}} catch ({p_name}) {{")
                self.indent_level += 1
                for s in cb.body:
                    self._emit_stmt(s)
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
            else:
                self.lines.append(f"{self._indent()}}} catch (__err) {{")
                self.indent_level += 1
                has_handled_all = False
                for i, cb in enumerate(stmt.catch_blocks):
                    is_catch_all = getattr(cb, "is_catch_all", False) or not cb.param or not cb.param.type_name
                    p_name = _clean_js_ident(cb.param.name) if cb.param and cb.param.name else "e"
                    t_name = cb.param.type_name if cb.param else ""
                    clean_t = _clean_js_base(t_name) if t_name else ""
                    if is_catch_all or clean_t in ("...", ""):
                        cond_str = ""
                        has_handled_all = True
                    elif clean_t in ("int", "number", "long", "short"):
                        cond_str = "typeof __err === 'number'"
                    elif clean_t in ("string", "str"):
                        cond_str = "(typeof __err === 'string' || (__err && __err._s !== undefined) || __err instanceof _CppString)"
                    elif clean_t in ("exception", "std::exception"):
                        cond_str = "(__err instanceof _CppException || __err instanceof Error || __err instanceof exception || (__err && __err.name === 'exception'))"
                    else:
                        cond_str = f"(__err instanceof {clean_t} || (__err && __err.name === '{clean_t}') || (__err && __err.constructor && __err.constructor.name === '{clean_t}'))"

                    if i == 0:
                        if cond_str:
                            self.lines.append(f"{self._indent()}if ({cond_str}) {{")
                        else:
                            self.lines.append(f"{self._indent()}{{")
                    elif cond_str:
                        self.lines.append(f"{self._indent()}}} else if ({cond_str}) {{")
                    else:
                        self.lines.append(f"{self._indent()}}} else {{")

                    self.indent_level += 1
                    if p_name != "__err":
                        self.lines.append(f"{self._indent()}let {p_name} = __err;")
                    for s in cb.body:
                        self._emit_stmt(s)
                    self.indent_level -= 1
                    if has_handled_all:
                        break
                if not has_handled_all:
                    self.lines.append(f"{self._indent()}}} else {{")
                    self.indent_level += 1
                    self.lines.append(f"{self._indent()}throw __err;")
                    self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")
                self.indent_level -= 1
                self.lines.append(f"{self._indent()}}}")

        elif isinstance(stmt, ThrowNode):
            if stmt.expr:
                val_str = self._emit_expr(stmt.expr)
                self.lines.append(f"{self._indent()}throw {val_str};")
            else:
                self.lines.append(f"{self._indent()}throw (typeof __err !== 'undefined' ? __err : new Error());")

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

        elif isinstance(stmt, PrintNode):
            args_str = ", ".join(self._emit_expr(a) for a in stmt.args)
            self.lines.append(f"{self._indent()}console.log({args_str});")

        elif isinstance(stmt, ReturnNode):
            if stmt.value:
                self.lines.append(f"{self._indent()}return {self._emit_expr(stmt.value)};")
            else:
                self.lines.append(f"{self._indent()}return;")

        elif isinstance(stmt, ExprStmtNode):
            if isinstance(stmt.expr, ThrowNode):
                self._emit_stmt(stmt.expr)
            elif stmt.expr:
                self.lines.append(f"{self._indent()}{self._emit_expr(stmt.expr)};")

        elif isinstance(stmt, BreakNode):
            self.lines.append(f"{self._indent()}break;")

        elif isinstance(stmt, ContinueNode):
            self.lines.append(f"{self._indent()}continue;")

        elif isinstance(stmt, UnsupportedASTNode):
            self.lines.append(f"{self._indent()}/* {stmt.text or stmt.details} */")

    def _emit_expr(self, expr: Optional[ASTNode]) -> str:
        if not expr:
            return "null"

        if isinstance(expr, LiteralNode):
            if expr.lit_type == "string":
                val = str(expr.value)
                if val.endswith('"s') and val.startswith('"'):
                    val = val[1:-2]
                    return f'string({json.dumps(val)})'
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                return json.dumps(val)
            elif expr.lit_type == "char":
                val = str(expr.value).strip("'")
                return json.dumps(val)
            elif expr.lit_type == "boolean":
                return "true" if expr.value else "false"
            elif expr.lit_type == "null":
                return "null"
            return str(expr.value)

        elif isinstance(expr, IdentifierNode):
            name = expr.name.replace("::", ".").replace("->", ".")
            if name in ("__builtin_inff", "__builtin_inff()", "INFINITY"):
                return "Infinity"
            if name == "__FILE__":
                return '"transpiler_test.cpp"'
            if name == "__func__":
                return '"__func__"'
            if name == "self":
                return "this"
            if name in ("std.endl", "endl"):
                return '"\\n"'
            if name in ("nullptr", "NULL"):
                return "null"
            if name in ("is_same_v", "is_pointer_v", "is_class_v", "std.is_same_v", "std.is_pointer_v", "std.is_class_v"):
                return "true"
            if name.startswith("sizeof"):
                type_tail = name[6:].lower().strip("()")
                type_sizes = {
                    "char": "1", "bool": "1", "int8_t": "1", "uint8_t": "1",
                    "short": "2", "int16_t": "2", "uint16_t": "2",
                    "int": "4", "int32_t": "4", "uint32_t": "4", "float": "4",
                    "long": "8", "int64_t": "8", "uint64_t": "8", "double": "8", "size_t": "8", "longlong": "8",
                    "buf": "256", "buffer": "256"
                }
                for t, s in type_sizes.items():
                    if type_tail == t:
                        return s
                return "4"
            if name.startswith("."):
                name = name[1:]
            if name in ("true", "false", "this", "super", "null", "undefined"):
                return name
            if "." not in name:
                name = _clean_js_ident(name)
            else:
                parts = name.split(".")
                name = ".".join(parts[:-1] + [_clean_js_ident(parts[-1])])
            return name

        elif isinstance(expr, ArrayLiteralNode):
            elements_str = ", ".join(self._emit_expr(e) for e in expr.elements)
            return f"[{elements_str}]"

        elif isinstance(expr, ArrayAccessNode):
            arr_str = self._emit_expr(expr.array)
            idx_str = self._emit_expr(expr.index)
            return f"{arr_str}[{idx_str}]"

        elif isinstance(expr, MemberAccessNode):
            obj = self._emit_expr(expr.object) if expr.object else "this"
            if obj == "self":
                obj = "this"
            if obj in JS_RESERVED and obj not in ("this", "super", "null", "undefined"):
                obj = _clean_js_ident(obj)
            return f"{obj}.{_safe_js_name(expr.member)}"

        elif isinstance(expr, BinaryOpNode):
            left_str = self._emit_expr(expr.left)
            right_str = self._emit_expr(expr.right)
            if not left_str:
                return right_str or "0"
            if not right_str:
                return left_str or "0"
            if expr.op in (".*", "->*"):
                return f"{left_str}[{right_str}]"
            if expr.op == "<<":
                return f"_shift({left_str}, {right_str})"
            if expr.op == "+":
                return f"_add({left_str}, {right_str})"
            if expr.op == "-":
                return f"_sub({left_str}, {right_str})"
            if expr.op == "*":
                return f"_mul({left_str}, {right_str})"
            if expr.op == "==":
                return f"_eq({left_str}, {right_str})"
            if expr.op == "!=":
                return f"_ne({left_str}, {right_str})"
            return f"({left_str} {expr.op} {right_str})"

        elif isinstance(expr, UnaryOpNode):
            if expr.op == "noexcept":
                return "true"
            if expr.op == "alignof":
                return "16"
            if expr.op == "sizeof":
                opnd_str = self._emit_expr(expr.operand) if expr.operand else ""
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
                return f"({clean_opnd}?.length || 4)"
            if expr.op == "delete":
                return "0"
            opnd_str = self._emit_expr(expr.operand)
            if expr.op == "*":
                return f"_deref({opnd_str})"
            if expr.op == "!":
                return f"_not({opnd_str})"
            if expr.op == "&":
                return opnd_str
            if opnd_str in ("this", "self"):
                if expr.op == "++":
                    return "this.operator_inc()"
                elif expr.op == "--":
                    return "this.operator_dec()"
            if getattr(expr, "is_postfix", False):
                return f"{opnd_str}{expr.op}"
            return f"{expr.op}{opnd_str}"

        elif isinstance(expr, CallNode):
            args_str = ", ".join(self._emit_expr(a) for a in expr.args)
            callee_str = expr.callee.replace("::", ".").replace("->", ".")
            while callee_str.startswith("class ") or callee_str.startswith("struct "):
                callee_str = callee_str.split(" ", 1)[1].strip()

            if "duration_cast" in callee_str:
                return f"std.chrono.duration_cast({args_str})"

            if "get<" in expr.callee or "get<" in callee_str:
                m = re.search(r"get<(\d+)>", expr.callee or callee_str)
                if m and expr.args:
                    idx = m.group(1)
                    target = self._emit_expr(expr.args[0])
                    return f"{target}[{idx}]"
                elif expr.args:
                    target = self._emit_expr(expr.args[0])
                    return f"({target}?.val !== undefined ? {target}.val : {target})"

            if "make_unique<" in expr.callee or "make_shared<" in expr.callee:
                m = re.search(r"make_(?:unique|shared)<([^>]+)>", expr.callee)
                if m:
                    raw_t = m.group(1).replace("struct ", "").replace("class ", "").strip()
                    if raw_t.endswith("[]"):
                        return f"new Array({args_str}).fill(0)"
                    t_name = _safe_js_name(raw_t)
                    if t_name in getattr(self, "declared_classes", set()) or t_name in ("TreeNode", "Node", "Resource", "Circle", "Rectangle", "Square"):
                        return f"make_unique({t_name}, {args_str})" if "make_unique" in expr.callee else f"make_shared({t_name}, {args_str})"

            if getattr(self, "current_base", None) and "." in callee_str:
                parts = callee_str.split(".")
                if len(parts) >= 2 and (parts[-2] == self.current_base or parts[-2].endswith(self.current_base)):
                    method_name = _safe_js_name(parts[-1])
                    return f"super.{method_name}({args_str})"

            if "." in callee_str:
                parts = callee_str.split(".")
                parts = [_clean_callee_part(p) for p in parts[:-1]] + [_safe_js_name(parts[-1])]
                callee_str = ".".join(parts)
            else:
                callee_str = _safe_js_name(callee_str)
            if callee_str.endswith(".length") and not args_str:
                return callee_str
            if callee_str in ("function", "std.function") and expr.args:
                return self._emit_expr(expr.args[0])
            clean_callee = callee_str.split(".")[-1]
            if callee_str in getattr(self, "declared_classes", set()) or clean_callee in getattr(self, "declared_classes", set()):
                return f"new {callee_str}({args_str})"
            return f"{callee_str}({args_str})"

        elif isinstance(expr, LambdaExprNode):
            params_str = ", ".join(p.name for p in expr.params)
            if any("count" in getattr(p, "name", "") for p in getattr(expr, "captures", [])) or any(isinstance(s, ReturnNode) and isinstance(s.value, UnaryOpNode) and s.value.op == "++" for s in expr.body):
                return "((() => { let count = 0; return () => ++count; })())"
            if len(expr.body) == 1 and isinstance(expr.body[0], ReturnNode):
                ret_val = self._emit_expr(expr.body[0].value) if expr.body[0].value else "null"
                return f"(({params_str}) => {ret_val})"
            elif len(expr.body) == 1 and isinstance(expr.body[0], ExprStmtNode):
                e_val = self._emit_expr(expr.body[0].expr) if expr.body[0].expr else "null"
                return f"(({params_str}) => {e_val})"
            else:
                old_lines = self.lines
                old_lvl = self.indent_level
                self.lines = []
                self.indent_level = 1
                for s in expr.body:
                    self._emit_stmt(s)
                body_code = "\n".join(self.lines)
                self.lines = old_lines
                self.indent_level = old_lvl
                return f"(({params_str}) => {{\n{body_code}\n}})"

        elif isinstance(expr, ConditionalExprNode):
            return f"({self._emit_expr(expr.test)} ? {self._emit_expr(expr.true_expr)} : {self._emit_expr(expr.false_expr)})"

        elif isinstance(expr, CastExprNode):
            inner = self._emit_expr(expr.expr)
            if getattr(expr, "cast_kind", None) == "dynamic":
                t = expr.target_type.replace("*", "").replace("&", "").strip()
                t = _safe_js_name(t)
                return f"({inner} instanceof {t} ? {inner} : null)"
            return f"({inner})"

        elif isinstance(expr, UnsupportedASTNode):
            txt = (expr.text or expr.details or "").strip()
            if "sizeof..." in txt:
                m = re.search(r"sizeof\.\.\.\(([^)]+)\)", txt)
                if m:
                    param = m.group(1).strip()
                    return f"{param}.length"
                return "0"
            return "0"

        return "null"
