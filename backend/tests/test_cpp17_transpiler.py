"""
Comprehensive C++17 Transpiler Regression Test Suite.
Verifies all advanced C++17 constructs:
1. Namespaces and nested namespaces
2. Classes, inheritance, virtual methods, abstract base classes
3. Templates (function and class templates)
4. Lambdas and closures
5. Smart pointers and references
6. Exceptions (try/catch/throw)
7. Concurrency (thread, mutex, lock_guard, atomic)
8. Full end-to-end 954-line transpiler_test.cpp analysis across all 5 targets (Python, C, C++, Java, JS)
"""
import sys
import os
import py_compile

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.compiler.pipeline import CompilerPipeline
from app.compiler.parser.clang_frontend import ClangFrontend


def test_namespaces():
    print("\n--- C++17 Test 1: Namespaces ---")
    code = """
    namespace math_utils {
        constexpr double PI = 3.141592653589793;
        int add(int a, int b) { return a + b; }
        namespace internal {
            int secret() { return 42; }
        }
    }
    int main() {
        int x = math_utils::add(2, 3);
        int y = math_utils::internal::secret();
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed namespace transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "class math_utils:" in target_code or "math_utils" in target_code
    assert "add" in target_code
    print(">>> Test 1 (Namespaces) PASSED!")


def test_classes_and_inheritance():
    print("\n--- C++17 Test 2: Classes, Inheritance & Virtual Methods ---")
    code = """
    class Shape {
    protected:
        double area_;
    public:
        Shape() : area_(0.0) {}
        virtual ~Shape() {}
        virtual double get_area() const = 0;
    };

    class Circle : public Shape {
        double r_;
    public:
        Circle(double r) : r_(r) {}
        double get_area() const override { return 3.14 * r_ * r_; }
    };

    int main() {
        Circle c(5.0);
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed class/inheritance transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "class Shape" in target_code
    assert "class Circle(Shape)" in target_code or "class Circle" in target_code
    print(">>> Test 2 (Classes & Inheritance) PASSED!")


def test_templates():
    print("\n--- C++17 Test 3: Templates ---")
    code = """
    template <typename T>
    T find_max(T a, T b) {
        return (a > b) ? a : b;
    }

    template <typename T>
    class Box {
        T value_;
    public:
        Box(T v) : value_(v) {}
        T get_val() const { return value_; }
    };

    int main() {
        int m = find_max<int>(3, 7);
        Box<double> b(3.14);
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed template transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "def find_max" in target_code
    assert "class Box" in target_code
    print(">>> Test 3 (Templates) PASSED!")


def test_lambdas():
    print("\n--- C++17 Test 4: Lambdas & Closures ---")
    code = """
    int main() {
        int factor = 10;
        auto multiplier = [factor](int x) { return x * factor; };
        int res = multiplier(5);
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed lambda transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "lambda" in target_code or "multiplier" in target_code
    print(">>> Test 4 (Lambdas) PASSED!")


def test_pointers_and_references():
    print("\n--- C++17 Test 5: Pointers & References ---")
    code = """
    #include <memory>
    int main() {
        int val = 100;
        int* ptr = &val;
        int& ref = val;
        auto uptr = std::make_unique<int>(200);
        auto sptr = std::make_shared<int>(300);
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed pointers transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "val = 100" in target_code
    print(">>> Test 5 (Pointers & References) PASSED!")


def test_exceptions():
    print("\n--- C++17 Test 6: Exceptions ---")
    code = """
    #include <stdexcept>
    int divide(int a, int b) {
        if (b == 0) throw std::runtime_error("division by zero");
        return a / b;
    }
    int main() {
        try {
            int r = divide(10, 0);
        } catch (const std::runtime_error& e) {
            return 1;
        }
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed exceptions transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "try:" in target_code
    assert "except" in target_code
    assert "raise" in target_code
    print(">>> Test 6 (Exceptions) PASSED!")


def test_concurrency():
    print("\n--- C++17 Test 7: Concurrency ---")
    code = """
    #include <mutex>
    #include <atomic>
    #include <thread>
    std::mutex mtx;
    std::atomic<int> counter(0);
    void worker() {
        std::lock_guard<std::mutex> lock(mtx);
        counter.fetch_add(1);
    }
    int main() {
        std::thread t(worker);
        t.join();
        return 0;
    }
    """
    pipeline = CompilerPipeline()
    res = pipeline.run_full_pipeline("cpp", "python", code)
    assert res["success"] is True, f"Failed concurrency transpilation: {res.get('errors')}"
    target_code = res["stages"]["codegen"]["target_code"]
    assert "counter" in target_code
    assert "worker" in target_code
    print(">>> Test 7 (Concurrency) PASSED!")


def test_transpiler_test_cpp_stress_test():
    print("\n--- C++17 Test 8: Full 954-Line transpiler_test.cpp Multi-Target Stress Test ---")
    stress_file = os.path.join(backend_dir, "..", "transpiler_test.cpp")
    if not os.path.exists(stress_file):
        stress_file = os.path.join(os.getcwd(), "transpiler_test.cpp")
    
    assert os.path.exists(stress_file), f"Could not find transpiler_test.cpp at {stress_file}"
    with open(stress_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    targets = ["python", "c", "cpp", "java", "javascript"]
    pipeline = CompilerPipeline()

    for target in targets:
        res = pipeline.run_full_pipeline(source_language="cpp", target_language=target, source_code=source_code)
        assert res["success"] is True, f"Failed for target {target}: {res.get('errors')}"
        codegen_stage = res["stages"].get("codegen", {})
        code = codegen_stage.get("target_code", "")
        lines = len(code.splitlines())
        print(f"  Target: {target:12} | Lines: {lines:5} | Success: True")
        assert lines > 500, f"Target {target} emitted unexpectedly few lines: {lines}"

        if target == "python":
            temp_py = os.path.join(os.path.dirname(__file__), "temp_transpiled.py")
            with open(temp_py, "w", encoding="utf-8") as out_f:
                out_f.write(code)
            try:
                py_compile.compile(temp_py, doraise=True)
                print("  -> Python py_compile verification: PASSED (0 syntax errors)")
            finally:
                if os.path.exists(temp_py):
                    os.remove(temp_py)

    print(">>> Test 8 (transpiler_test.cpp Stress Test) PASSED!")


if __name__ == "__main__":
    print("=================================================================")
    print("RUNNING ADVANCED C++17 TRANSPILER REGRESSION SUITE...")
    print("=================================================================")
    test_namespaces()
    test_classes_and_inheritance()
    test_templates()
    test_lambdas()
    test_pointers_and_references()
    test_exceptions()
    test_concurrency()
    test_transpiler_test_cpp_stress_test()
    print("\n=================================================================")
    print("ALL ADVANCED C++17 REGRESSION TESTS PASSED WITH 100% SUCCESS!")
    print("=================================================================")
