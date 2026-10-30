"""Regression tests for idiomatic C/C++ -> Python print generation (no runtime _fmt unless needed)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.compiler.pipeline import CompilerPipeline
from app.execution.sandbox import ExecutionSandbox


def _to_py(code: str, lang: str = "cpp") -> str:
    return CompilerPipeline().run_full_pipeline(lang, "python", code)["transpiled_code"]


def _run(py: str) -> str:
    res = ExecutionSandbox().execute("python", py)
    assert res["success"] is True, res["stderr"]
    return res["stdout"]


FIB = """#include <iostream>
using namespace std;
int main() {
    int n = 8, t1 = 0, t2 = 1, nextTerm;
    int i = 1;
    while (i <= n) { cout << t1 << " "; nextTerm = t1 + t2; t1 = t2; t2 = nextTerm; i = i + 1; }
    return 0;
}"""


def test_fibonacci_is_idiomatic():
    py = _to_py(FIB)
    assert "_fmt" not in py                      # statically-typed ints need no helper
    assert 'print(t1, end=" ")' in py            # trailing literal folded into end=
    assert "i += 1" in py                        # x = x + 1 -> x += 1
    assert "nextTerm = 0" in py                  # not "= None"
    assert "# using namespace" not in py         # no empty/noisy comment
    assert 'if __name__ == "__main__":' in py
    assert _run(py) == "0 1 1 2 3 5 8 13 "


def test_float_bool_and_mixed_output_matches_cpp():
    code = """#include <iostream>
using namespace std;
int main() {
    int a = 7, b = 2; double d = 3.0, e = 2.5; bool f = true;
    cout << "sum=" << a + b << endl;
    cout << "d=" << d << " e=" << e << endl;
    cout << f << (a < b) << endl;
    cout << "braces {} 'q'" << endl;
    return 0;
}"""
    py = _to_py(code)
    assert "_fmt" not in py
    assert _run(py) == "sum=9\nd=3 e=2.5\n10\nbraces {} 'q'\n"


def test_escape_sequences_are_decoded():
    code = """#include <iostream>
using namespace std;
int main() { int a = 5; cout << "Hello\\n"; cout << "V:\\t" << a << "\\n"; return 0; }"""
    assert _run(_to_py(code)) == "Hello\nV:\t5\n"


def test_int_holding_division_result_still_prints_like_cpp():
    # '/' is emitted as true division, so these ints are floats at runtime: must NOT print "5.0"
    code = """#include <iostream>
using namespace std;
int main() { int a = 10, b = 2; int c = a / b; cout << c << endl; int area = (a * b) / 2; cout << area << endl; return 0; }"""
    py = _to_py(code)
    assert "_fmt" in py                           # safe fallback kept where type is not provable
    assert _run(py) == "5\n10\n"


def test_c_printf_program():
    code = """#include <stdio.h>
int main() { int n = 3, i; for (i = 0; i < n; i++) printf("%d ", i); printf("\\nok %d\\n", n * 2); return 0; }"""
    assert _run(_to_py(code, "c")) == "0 1 2 \nok 6\n"
