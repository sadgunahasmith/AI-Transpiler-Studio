"""
Hybrid AI + Compiler Router.
Coordinates execution across 3 distinct operational modes:
1. Compiler Only (Pure deterministic classical 6-stage pipeline)
2. Compiler + Gemini Correction (Compiler diagnostics + Gemini 2.5 Flash repair)
3. AI-Assisted Translation (High-fidelity semantic translation for complex/unsupported patterns)
"""
import re
import time
from typing import Dict, Any, Optional
from ..compiler.pipeline import CompilerPipeline
from ..compiler.parser import parse_code
from ..compiler.codegen import validate_target_code
from .provider import AIProvider
from .corrector import AICorrector
from .explainer import AIExplainer

class HybridRouter:
    """Orchestrates deterministic compilation and Gemini AI assistance."""

    def __init__(self):
        self.pipeline = CompilerPipeline()
        self.provider = AIProvider()
        self.corrector = AICorrector()
        self.explainer = AIExplainer()

    def process(
        self,
        source_language: str,
        target_language: str,
        source_code: str,
        ai_mode: str = "compiler_only",
        optimize: bool = True
    ) -> Dict[str, Any]:
        """Routes request based on chosen AI mode."""
        mode = ai_mode.strip().lower()

        if mode in ("compiler_only", "compiler"):
            return self._process_compiler_only(source_language, target_language, source_code, optimize)
        elif mode in ("hybrid_correction", "hybrid", "correction"):
            return self._process_hybrid_correction(source_language, target_language, source_code, optimize)
        elif mode in ("ai_assisted", "ai", "ai_translation"):
            return self._process_ai_assisted(source_language, target_language, source_code, optimize)
        else:
            # Default to compiler only
            return self._process_compiler_only(source_language, target_language, source_code, optimize)

    def _process_compiler_only(
        self,
        source_language: str,
        target_language: str,
        source_code: str,
        optimize: bool
    ) -> Dict[str, Any]:
        """Mode 1: Pure classical 6-stage compiler pipeline."""
        result = self.pipeline.run_full_pipeline(
            source_language=source_language,
            target_language=target_language,
            source_code=source_code,
            optimize=optimize
        )
        result["mode_used"] = "compiler_only"
        result["ai_used"] = False
        result["ai_telemetry"] = {
            "mode": "Compiler Only",
            "provider": "None (Classical Compiler Pipeline)",
            "latency_ms": 0.0
        }

        # Generate educational explanation
        target_code = result.get("transpiled_code", "")
        result["ai_explanation"] = self.explainer.explain_transpilation(
            source_lang=source_language,
            target_lang=target_language,
            source_code=source_code,
            target_code=target_code
        )
        return result

    def _process_hybrid_correction(
        self,
        source_language: str,
        target_language: str,
        source_code: str,
        optimize: bool
    ) -> Dict[str, Any]:
        """Mode 2: Compiler Error Detection + Deterministic & Gemini Correction -> Transpile."""
        # 1. Check if source code has syntax/semantic errors
        ast_root, syn_errors = parse_code(source_language, source_code)
        error_dicts = [e.to_dict() for e in syn_errors]

        working_code = source_code
        correction_result = None
        ai_used = False

        if error_dicts:
            # Errors found: perform correction
            correction_result = self.corrector.correct_code(
                language=source_language,
                source_code=source_code,
                compiler_errors=error_dicts
            )
            working_code = correction_result.get("corrected_code", source_code)
            ai_used = bool(correction_result.get("ai_telemetry", {}).get("success", False))

        # 2. Run compiler pipeline on the repaired code
        result = self.pipeline.run_full_pipeline(
            source_language=source_language,
            target_language=target_language,
            source_code=working_code,
            optimize=optimize
        )
        result["mode_used"] = "hybrid_correction"
        result["ai_used"] = ai_used
        result["corrected_source_code"] = working_code if working_code != source_code else None
        result["correction_details"] = correction_result
        result["ai_telemetry"] = (
            correction_result.get("ai_telemetry", {})
            if correction_result
            else {"mode": "Hybrid Correction", "provider": self.provider.get_provider_name(), "latency_ms": 0.0}
        )

        target_code = result.get("transpiled_code", "")
        result["ai_explanation"] = (
            correction_result.get("explanation")
            if correction_result and correction_result.get("explanation")
            else self.explainer.explain_transpilation(
                source_lang=source_language,
                target_lang=target_language,
                source_code=working_code,
                target_code=target_code
            )
        )
        return result

    def _process_ai_assisted(
        self,
        source_language: str,
        target_language: str,
        source_code: str,
        optimize: bool
    ) -> Dict[str, Any]:
        """Mode 3: Traditional compiler with Gemini translation fallback for complex idioms."""
        # First attempt standard pipeline
        compiler_res = self.pipeline.run_full_pipeline(
            source_language=source_language,
            target_language=target_language,
            source_code=source_code,
            optimize=optimize
        )

        # If compiler succeeded with clean valid output and no errors, preserve it
        if compiler_res.get("success", False) and not compiler_res.get("errors", []):
            compiler_res["mode_used"] = "ai_assisted"
            compiler_res["ai_used"] = False
            compiler_res["translation_source"] = "compiler_pipeline"
            compiler_res["ai_telemetry"] = {
                "mode": "AI-Assisted Translation",
                "note": "Source grammar fully parsed by traditional compiler; AI fallback was not required.",
                "latency_ms": 0.0
            }
            compiler_res["ai_explanation"] = self.explainer.explain_transpilation(
                source_lang=source_language,
                target_lang=target_language,
                source_code=source_code,
                target_code=compiler_res.get("transpiled_code", "")
            )
            return compiler_res

        # If compiler had errors or failed and Gemini is configured, invoke Gemini for semantic translation
        if self.provider.is_configured():
            prompt = (
                f"You are an expert compiler engineer performing accurate code transpilation.\n"
                f"Source Language: {source_language}\n"
                f"Target Language: {target_language}\n\n"
                f"Source Code:\n```{source_language}\n{source_code}\n```\n\n"
                f"Instructions:\n"
                f"1. Transpile the source program into idiomatic, compilable {target_language}.\n"
                f"2. Faithfully preserve all algorithms, variable states, and program logic.\n"
                f"3. Enclose the transpiled code in a single markdown code block (```{target_language} ... ```).\n"
                f"4. Following the code block, list brief notes explaining key semantic adaptations."
            )
            ai_text, ai_telemetry = self.provider.query_model(
                prompt,
                system_prompt="You are an expert compiler design engineer specializing in semantic code translation."
            )
            if ai_text:
                code_match = re.search(rf"```(?:{target_language}|\w+)?\s*\n(.*?)\n```", ai_text, re.DOTALL)
                target_code = code_match.group(1).strip() if code_match else ai_text.strip()
                val_res = validate_target_code(target_language, target_code)

                return {
                    "source_language": source_language,
                    "target_language": target_language,
                    "success": val_res.get("valid", True),
                    "errors": compiler_res.get("errors", []),
                    "warnings": compiler_res.get("warnings", []),
                    "stages": compiler_res.get("stages", {}),
                    "stage_timings": compiler_res.get("stage_timings", {}),
                    "total_pipeline_ms": compiler_res.get("total_pipeline_ms", 0),
                    "transpiled_code": target_code,
                    "is_valid_target": val_res.get("valid", True),
                    "mode_used": "ai_assisted",
                    "ai_used": True,
                    "translation_source": "gemini_model",
                    "ai_telemetry": ai_telemetry,
                    "ai_explanation": ai_text
                }

        # If Gemini is not configured, return standard compiler result with diagnostic
        compiler_res["mode_used"] = "ai_assisted"
        compiler_res["ai_used"] = False
        compiler_res["translation_source"] = "compiler_pipeline"
        compiler_res["ai_telemetry"] = {
            "mode": "AI-Assisted Translation",
            "error": "Gemini API key is not configured; fell back to compiler pipeline.",
            "latency_ms": 0.0
        }
        return compiler_res
