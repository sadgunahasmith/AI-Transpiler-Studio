"""
Comprehensive Automated Test Suite for AI Transpiler and Compiler Pipeline.
Tests:
1. C Prompt Error Detection & Semicolon Auto-Correction & C->Python Transpilation & Execution.
2. Vertical Slice: Python -> JavaScript transpilation and Node.js execution.
3. Vertical Slice: JavaScript -> Python transpilation and Python execution.
4. Compiler Stages 1-6 (Tokens, AST, Symbol Table, IR TAC, Optimizer constant folding).
5. Output equivalence comparator.
"""
import sys
import os

# Enable execution for local regression tests
os.environ["ALLOW_UNTRUSTED_EXECUTION"] = "true"

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.compiler.pipeline import CompilerPipeline
from app.compiler.lexer import tokenize_code
from app.compiler.parser import parse_code
from app.compiler.semantic import analyze_semantics
from app.compiler.ir import build_ir
from app.compiler.optimizer import optimize_program
from app.compiler.codegen import generate_target_code, validate_target_code
from app.ai.corrector import AICorrector
from app.execution.sandbox import ExecutionSandbox
from app.execution.comparator import OutputComparator

def test_prompt_c_to_python_demo():
    print("\n--- Test 1: User Prompt C -> Python Demo ---")
    c_buggy_code = """#include <stdio.h>

int main() {
    int a = 10
    int b = 20;

    printf("%d", a + b)

    return 0;
}"""

    # Stage 1 & 2: Error detection
    _, syn_errors = parse_code("c", c_buggy_code)
    print(f"Detected {len(syn_errors)} syntax errors:")
    for err in syn_errors:
        print(f"  Line {err.line}: {err.message}")

    assert len(syn_errors) >= 2, f"Expected at least 2 missing semicolons, got {len(syn_errors)}"
    err_lines = [e.line for e in syn_errors]
    assert 4 in err_lines, "Expected missing semicolon on line 4 (int a = 10)"
    assert 7 in err_lines, "Expected missing semicolon on line 7 (printf statement)"

    # AI Auto-Correction
    corrector = AICorrector()
    correction_result = corrector.correct_code("c", c_buggy_code, [e.to_dict() for e in syn_errors])
    corrected_c = correction_result["corrected_code"]
    print("\nCorrected C Code:")
    print(corrected_c)
    assert "int a = 10;" in corrected_c, "Failed to restore semicolon after 'int a = 10'"
    assert 'printf("%d", a + b);' in corrected_c, "Failed to restore semicolon after 'printf'"
    assert correction_result["revalidated"] is True, "Corrected code failed revalidation!"

    # Transpilation to Python
    pipeline = CompilerPipeline()
    transpile_result = pipeline.run_full_pipeline("c", "python", corrected_c, optimize=True)
    python_code = transpile_result["transpiled_code"]
    print("\nGenerated Python Code:")
    print(python_code)
    assert "def main():" in python_code, "Generated Python code should contain main function"
    assert "a = 10" in python_code or "a = 10;" in python_code or "10" in python_code

    # Execute Python in Sandbox
    sandbox = ExecutionSandbox()
    py_exec = sandbox.execute("python", python_code)
    print("\nPython Execution Result:")
    print(f"  stdout: '{py_exec['stdout'].strip()}'")
    print(f"  exit_code: {py_exec['exit_code']}")
    assert py_exec["success"] is True, f"Python execution failed: {py_exec['stderr']}"
    assert "30" in py_exec["stdout"], f"Expected output '30', got '{py_exec['stdout']}'"
    print(">>> Test 1 PASSED!")

def test_python_to_javascript_vertical_slice():
    print("\n--- Test 2: Python -> JavaScript Vertical Slice ---")
    py_code = """def add_numbers(x, y):
    return x + y

def main():
    val = add_numbers(15, 25)
    print(val)

if __name__ == "__main__":
    main()"""

    pipeline = CompilerPipeline()
    result = pipeline.run_full_pipeline("python", "javascript", py_code, optimize=True)
    js_code = result["transpiled_code"]
    print("Generated JS Code:")
    print(js_code)
    assert "function add_numbers" in js_code
    assert "console.log" in js_code

    # Execute both in sandbox and compare
    sandbox = ExecutionSandbox()
    py_res = sandbox.execute("python", py_code)
    js_res = sandbox.execute("javascript", js_code)

    print(f"Python output: '{py_res['stdout'].strip()}'")
    print(f"JS output:     '{js_res['stdout'].strip()}'")

    comparator = OutputComparator()
    comp = comparator.compare(py_res["stdout"], js_res["stdout"])
    print(f"Comparison: {comp['status']} (Equivalence: {comp['is_equivalent']})")
    assert comp["is_equivalent"] is True, f"Outputs did not match: Py='{py_res['stdout']}' vs JS='{js_res['stdout']}'"
    print(">>> Test 2 PASSED!")

