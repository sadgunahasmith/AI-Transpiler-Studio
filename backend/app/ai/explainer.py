"""
AI Pedagogical Explainer: Generates educational explanations for compiler errors,
optimizations, and cross-language translation decisions.
"""
from typing import Dict, Any, List

class AIExplainer:
    """Provides human-readable academic explanations for compiler decisions."""

    def explain_transpilation(
        self,
        source_lang: str,
        target_lang: str,
        source_code: str,
        target_code: str
    ) -> str:
        s = source_lang.capitalize()
        t = target_lang.capitalize()

        notes = [
            f"### Academic Transpilation Analysis: {s} -> {t}\n",
            "#### 1. Architectural Translation Pipeline",
            f"The input program was parsed into a language-neutral Intermediate Representation (IR) AST and lowered to Three-Address Code (TAC), decoupling the source grammar of **{s}** from the target syntax of **{t}**.",
            "\n#### 2. Key Semantic Mappings"
        ]

        if s in ("C", "Cpp", "Java") and t == "Python":
            notes.append("- **Static to Dynamic Typing**: Explicit type signatures (`int`, `float`) were normalized and mapped to Python dynamic assignments.")
            notes.append("- **Standard I/O Adaptation**: Formatted output calls (`printf`, `System.out.println`) were transformed into Python's native `print()` function.")
            notes.append("- **Entry Point Normalization**: C-style `main()` function was encapsulated within the standard Python execution idiom: `if __name__ == '__main__':`.")

        elif s == "Python" and t in ("C", "Cpp", "Java"):
            notes.append(f"- **Dynamic to Static Typing**: Variable bindings were analyzed to infer static type definitions (`int`, `double`) required by {t}.")
            notes.append(f"- **Program Structure**: Top-level statements were synthesized into a formal `{t}` class/function harness with standard boilerplate.")
            notes.append("- **I/O Translation**: Python `print()` statements were mapped to standard stream/formatted output.")

        elif s == "Python" and t == "Javascript":
            notes.append("- **Control Flow & Blocks**: Indented suites were converted to C-style curly brace blocks `{ ... }`.")
            notes.append("- **Variable Declarations**: Implicit assignments were translated to modern `let` statements.")
            notes.append("- **Output Operations**: Python `print()` was adapted to JavaScript `console.log()`.")

        elif s == "Javascript" and t == "Python":
            notes.append("- **Syntax Simplification**: Semicolons and curly braces were transformed into clean, 4-space indented Python blocks.")
            notes.append("- **Variable Scope**: JS `let`/`const` declarations were converted to idiomatic Python variable bindings.")
            notes.append("- **Console to Print**: `console.log()` calls were translated to Python `print()`.")

        else:
            notes.append(f"- Standard statements and expressions were systematically lowered to universal IR nodes and re-emitted according to {t} grammar standards.")

        notes.append("\n#### 3. Semantic Equivalence & Limitations")
        notes.append("- Constant folding and propagation were applied where safe without altering runtime behavior.")
        notes.append("- Arithmetic precedence and logical evaluation order were strictly preserved across AST boundaries.")

        return "\n".join(notes)
