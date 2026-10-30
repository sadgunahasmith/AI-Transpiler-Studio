"""
AI Error Corrector & Code Repair Module.
Preserves programmer logic, produces transparent change explanations,
and revalidates repaired code against compiler stages.
"""
from typing import Dict, Any, List, Tuple
from .provider import AIProvider
from .heuristic_engine import HeuristicEngine
from ..compiler.parser import parse_code

class AICorrector:
    """Intelligently repairs erroneous source code and revalidates changes."""

    def __init__(self):
        self.provider = AIProvider()
        self.heuristic = HeuristicEngine()

    def correct_code(
        self,
        language: str,
        source_code: str,
        compiler_errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates corrected code, tracks modifications, and revalidates."""
        corrected_code = source_code
        modifications: List[Dict[str, Any]] = []
        explanation = ""
        telemetry = {}

        # Step 1: Use Heuristic Engine first to reliably patch confirmed syntax & delimiter issues
        heuristic_code, mods = self.heuristic.auto_correct(language, source_code, compiler_errors)
        if mods:
            corrected_code = heuristic_code
            modifications.extend(mods)

        # Step 2: Validate current state
        ast_reval, reval_errors = parse_code(language, corrected_code)
        remaining_errs = [e.to_dict() for e in reval_errors]

        # Step 3: If errors remain and Gemini AI is configured, invoke Gemini 2.5 Flash for intelligent repair
        if remaining_errs and self.provider.is_configured():
            prompt = (
                f"You are an expert compiler and code repair engine.\n"
                f"Programming Language: {language}\n\n"
                f"Original Code:\n```{language}\n{corrected_code}\n```\n\n"
                f"Remaining Compiler Errors:\n{remaining_errs}\n\n"
                f"Instructions:\n"
                f"1. Fix the syntax and structural errors while preserving the exact program logic.\n"
                f"2. Enclose the complete corrected code in a single markdown block (```{language} ... ```).\n"
                f"3. Provide a concise bulleted explanation of each change made below the code block."
            )
            ai_text, ai_telemetry = self.provider.query_model(
                prompt,
                system_prompt="You are an expert compiler design engineer and automated code repair tutor."
            )
            telemetry = ai_telemetry
            if ai_text:
                import re
                code_match = re.search(r"```(?:\w+)?\s*\n(.*?)\n```", ai_text, re.DOTALL)
                if code_match:
                    proposed_code = code_match.group(1).strip()
                    # Revalidate proposed code
                    ast_ai, errs_ai = parse_code(language, proposed_code)
                    if len(errs_ai) <= len(remaining_errs):
                        corrected_code = proposed_code
                        ast_reval = ast_ai
                        remaining_errs = [e.to_dict() for e in errs_ai]
                        modifications.append({
                            "line": 1,
                            "type": "Gemini AI Structural Repair",
                            "description": "Repaired code syntax and structures using Gemini 2.5 Flash",
                            "rationale": "Resolved remaining compiler diagnostics while preserving program logic."
                        })
                # Use AI explanation or excerpt
                explanation = ai_text

        elif self.provider.is_configured() and not remaining_errs:
            # Query Gemini for educational explanation if desired
            prompt = (
                f"Language: {language}\n"
                f"Source Code:\n{source_code}\n"
                f"Repairs Applied:\n{modifications}\n"
                f"Provide a brief 2-sentence pedagogical note on the grammar rules involved."
            )
            ai_text, ai_telemetry = self.provider.query_model(prompt)
            telemetry = ai_telemetry
            explanation = ai_text or "All syntax requirements satisfied."

        else:
            # Generate structured pedagogical explanation from heuristics
            if modifications:
                lines_exp = [f"- **Line {m['line']}** ({m['type']}): {m['description']}. *Reason:* {m['rationale']}" for m in modifications]
                explanation = "### AI Diagnostic & Repair Summary\n\n" + "\n".join(lines_exp)
            else:
                explanation = "No syntactic repair modifications were necessary. The source code adheres to grammar standards."

        is_revalidated = len(remaining_errs) == 0

        return {
            "original_code": source_code,
            "corrected_code": corrected_code,
            "modifications": modifications,
            "explanation": explanation,
            "revalidated": is_revalidated,
            "remaining_errors": remaining_errs,
            "provider_used": self.provider.get_provider_name(),
            "ai_telemetry": telemetry
        }
