"""
Intermediate Representation module entry point for Stage 4.
"""
from typing import Optional
from .ir_nodes import IRProgram, IRFunction, IRInstruction
from .ir_builder import IRBuilder
from ..parser.ast_nodes import ProgramNode

def build_ir(ast_root: Optional[ProgramNode]) -> IRProgram:
    builder = IRBuilder()
    return builder.build_ir(ast_root)

__all__ = ["build_ir", "IRProgram", "IRFunction", "IRInstruction", "IRBuilder"]
