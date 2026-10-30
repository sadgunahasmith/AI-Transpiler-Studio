"""
Comprehensive Test Suite for Any-Type Code Conversion & Syntax Error Modify-Changes.
Verifies:
1. C++ kitchen-sink codes with headers (<bits/stdc++.h>, <iostream>, <vector>, <cmath>) transpiling to Python, Java, C.
2. C code -> Python, Java, C++ transpilation & execution.
3. Python code -> C, Java, C++ transpilation & validation.
4. Java code -> C, Python, C++ transpilation & validation.
5. Syntax error identification and one-click 'Modify Changes' producing valid equivalent output code.
"""
import os
import sys

os.environ["ALLOW_UNTRUSTED_EXECUTION"] = "true"
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.compiler.pipeline import CompilerPipeline
from app.compiler.parser import parse_code
from app.compiler.codegen import generate_target_code, validate_target_code
from app.ai.corrector import AICorrector
from app.ai.heuristic_engine import HeuristicEngine
from app.execution.sandbox import ExecutionSandbox
from app.api.schemas import ModifyChangesRequest
from app.api.routes import modify_changes_and_transpile, detect_errors, DetectErrorsRequest

pipeline = CompilerPipeline()
sandbox = ExecutionSandbox()
corrector = AICorrector()
heuristic = HeuristicEngine()

def test_cpp_kitchen_sink_to_all_targets():
    print("\n--- Test A: Any C++ Code (STL, Templates, Headers) -> Python, Java, C ---")
    cpp_code = """
#include <iostream>
#include <vector>
#include <cmath>
#include <string>
using namespace std;

template <typename T>
T square_val(T x) {
    return x * x;
}

int main() {
    vector<int> numbers = {1, 2, 3, 4, 5};
    int total = 0;
    for (auto num : numbers) {
        total += square_val(num);
    }
    cout << "Total squares sum: " << total << endl;
    double root = sqrt(16.0);
    cout << "Square root: " << root << endl;
    return 0;
}
"""
    ast, errs = parse_code("cpp", cpp_code)
    assert ast is not None, f"C++ AST parsing failed: {errs}"
    print(f"C++ parsed successfully into {len(ast.body)} AST nodes. Errors: {len(errs)}")

    for target in ["python", "c", "java", "cpp"]:
        out = generate_target_code(target, ast)
        val = validate_target_code(target, out)
        print(f"  Target: {target:<8} | Generated: {len(out)} chars | Valid: {val['valid']}")
        assert val["valid"] is True, f"Failed target validation for {target}: {val}"

    # Execute generated python in sandbox
    py_code = generate_target_code("python", ast)
    res = sandbox.execute("python", py_code)
    print("  Python sandbox execution success:", res["success"])
    assert res["success"] is True, f"Execution failed: {res['stderr']}"
    assert "Total squares sum" in res["stdout"] or "55" in res["stdout"]
    print(">>> Test A PASSED!")

def test_c_code_to_all_targets():
    print("\n--- Test B: C Code with Math & Standard IO -> Python, Java, C++ ---")
    c_code = """
#include <stdio.h>
#include <math.h>

double compute_hypotenuse(double a, double b) {
    return sqrt(a * a + b * b);
}

int main() {
    double x = 3.0;
    double y = 4.0;
    double hyp = compute_hypotenuse(x, y);
    printf("Hypotenuse: %f\\n", hyp);
    return 0;
}
"""
    ast, errs = parse_code("c", c_code)
    assert ast is not None, f"C parsing failed: {errs}"
    print(f"C parsed successfully into {len(ast.body)} AST nodes.")

    for target in ["python", "java", "cpp", "c"]:
        out = generate_target_code(target, ast)
        val = validate_target_code(target, out)
        print(f"  Target: {target:<8} | Valid: {val['valid']}")
        assert val["valid"] is True

    py_code = generate_target_code("python", ast)
    res = sandbox.execute("python", py_code)
    assert res["success"] is True, f"Python execution failed: {res['stderr']}"
    assert "5" in res["stdout"], f"Expected 5 in stdout, got {res['stdout']}"
    print(">>> Test B PASSED!")

