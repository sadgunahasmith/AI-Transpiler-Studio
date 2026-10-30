"""Shared helpers for emitting standard-input code in the target generators."""
import re
from typing import Any, Set
from ..parser.ast_nodes import ASTNode, InputNode, IdentifierNode

NUMERIC_KINDS = ("int", "long", "float", "double")
LIST_KINDS = ("int_list", "float_list", "string_list")


def walk(node: Any):
    """Yields every ASTNode reachable from `node`."""
    if isinstance(node, list):
        for item in node:
            yield from walk(item)
    elif isinstance(node, ASTNode):
        yield node
        for v in node.__dict__.values():
            if isinstance(v, (list, ASTNode)):
                yield from walk(v)


def has_input(ast_root: Any) -> bool:
    return any(isinstance(n, InputNode) for n in walk(ast_root))


def string_input_names(ast_root: Any) -> Set[str]:
    """Names of simple variables that receive string / line values from stdin."""
    names: Set[str] = set()
    for n in walk(ast_root):
        if isinstance(n, InputNode):
            for i, t in enumerate(n.targets):
                kind = n.kinds[i] if i < len(n.kinds) else ""
                if isinstance(t, IdentifierNode) and kind in ("string", "line"):
                    names.add(t.name)
    return names


def kind_of(stmt: InputNode, i: int) -> str:
    return stmt.kinds[i] if i < len(stmt.kinds) else "int"


_LEN_MOD = re.compile(r"(%[-+ #0]*\d*(?:\.\d+)?)(?:hh|h|ll|l|L|z|j|t)([diouxXeEfFgGcs])")


def sanitize_printf_format(fmt: str, target: str) -> str:
    """Adapts a C printf format string for Python (% operator) or Java (printf)."""
    fmt = _LEN_MOD.sub(r"\1\2", fmt)
    if target == "java":
        fmt = re.sub(r"%([-+ #0]*\d*(?:\.\d+)?)[iu]", r"%\1d", fmt)
    return fmt
