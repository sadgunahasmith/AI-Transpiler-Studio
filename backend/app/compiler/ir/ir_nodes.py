"""
Language-Neutral Intermediate Representation (IR) and Three-Address Code (TAC) definitions.
Stage 4: Intermediate Representation
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class IRInstruction:
    def to_tac(self) -> str:
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.__class__.__name__, "tac": self.to_tac()}

@dataclass
class IRLabel(IRInstruction):
    name: str

    def to_tac(self) -> str:
        return f"{self.name}:"

@dataclass
class IRAssign(IRInstruction):
    target: str
    source: str

    def to_tac(self) -> str:
        return f"  {self.target} = {self.source}"

@dataclass
class IRBinaryOp(IRInstruction):
    target: str
    left: str
    op: str
    right: str

    def to_tac(self) -> str:
        return f"  {self.target} = {self.left} {self.op} {self.right}"

@dataclass
class IRUnaryOp(IRInstruction):
    target: str
    op: str
    operand: str

    def to_tac(self) -> str:
        return f"  {self.target} = {self.op}{self.operand}"

@dataclass
class IRJump(IRInstruction):
    target_label: str

    def to_tac(self) -> str:
        return f"  GOTO {self.target_label}"

@dataclass
class IRJumpIf(IRInstruction):
    condition: str
    target_label: str

    def to_tac(self) -> str:
        return f"  IF {self.condition} GOTO {self.target_label}"

@dataclass
class IRJumpIfNot(IRInstruction):
    condition: str
    target_label: str

    def to_tac(self) -> str:
        return f"  IF_NOT {self.condition} GOTO {self.target_label}"

@dataclass
class IRCall(IRInstruction):
    target: Optional[str]
    func_name: str
    args: List[str]

    def to_tac(self) -> str:
        args_str = ", ".join(self.args)
        if self.target:
            return f"  {self.target} = CALL {self.func_name}({args_str})"
        return f"  CALL {self.func_name}({args_str})"

@dataclass
class IRPrint(IRInstruction):
    args: List[str]

    def to_tac(self) -> str:
        return f"  PRINT {', '.join(self.args)}"

@dataclass
class IRReturn(IRInstruction):
    value: Optional[str] = None

    def to_tac(self) -> str:
        if self.value:
            return f"  RETURN {self.value}"
        return "  RETURN"

@dataclass
class IRFunction:
    name: str
    params: List[str] = field(default_factory=list)
    return_type: str = "void"
    instructions: List[IRInstruction] = field(default_factory=list)

    def to_tac(self) -> str:
        lines = [f"FUNCTION {self.name}({', '.join(self.params)}):"]
        for instr in self.instructions:
            lines.append(instr.to_tac())
        lines.append(f"END_FUNCTION {self.name}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "params": self.params,
            "return_type": self.return_type,
            "instructions": [instr.to_dict() for instr in self.instructions]
        }

@dataclass
class IRProgram:
    functions: List[IRFunction] = field(default_factory=list)
    globals: List[IRInstruction] = field(default_factory=list)

    def to_tac(self) -> str:
        sections = []
        if self.globals:
            sections.append("// --- Global Section ---")
            for instr in self.globals:
                sections.append(instr.to_tac())
            sections.append("")
        for fn in self.functions:
            sections.append(fn.to_tac())
            sections.append("")
        return "\n".join(sections)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globals": [g.to_dict() for g in self.globals],
            "functions": [fn.to_dict() for fn in self.functions],
            "tac": self.to_tac()
        }
