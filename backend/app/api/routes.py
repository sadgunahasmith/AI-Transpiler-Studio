"""
FastAPI REST API routes for Compiler, AI, Execution, and History endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from .schemas import (
    AnalyzeRequest, DetectErrorsRequest, CorrectRequest,
    TranspileRequest, ExecuteRequest, CompareRequest
)
from ..compiler.pipeline import CompilerPipeline
from ..compiler.lexer import tokenize_code
from ..compiler.parser import parse_code
from ..compiler.semantic import analyze_semantics
from ..ai.corrector import AICorrector
from ..ai.explainer import AIExplainer
from ..ai.heuristic_engine import HeuristicEngine
from ..ai.hybrid_router import HybridRouter
from ..execution.sandbox import ExecutionSandbox
from ..execution.comparator import OutputComparator
from ..database.db import save_history_record, get_history_records, clear_history
from ..samples.code_samples import get_samples

router = APIRouter()
pipeline = CompilerPipeline()
corrector = AICorrector()
explainer = AIExplainer()
heuristic = HeuristicEngine()
hybrid_router = HybridRouter()
sandbox = ExecutionSandbox()
comparator = OutputComparator()

@router.get("/languages")
def get_supported_languages() -> List[Dict[str, Any]]:
    return [
        {"id": "c", "name": "C", "extension": ".c", "monaco_lang": "c", "has_compiler_pipeline": True},
        {"id": "cpp", "name": "C++", "extension": ".cpp", "monaco_lang": "cpp", "has_compiler_pipeline": True},
        {"id": "python", "name": "Python", "extension": ".py", "monaco_lang": "python", "has_compiler_pipeline": True},
        {"id": "javascript", "name": "JavaScript", "extension": ".js", "monaco_lang": "javascript", "has_compiler_pipeline": True},
        {"id": "java", "name": "Java", "extension": ".java", "monaco_lang": "java", "has_compiler_pipeline": True}
    ]

@router.get("/samples")
def list_samples() -> List[Dict[str, Any]]:
    return get_samples()

@router.get("/system-info")
def get_system_runtimes() -> Dict[str, Any]:
    return {
        "runtimes": sandbox.check_system_runtimes(),
        "ai_provider": corrector.provider.get_provider_name(),
        "ai_status": corrector.provider.get_status_info()
    }

@router.post("/analyze")
def analyze_code(req: AnalyzeRequest) -> Dict[str, Any]:
    tokens, lex_errs = tokenize_code(req.language, req.code)
    ast_root, syn_errs = parse_code(req.language, req.code)
    sym_table, sem_diags = analyze_semantics(req.language, ast_root)

    return {
        "language": req.language,
        "token_count": len(tokens),
        "tokens": [t.to_dict() for t in tokens[:300]],
        "ast": ast_root.to_dict() if ast_root else None,
        "symbol_table": sym_table[:300],
        "errors": [e.to_dict() for e in lex_errs] + [e.to_dict() for e in syn_errs] + [s for s in sem_diags if s.get("severity") != "warning"],
        "warnings": [s for s in sem_diags if s.get("severity") == "warning"]
    }

@router.post("/detect-errors")
def detect_errors(req: DetectErrorsRequest) -> Dict[str, Any]:
    # Compiler stage errors
    _, lex_errs = tokenize_code(req.language, req.code)
    _, syn_errs = parse_code(req.language, req.code)
    ast_root, _ = parse_code(req.language, req.code)
    _, sem_diags = analyze_semantics(req.language, ast_root)

    compiler_errors = [e.to_dict() for e in lex_errs] + [e.to_dict() for e in syn_errs]
    compiler_errors.extend(sem_diags)

    # AI suspected issues (logic smells, bugs)
    ai_suspicions = heuristic.detect_ai_suspicions(req.language, req.code)

    all_issues = compiler_errors + ai_suspicions

    return {
        "language": req.language,
        "total_issues": len(all_issues),
        "compiler_errors": compiler_errors,
        "ai_suspicions": ai_suspicions,
        "all_issues": all_issues
    }

@router.post("/correct")
def auto_correct(req: CorrectRequest) -> Dict[str, Any]:
    errs = req.compiler_errors
    if errs is None:
        # Detect errors automatically
        det = detect_errors(DetectErrorsRequest(language=req.language, code=req.code))
        errs = det["all_issues"]

    result = corrector.correct_code(req.language, req.code, errs)
    return result

@router.post("/transpile")
def transpile(req: TranspileRequest) -> Dict[str, Any]:
    result = hybrid_router.process(
        source_language=req.source_language,
        target_language=req.target_language,
        source_code=req.code,
        ai_mode=req.ai_mode or "compiler_only",
        optimize=req.optimize
    )

    # Save run in database
    target_code = result.get("transpiled_code", "")
    try:
        save_history_record(
            source_lang=req.source_language,
            target_lang=req.target_language,
            original_code=req.code,
            corrected_code=result.get("corrected_source_code", "") or "",
            target_code=target_code,
            errors=result.get("errors", []),
            execution_match=None,
            notes=f"Mode: {result.get('mode_used', 'compiler_only')} | Opt: {req.optimize}"
        )
    except Exception:
        pass

    return result

@router.post("/execute")
def execute_code(req: ExecuteRequest) -> Dict[str, Any]:
    res = sandbox.execute(req.language, req.code, req.stdin or "")
    return res

@router.post("/compare")
def compare_executions(req: CompareRequest) -> Dict[str, Any]:
    # Execute source code
    source_res = sandbox.execute(req.source_language, req.source_code, req.stdin or "")
    # Execute target code
    target_res = sandbox.execute(req.target_language, req.target_code, req.stdin or "")

    comp_res = comparator.compare(
        source_stdout=source_res.get("stdout", ""),
        target_stdout=target_res.get("stdout", ""),
        source_stderr=source_res.get("stderr", ""),
        target_stderr=target_res.get("stderr", ""),
        source_success=bool(source_res.get("success", False)),
        target_success=bool(target_res.get("success", False))
    )

    return {
        "source_execution": source_res,
        "target_execution": target_res,
        "comparison": comp_res
    }

@router.get("/history")
def list_history() -> List[Dict[str, Any]]:
    return get_history_records(limit=30)

@router.delete("/history")
def purge_history() -> Dict[str, str]:
    clear_history()
    return {"message": "Translation history cleared successfully."}