def test_javascript_to_python_vertical_slice():
    print("\n--- Test 3: JavaScript -> Python Vertical Slice ---")
    js_code = """function main() {
    let count = 1;
    let total = 0;
    while (count <= 5) {
        total += count;
        count += 1;
    }
    console.log(total);
}
main();"""

    pipeline = CompilerPipeline()
    result = pipeline.run_full_pipeline("javascript", "python", js_code, optimize=True)
    py_code = result["transpiled_code"]
    print("Generated Python Code:")
    print(py_code)
    assert "while" in py_code
    assert "print" in py_code

    sandbox = ExecutionSandbox()
    js_res = sandbox.execute("javascript", js_code)
    py_res = sandbox.execute("python", py_code)

    print(f"JS output:     '{js_res['stdout'].strip()}'")
    print(f"Python output: '{py_res['stdout'].strip()}'")

    comparator = OutputComparator()
    comp = comparator.compare(js_res["stdout"], py_res["stdout"])
    assert comp["is_equivalent"] is True, f"Outputs did not match: JS='{js_res['stdout']}' vs Py='{py_res['stdout']}'"
    print(">>> Test 3 PASSED!")

def test_optimizer_constant_folding():
    print("\n--- Test 4: Stage 5 Optimizer Constant Folding ---")
    code = """def main():
    x = 10 + 20
    y = x * 1
    print(x)"""

    ast_root, _ = parse_code("python", code)
    opt_ast, stats = optimize_program(ast_root)
    print(f"Optimizer Stats: {stats}")
    assert stats["constants_folded"] >= 1, "Failed to fold constant 10 + 20"
    print(">>> Test 4 PASSED!")

def test_compiler_stages_telemetry():
    print("\n--- Test 5: All 6 Stages Telemetry Verification ---")
    code = """int main() {
    int a = 5;
    int b = 10;
    printf("%d", a + b);
    return 0;
}"""
    pipeline = CompilerPipeline()
    report = pipeline.run_full_pipeline("c", "python", code, optimize=True)

    assert "lexical" in report["stages"]
    assert report["stages"]["lexical"]["token_count"] > 0
    assert "syntax" in report["stages"]
    assert report["stages"]["syntax"]["ast"] is not None
    assert "semantic" in report["stages"]
    assert len(report["stages"]["semantic"]["symbol_table"]) > 0
    assert "ir" in report["stages"]
    assert "FUNCTION main" in report["stages"]["ir"]["tac"]
    assert "optimized_ir" in report["stages"]
    assert "codegen" in report["stages"]
    assert report["stages"]["codegen"]["validation"]["valid"] is True
    print(">>> Test 5 PASSED!")

def test_minimal_c_to_python_clean_output():
    print("\n--- Test 6: Minimal Clean Idiomatic C -> Python Transpilation ---")
    code = """#include <stdio.h>
int main() {
    int a = 10;
    int b = 20;
    printf("%d", a + b);
    return 0;
}"""
    pipeline = CompilerPipeline()
    
    # 1. Unoptimized (optimize=False)
    res_unopt = pipeline.run_full_pipeline("c", "python", code, optimize=False)
    py_unopt = res_unopt["transpiled_code"]
    print("Unoptimized Python:")
    print(py_unopt)

    # Check absence of runtime stubs
    unwanted = [
        "import sys", "import math", "import time", "import threading",
        "_TemplateType", "vector = list", "map = dict", "mutex", "atomic",
        "lock_guard", "class _Std:", "std = _Std()", "_smart_int",
        "inspect", "try:", "except Exception:"
    ]
    for stub in unwanted:
        assert stub not in py_unopt, f"Found unexpected runtime stub in minimal output: {stub}"

    # Check essential concise structure
    assert "def main():" in py_unopt
    assert "a = 10" in py_unopt
    assert "b = 20" in py_unopt
    assert 'print(a + b, end="")' in py_unopt
    assert "return 0" in py_unopt
    assert 'if __name__ == "__main__":' in py_unopt
    assert "main()" in py_unopt

    # 2. Optimized (optimize=True)
    res_opt = pipeline.run_full_pipeline("c", "python", code, optimize=True)
    py_opt = res_opt["transpiled_code"]
    print("Optimized Python:")
    print(py_opt)
    for stub in unwanted:
        assert stub not in py_opt, f"Found unexpected runtime stub in minimal output: {stub}"
    assert 'print(30, end="")' in py_opt

    # 3. Sandbox execution verification
    sandbox = ExecutionSandbox()
    run_unopt = sandbox.execute("python", py_unopt)
    assert run_unopt["success"] is True
    assert run_unopt["stdout"] == "30", f"Expected exact stdout '30' without trailing newline, got {repr(run_unopt['stdout'])}"

    run_opt = sandbox.execute("python", py_opt)
    assert run_opt["success"] is True
    assert run_opt["stdout"] == "30", f"Expected exact stdout '30' without trailing newline, got {repr(run_opt['stdout'])}"

    print(">>> Test 6 PASSED!")

if __name__ == "__main__":
    print("RUNNING COMPILER DESIGN & AI TRANSPILER TEST SUITE...")
    test_prompt_c_to_python_demo()
    test_python_to_javascript_vertical_slice()
    test_javascript_to_python_vertical_slice()
    test_optimizer_constant_folding()
    test_compiler_stages_telemetry()
    test_minimal_c_to_python_clean_output()
    print("\n==========================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("==========================================")
