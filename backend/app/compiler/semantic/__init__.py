"""
Semantic Analysis module entry point for Stage 3: Semantic Analysis.
"""
from typing import List, Dict, Any, Tuple, Optional
from .analyzer import SemanticAnalyzer
from .symbol_table import SymbolTable, Symbol
from ..parser.ast_nodes import ProgramNode

def analyze_semantics(language: str, ast: Optional[ProgramNode]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    analyzer = SemanticAnalyzer(language)
    return analyzer.analyze(ast)

__all__ = ["analyze_semantics", "SemanticAnalyzer", "SymbolTable", "Symbol"]
