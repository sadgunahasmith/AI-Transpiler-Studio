"""
Master Compiler Pipeline Coordinator.
Orchestrates Stages 1-6: Lexical, Syntax, Semantic, IR, Optimization, and Code Generation.
"""
from typing import Dict, Any, List, Optional
import time
from .lexer import tokenize_code
from .parser import parse_code
from .semantic import analyze_semantics
from .ir import build_ir
from .optimizer import optimize_program
from .codegen import generate_target_code, validate_target_code

class CompilerPipeline:
    """Orchestrates all 6 traditional compiler stages with precise microsecond telemetry."""

    def __init__(self):
        pass

    def run_full_pipeline(
        self,
        source_language: str,
        target_language: str,
        source_code: str,
        optimize: bool = True,
        parser_mode: Optional[str] = "auto"
    ) -> Dict[str, Any]:
        """Runs stages 1 through 6 in sequence."""
        t_pipeline_start = time.perf_counter()
        report = {
            "source_language": source_language,
            "target_language": target_language,
            "success": True,
            "errors": [],
            "warnings": [],
            "stages": {},
            "stage_timings": {}
        }

        # Stage 1: Lexical Analysis
        t0 = time.perf_counter()
        tokens, lex_errors = tokenize_code(source_language, source_code)
        lex_ms = round((time.perf_counter() - t0) * 1000, 3)
        token_dicts = [t.to_dict() for t in tokens]
        report["stages"]["lexical"] = {
            "token_count": len(tokens),
            "tokens": token_dicts[:150],  # sample or full list
            "errors": [e.to_dict() for e in lex_errors],
            "execution_time_ms": lex_ms
        }
        report["stage_timings"]["lexical_ms"] = lex_ms
        for le in lex_errors:
            report["errors"].append(le.to_dict())

        # Stage 2: Syntax Analysis
        t0 = time.perf_counter()
        ast_root, syn_errors = parse_code(source_language, source_code, parser_mode=parser_mode)
        syn_ms = round((time.perf_counter() - t0) * 1000, 3)
        report["stages"]["syntax"] = {
            "ast": ast_root.to_dict() if ast_root else None,
            "errors": [se.to_dict() for se in syn_errors],
            "execution_time_ms": syn_ms,
            "parser_mode": parser_mode
        }
        report["stage_timings"]["syntax_ms"] = syn_ms
        for se in syn_errors:
            report["errors"].append(se.to_dict())

        # Stage 3: Semantic Analysis
        t0 = time.perf_counter()
        symbol_table_records, sem_diagnostics = analyze_semantics(source_language, ast_root)
        sem_ms = round((time.perf_counter() - t0) * 1000, 3)
        report["stages"]["semantic"] = {
            "symbol_table": symbol_table_records,
            "diagnostics": sem_diagnostics,
            "execution_time_ms": sem_ms
        }
        report["stage_timings"]["semantic_ms"] = sem_ms
        for sd in sem_diagnostics:
            if sd.get("severity") == "warning":
                report["warnings"].append(sd)
            else:
                report["errors"].append(sd)

        # If there are hard syntax errors that prevented AST generation, we report and stop before codegen
        if not ast_root:
            report["success"] = False
            report["error_summary"] = "Syntax analysis failed. Please fix errors or apply auto-correction."
            report["stage_timings"]["total_ms"] = round((time.perf_counter() - t_pipeline_start) * 1000, 3)
            report["total_pipeline_ms"] = report["stage_timings"]["total_ms"]
            return report

        # Stage 4: Intermediate Representation
        t0 = time.perf_counter()
        ir_prog = build_ir(ast_root)
        ir_ms = round((time.perf_counter() - t0) * 1000, 3)
        report["stages"]["ir"] = {
            "tac": ir_prog.to_tac(),
            "ir_tree": ir_prog.to_dict(),
            "execution_time_ms": ir_ms
        }
        report["stage_timings"]["ir_ms"] = ir_ms

        # Stage 5: Optimization
        t0 = time.perf_counter()
        working_ast = ast_root
        opt_stats = {"enabled": optimize}
        if optimize:
            opt_ast, stats = optimize_program(working_ast)
            working_ast = opt_ast or working_ast
            opt_stats.update(stats)
            # Rebuild optimized IR TAC
            opt_ir_prog = build_ir(working_ast)
            opt_ms = round((time.perf_counter() - t0) * 1000, 3)
            report["stages"]["optimized_ir"] = {
                "tac": opt_ir_prog.to_tac(),
                "stats": opt_stats,
                "execution_time_ms": opt_ms
            }
        else:
            opt_ms = round((time.perf_counter() - t0) * 1000, 3)
            report["stages"]["optimized_ir"] = {
                "tac": ir_prog.to_tac(),
                "stats": {"enabled": False, "constants_folded": 0, "expressions_simplified": 0, "dead_code_eliminated": 0},
                "execution_time_ms": opt_ms
            }
        report["stage_timings"]["optimizer_ms"] = opt_ms

        # Stage 6: Target Code Generation
        t0 = time.perf_counter()
        if working_ast is not None:
            working_ast.source_language = source_language
        target_code = generate_target_code(target_language, working_ast)
        validation_res = validate_target_code(target_language, target_code)
        codegen_ms = round((time.perf_counter() - t0) * 1000, 3)

        report["stages"]["codegen"] = {
            "target_code": target_code,
            "validation": validation_res,
            "execution_time_ms": codegen_ms
        }
        report["stage_timings"]["codegen_ms"] = codegen_ms
        report["transpiled_code"] = target_code
        report["is_valid_target"] = validation_res.get("valid", True)

        total_ms = round((time.perf_counter() - t_pipeline_start) * 1000, 3)
        report["stage_timings"]["total_ms"] = total_ms
        report["total_pipeline_ms"] = total_ms

        return report
