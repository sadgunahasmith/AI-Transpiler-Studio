"""
Normalized Abstract Syntax Tree (AST) definitions for Stage 2: Syntax Analysis.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Tuple

@dataclass
class SyntaxErrorRecord:
    line: int
    column: int
    message: str
    token_value: Optional[str] = None
    severity: str = "error"
    source: str = "compiler"
    category: str = "Syntax Error"
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "token_value": self.token_value,
            "severity": self.severity,
            "source": self.source,
            "category": self.category,
            "suggested_fix": self.suggested_fix
        }

@dataclass
class ASTNode:
    line: int = 1
    column: int = 1

    def to_dict(self) -> Dict[str, Any]:
        result = {"node_type": self.__class__.__name__, "line": self.line, "column": self.column}
        for k, v in self.__dict__.items():
            if k in ("line", "column"):
                continue
            if isinstance(v, ASTNode):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            elif isinstance(v, tuple):
                result[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            elif isinstance(v, dict):
                result[k] = {dk: (dv.to_dict() if isinstance(dv, ASTNode) else dv) for dk, dv in v.items()}
            else:
                result[k] = v
        return result

# Program Root
@dataclass
class ProgramNode(ASTNode):
    body: List[ASTNode] = field(default_factory=list)

# Declarations & Definitions
@dataclass
class IncludeNode(ASTNode):
    header: str = ""
    is_system: bool = True

@dataclass
class UsingDirectiveNode(ASTNode):
    target: str = ""

@dataclass
class TypeAliasNode(ASTNode):
    name: str = ""
    target_type: str = ""

@dataclass
class NamespaceDefNode(ASTNode):
    name: str = ""
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class EnumDefNode(ASTNode):
    name: str = ""
    is_scoped: bool = False
    base_type: Optional[str] = None
    enumerators: List[Tuple[str, Optional[ASTNode]]] = field(default_factory=list)

@dataclass
class TemplateDefNode(ASTNode):
    params: List[str] = field(default_factory=list)
    declaration: Optional[ASTNode] = None

@dataclass
class ParamNode(ASTNode):
    name: str = ""
    type_name: Optional[str] = None
    default_val: Optional[ASTNode] = None

@dataclass
class FunctionDefNode(ASTNode):
    name: str = ""
    return_type: Optional[str] = "void"
    params: List[ParamNode] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    is_virtual: bool = False
    is_pure_virtual: bool = False
    is_override: bool = False
    is_const: bool = False
    is_static: bool = False
    is_noexcept: bool = False
    is_constexpr: bool = False
    template_params: List[str] = field(default_factory=list)

@dataclass
class ClassDefNode(ASTNode):
    name: str = ""
    body: List[ASTNode] = field(default_factory=list)
    fields: List[ASTNode] = field(default_factory=list)
    methods: List[ASTNode] = field(default_factory=list)
    base_classes: List[Tuple[str, str, bool]] = field(default_factory=list)  # (name, access, is_virtual)
    is_struct: bool = False

@dataclass
class StructDefNode(ASTNode):
    name: str = ""
    fields: List[ASTNode] = field(default_factory=list)
    methods: List[ASTNode] = field(default_factory=list)
    base_classes: List[Tuple[str, str, bool]] = field(default_factory=list)

@dataclass
class VarDeclNode(ASTNode):
    name: str = ""
    type_name: Optional[str] = None
    init_val: Optional[ASTNode] = None
    is_const: bool = False
    is_array: bool = False
    array_size: Optional[ASTNode] = None
    is_static: bool = False
    is_constexpr: bool = False
    is_reference: bool = False
    is_pointer: bool = False

@dataclass
class AssignNode(ASTNode):
    target: str = ""
    value: Optional[ASTNode] = None
    op: str = "="
    target_node: Optional[ASTNode] = None

@dataclass
class ArrayLiteralNode(ASTNode):
    elements: List[ASTNode] = field(default_factory=list)

# Control Flow Statements
@dataclass
class IfNode(ASTNode):
    test: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)
    orelse: List[ASTNode] = field(default_factory=list)

@dataclass
class WhileNode(ASTNode):
    test: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class ForNode(ASTNode):
    init: Optional[ASTNode] = None
    test: Optional[ASTNode] = None
    step: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class RangeForNode(ASTNode):
    var: Optional[ASTNode] = None
    iterable: Optional[ASTNode] = None
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class CatchClauseNode(ASTNode):
    param: Optional[ParamNode] = None
    body: List[ASTNode] = field(default_factory=list)
    is_catch_all: bool = False

@dataclass
class TryCatchNode(ASTNode):
    try_block: List[ASTNode] = field(default_factory=list)
    catch_blocks: List[CatchClauseNode] = field(default_factory=list)

@dataclass
class ThrowNode(ASTNode):
    expr: Optional[ASTNode] = None

@dataclass
class CaseNode(ASTNode):
    value: Optional[ASTNode] = None  # None for default case
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class SwitchNode(ASTNode):
    discriminant: Optional[ASTNode] = None
    cases: List[CaseNode] = field(default_factory=list)

@dataclass
class ReturnNode(ASTNode):
    value: Optional[ASTNode] = None

@dataclass
class PrintNode(ASTNode):
    args: List[ASTNode] = field(default_factory=list)
    format_str: Optional[str] = None
    end: str = "\n"
    raw_printf: bool = False   # True: args are printf arguments for `format_str` (complex specs like %.2f)

@dataclass
class ExprStmtNode(ASTNode):
    expr: Optional[ASTNode] = None

# Expressions
@dataclass
class ConditionalExprNode(ASTNode):
    test: Optional[ASTNode] = None
    true_expr: Optional[ASTNode] = None
    false_expr: Optional[ASTNode] = None

@dataclass
class BinaryOpNode(ASTNode):
    left: Optional[ASTNode] = None
    op: str = "+"
    right: Optional[ASTNode] = None

@dataclass
class UnaryOpNode(ASTNode):
    op: str = "-"
    operand: Optional[ASTNode] = None
    is_postfix: bool = False

@dataclass
class LiteralNode(ASTNode):
    value: Any = None
    lit_type: str = "number"  # number, string, boolean, null
    raw: str = ""

@dataclass
class IdentifierNode(ASTNode):
    name: str = ""

@dataclass
class CallNode(ASTNode):
    callee: str = ""
    args: List[ASTNode] = field(default_factory=list)

@dataclass
class LambdaExprNode(ASTNode):
    params: List[ParamNode] = field(default_factory=list)
    return_type: Optional[str] = None
    captures: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class CastExprNode(ASTNode):
    cast_kind: str = "static"  # static, dynamic, reinterpret, const, cstyle
    target_type: str = ""
    expr: Optional[ASTNode] = None

@dataclass
class ArrayAccessNode(ASTNode):
    array: Optional[ASTNode] = None
    index: Optional[ASTNode] = None

@dataclass
class MemberAccessNode(ASTNode):
    object: Optional[ASTNode] = None
    member: str = ""

@dataclass
class InputNode(ASTNode):
    """Reads values from standard input into `targets`.

    kinds : one entry per target - "int" | "long" | "float" | "double" |
            "char" | "string" | "line" (whole line) | "int_list" | "float_list"
            | "string_list" (all whitespace separated values of the current line)
    mode  : "token" (scanf / cin >> / Scanner.next*) reads whitespace separated
            tokens, "line" (input() / getline / nextLine) reads a whole line.
    """
    targets: List[ASTNode] = field(default_factory=list)
    prompt: Optional[str] = None
    kinds: List[str] = field(default_factory=list)
    mode: str = "token"

@dataclass
class BreakNode(ASTNode):
    pass

@dataclass
class ContinueNode(ASTNode):
    pass

@dataclass
class UnsupportedASTNode(ASTNode):
    raw_kind: str = ""
    text: str = ""
    location: str = ""
    details: str = ""


