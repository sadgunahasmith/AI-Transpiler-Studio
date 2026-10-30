"""
Heuristic Expert Engine: Offline AI fallback for error detection, diagnosis, and repair.
Works 100% reliably without requiring external cloud API keys.
"""
import re
from typing import List, Dict, Any, Tuple

class HeuristicEngine:
    """Rule-based expert system simulating compiler repair and pedagogical diagnosis."""

    def auto_correct(
        self,
        language: str,
        code: str,
        compiler_errors: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Repairs source code based on compiler diagnostics and grammar rules."""
        lang = language.strip().lower()
        lines = code.split("\n")
        modifications: List[Dict[str, Any]] = []

        # 1. Fix missing semicolons in C, C++, Java, JS
        if lang in ("c", "cpp", "c++", "java", "javascript", "js"):
            for err in compiler_errors:
                msg = err.get("message", "").lower()
                line_idx = err.get("line", 1) - 1
                if 0 <= line_idx < len(lines):
                    curr_line = lines[line_idx]
                    stripped = curr_line.rstrip()
                    if ("missing semicolon" in msg or "expected ';'" in msg) and not stripped.endswith(";"):
                        lines[line_idx] = stripped + ";"
                        modifications.append({
                            "line": line_idx + 1,
                            "type": "Syntax Correction",
                            "description": f"Added missing semicolon ';' to statement: '{stripped}'",
                            "rationale": f"{language.upper()} grammar requires every simple expression and declaration statement to terminate with a semicolon."
                        })

        # 2. Fix missing colons in Python
        if lang in ("python", "py"):
            for i, line in enumerate(lines):
                stripped = line.strip()
                if (re.match(r'^(def\s+\w+\s*\(.*\)|if\s+.*|elif\s+.*|else|while\s+.*|for\s+.*in\s+.*)', stripped) and
                    not stripped.endswith(":")):
                    lines[i] = line.rstrip() + ":"
                    modifications.append({
                        "line": i + 1,
                        "type": "Syntax Correction",
                        "description": f"Added missing colon ':' to compound statement header: '{stripped}'",
                        "rationale": "Python syntax mandates a colon ':' at the end of block header statements before an indented suite."
                    })

        # 3. Fix unclosed parentheses or brackets
        for i, line in enumerate(lines):
            open_p = line.count("(")
            close_p = line.count(")")
            if open_p > close_p:
                needed = open_p - close_p
                lines[i] = line.rstrip() + (")" * needed)
                modifications.append({
                    "line": i + 1,
                    "type": "Delimiter Balancing",
                    "description": f"Appended {needed} missing closing parenthesis ')'",
                    "rationale": "Mismatched parentheses prevent parser from building an expression subtree."
                })

        # 4. Check missing C headers if printf is used without stdio.h
        if lang in ("c", "cpp", "c++"):
            full_code = "\n".join(lines)
            if "printf" in full_code and "#include <stdio.h>" not in full_code:
                lines.insert(0, "#include <stdio.h>")
                modifications.append({
                    "line": 1,
                    "type": "Header Inclusion",
                    "description": "Included standard I/O header <stdio.h>",
                    "rationale": "The printf function requires declaration from <stdio.h> in standard C."
                })
            if "cout" in full_code and "#include <iostream>" not in full_code:
                lines.insert(0, "#include <iostream>\nusing namespace std;")
                modifications.append({
                    "line": 1,
                    "type": "Header Inclusion",
                    "description": "Included <iostream> and namespace std for cout",
                    "rationale": "cout is declared in C++ standard header <iostream> under namespace std."
                })

        corrected_code = "\n".join(lines)
        return corrected_code, modifications

    def detect_ai_suspicions(self, language: str, code: str) -> List[Dict[str, Any]]:
        """Identifies subtle code smells, potential logic traps, and non-fatal issues."""
        suspicions = []
        lang = language.strip().lower()
        lines = code.split("\n")

        for idx, line in enumerate(lines, 1):
            s = line.strip()

            # Assignment inside if condition in C/C++/Java/JS: if (x = 5)
            if re.search(r'\bif\s*\([^=]*=[^=]*\)', s):
                suspicions.append({
                    "line": idx,
                    "column": 1,
                    "message": "Potential accidental assignment '=' inside condition instead of comparison '=='",
                    "severity": "warning",
                    "source": "ai",
                    "category": "AI Logic Suspicion",
                    "suggested_fix": "Replace '=' with '==' if checking equality"
                })

            # Empty while/for loop body with semicolon: while(cond);
            if re.search(r'\b(while|for)\s*\([^)]*\)\s*;', s):
                suspicions.append({
                    "line": idx,
                    "column": 1,
                    "message": "Potentially unintentional empty loop body terminated by immediate semicolon ';'",
                    "severity": "warning",
                    "source": "ai",
                    "category": "AI Logic Suspicion",
                    "suggested_fix": "Remove the trailing ';' or enclose loop body in braces"
                })

            # Floating point equality comparison: == on floats
            if re.search(r'==\s*\d+\.\d+', s):
                suspicions.append({
                    "line": idx,
                    "column": 1,
                    "message": "Exact floating-point equality comparison may fail due to precision rounding",
                    "severity": "info",
                    "source": "ai",
                    "category": "AI Code Quality",
                    "suggested_fix": "Use an epsilon threshold comparison e.g. fabs(a - b) < 1e-6"
                })

        return suspicions
