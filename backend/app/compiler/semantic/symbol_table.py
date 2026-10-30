"""
Symbol Table data structures for Stage 3: Semantic Analysis.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class Symbol:
    name: str
    type_name: str
    scope_level: int
    line: int
    column: int = 1
    category: str = "variable"  # variable, function, parameter
    is_initialized: bool = False
    reference_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type_name,
            "scope_level": self.scope_level,
            "line": self.line,
            "column": self.column,
            "category": self.category,
            "is_initialized": self.is_initialized,
            "reference_count": self.reference_count
        }

class SymbolTable:
    """Scoped Symbol Table for tracking identifiers across nested scopes."""

    def __init__(self):
        # Stack of scopes (dicts of name -> Symbol)
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.all_symbols: List[Symbol] = []
        self.scope_level = 0

    def enter_scope(self):
        self.scope_level += 1
        self.scopes.append({})

    def exit_scope(self):
        if self.scope_level > 0:
            self.scopes.pop()
            self.scope_level -= 1

    def define(self, symbol: Symbol) -> bool:
        """Defines a symbol in the current innermost scope. Returns False if already declared."""
        curr_scope = self.scopes[-1]
        if symbol.name in curr_scope:
            return False  # Already declared in current scope
        symbol.scope_level = self.scope_level
        curr_scope[symbol.name] = symbol
        self.all_symbols.append(symbol)
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        """Looks up a symbol from innermost to outermost scope."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    def record_usage(self, name: str):
        sym = self.lookup(name)
        if sym:
            sym.reference_count += 1

    def get_all_records(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.all_symbols]