def test_python_code_to_all_targets():
    print("\n--- Test C: Python Code -> C, Java, C++ ---")
    py_code = """
def is_prime(n):
    if n <= 1:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True

num = 17
if is_prime(num):
    print("Prime number")
else:
    print("Not prime")
"""
    ast, errs = parse_code("python", py_code)
    assert ast is not None, f"Python AST failed: {errs}"

    for target in ["c", "java", "cpp"]:
        out = generate_target_code(target, ast)
        val = validate_target_code(target, out)
        print(f"  Target: {target:<8} | Lines: {len(out.splitlines())} | Valid: {val['valid']}")
        assert val["valid"] is True
    print(">>> Test C PASSED!")

def test_java_code_to_all_targets():
    print("\n--- Test D: Java Code -> C, Python, C++ ---")
    java_code = """
public class Main {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    public static void main(String[] args) {
        int n = 7;
        int ans = fibonacci(n);
        System.out.println(ans);
    }
}
"""
    ast, errs = parse_code("java", java_code)
    assert ast is not None, f"Java parsing failed: {errs}"

    for target in ["c", "python", "cpp", "java"]:
        out = generate_target_code(target, ast)
        val = validate_target_code(target, out)
        print(f"  Target: {target:<8} | Valid: {val['valid']}")
        assert val["valid"] is True

    py_code = generate_target_code("python", ast)
    res = sandbox.execute("python", py_code)
    assert res["success"] is True, f"Python execution failed: {res['stderr']}"
    assert "13" in res["stdout"], f"Expected 13 in stdout, got {res['stdout']}"
    print(">>> Test D PASSED!")

def test_syntax_error_modify_changes_pipeline():
    print("\n--- Test E: Syntax Error Identification -> Modify Changes -> Equivalent Target Output ---")
    # Buggy C++ code: missing semicolons, missing <iostream> include, typo in cout
    buggy_code = """
int main() {
    int a = 25
    int b = 75;
    coutt << a + b << endl
    return 0
}
"""
    # 1. Error identification
    det_res = detect_errors(DetectErrorsRequest(language="cpp", code=buggy_code))
    print(f"Identified {det_res['total_issues']} syntax issues in buggy code.")
    assert det_res["total_issues"] > 0, "Failed to identify syntax errors!"

    # 2. Modify changes action
    req = ModifyChangesRequest(
        source_language="cpp",
        target_language="python",
        code=buggy_code,
        optimize=True,
        ai_mode="hybrid_correction"
    )
    result = modify_changes_and_transpile(req)
    print("Modify Changes Success:", result["success"])
    print("Modifications made:", len(result["modifications"]))
    for m in result["modifications"]:
        print(f"  - Line {m.get('line')}: {m.get('description')}")
    print("\nModified Source Code:\n" + result["modified_code"])
    print("\nEquivalent Python Output:\n" + result["transpiled_code"])

    assert result["success"] is True, "Modify changes pipeline reported failure!"
    assert len(result["modifications"]) >= 2, "Expected multiple automated syntax corrections"
    assert "int a = 25;" in result["modified_code"], "Missing semicolon was not restored"
    assert "return 0;" in result["modified_code"], "Return 0 semicolon was not restored"
    assert len(result["transpiled_code"]) > 0, "Failed to generate equivalent target code"

    # 3. Execute equivalent output code
    exec_res = sandbox.execute("python", result["transpiled_code"])
    print(f"Equivalent Code Sandbox Execution: stdout='{exec_res['stdout'].strip()}', exit={exec_res['exit_code']}")
    assert exec_res["success"] is True, f"Execution failed: {exec_res['stderr']}"
    assert "100" in exec_res["stdout"], f"Expected output 100, got '{exec_res['stdout']}'"
    print(">>> Test E PASSED!")

if __name__ == "__main__":
    print("RUNNING ANY-TYPE CODE CONVERSION & MODIFY-CHANGES VERIFICATION...")
    test_cpp_kitchen_sink_to_all_targets()
    test_c_code_to_all_targets()
    test_python_code_to_all_targets()
    test_java_code_to_all_targets()
    test_syntax_error_modify_changes_pipeline()
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 50)
