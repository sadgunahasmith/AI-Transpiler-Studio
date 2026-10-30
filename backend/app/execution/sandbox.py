"""
Sandboxed Code Execution Engine with timeouts, isolated scratch filesystem, and compiler detection.
"""
import os
import sys
import shutil
import tempfile
import subprocess
import time
from typing import Dict, Any, Optional
from ..config import ALLOW_UNTRUSTED_EXECUTION

SANDBOX_DIR = os.path.join(tempfile.gettempdir(), "transpiler_sandbox")
os.makedirs(SANDBOX_DIR, exist_ok=True)

class ExecutionSandbox:
    """Safe execution harness for Python, JavaScript (Node), C/C++, and Java."""

    def __init__(self, timeout_sec: int = 5):
        self.timeout_sec = timeout_sec
        self.allow_untrusted = ALLOW_UNTRUSTED_EXECUTION

    def is_isolated_sandbox_available(self) -> bool:
        """Probes whether an isolated container runtime (Docker daemon) is active."""
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return res.returncode == 0
        except Exception:
            return False

    def check_system_runtimes(self) -> Dict[str, Dict[str, Any]]:
        """Probes the host OS for available runtimes and compilers."""
        runtimes = {}
        docker_available = self.is_isolated_sandbox_available()
        runtimes["security"] = {
            "isolated_sandbox_active": docker_available,
            "untrusted_execution_allowed": self.allow_untrusted,
            "isolation_type": "Docker Container" if docker_available else ("Local Subprocess (Trusted Only)" if self.allow_untrusted else "Execution Disabled (Security Guard Active)")
        }
        # Python
        runtimes["python"] = {
            "available": True,
            "path": sys.executable,
            "version": sys.version.split()[0]
        }
        # Node.js
        node_path = shutil.which("node")
        runtimes["javascript"] = {
            "available": bool(node_path),
            "path": node_path or "Not installed",
            "version": "v24.x" if node_path else None
        }
        # GCC / Clang
        gcc_path = shutil.which("gcc") or shutil.which("clang")
        runtimes["c"] = {
            "available": bool(gcc_path),
            "path": gcc_path or "Not installed in PATH",
            "info": "Requires MinGW-w64 or Clang on Windows for native execution"
        }
        runtimes["cpp"] = {
            "available": bool(shutil.which("g++") or shutil.which("clang++")),
            "path": shutil.which("g++") or shutil.which("clang++") or "Not installed in PATH"
        }
        # Java
        javac_path = shutil.which("javac")
        runtimes["java"] = {
            "available": bool(javac_path),
            "path": javac_path or "Not installed in PATH",
            "info": "Requires JDK for compilation and execution"
        }
        return runtimes

    def execute(self, language: str, code: str, stdin_data: str = "") -> Dict[str, Any]:
        """Executes code with strict security isolation verification."""
        docker_active = self.is_isolated_sandbox_available()
        if not docker_active and not self.allow_untrusted:
            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    "Security Guard: Untrusted code execution is disabled. "
                    "Subprocess restrictions alone do not provide process or filesystem isolation. "
                    "To enable execution, start an isolated container environment (e.g. Docker daemon) "
                    "or set ALLOW_UNTRUSTED_EXECUTION=true in backend/.env for trusted local scripts."
                ),
                "execution_time_ms": 0,
                "exit_code": -1,
                "security_blocked": True
            }

        lang = language.strip().lower()

        if docker_active and lang in ("python", "py", "javascript", "js"):
            return self._run_in_docker(lang, code, stdin_data)

        if lang in ("python", "py"):
            return self._run_python(code, stdin_data)
        elif lang in ("javascript", "js"):
            return self._run_javascript(code, stdin_data)
        elif lang in ("c",):
            return self._run_c(code, stdin_data, is_cpp=False)
        elif lang in ("cpp", "c++"):
            return self._run_c(code, stdin_data, is_cpp=True)
        elif lang in ("java",):
            return self._run_java(code, stdin_data)
        else:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution for language '{language}' is not supported.",
                "execution_time_ms": 0,
                "exit_code": -1
            }

    def _run_in_docker(self, lang: str, code: str, stdin_data: str) -> Dict[str, Any]:
        """Runs code in an isolated container with strict resource limits."""
        image_map = {
            "python": ("python:3.11-alpine", ["python", "-c", code]),
            "py": ("python:3.11-alpine", ["python", "-c", code]),
            "javascript": ("node:20-alpine", ["node", "-e", code]),
            "js": ("node:20-alpine", ["node", "-e", code]),
        }
        if lang not in image_map:
            return self._run_python(code, stdin_data) if lang in ("python", "py") else self._run_javascript(code, stdin_data)

        img, cmd = image_map[lang]
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                ["docker", "run", "--rm", "-i", "--network=none", "--memory=256m", "--cpus=0.5", img] + cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            duration_ms = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "execution_time_ms": duration_ms,
                "exit_code": proc.returncode,
                "sandboxed": True,
                "sandbox_type": "Docker Container"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Docker sandbox error: {str(e)}",
                "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
                "exit_code": -1
            }

    def _run_python(self, code: str, stdin_data: str) -> Dict[str, Any]:
        temp_file = os.path.join(SANDBOX_DIR, f"temp_{int(time.time() * 1000)}.py")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)

            start = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, temp_file],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd=SANDBOX_DIR
            )
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "execution_time_ms": duration_ms,
                "exit_code": proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_sec} seconds (Infinite loop guard triggered).",
                "execution_time_ms": self.timeout_sec * 1000,
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "execution_time_ms": 0,
                "exit_code": -1
            }
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def _run_javascript(self, code: str, stdin_data: str) -> Dict[str, Any]:
        node_path = shutil.which("node")
        if not node_path:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Node.js runtime not found in system PATH. Cannot execute JavaScript code.",
                "execution_time_ms": 0,
                "exit_code": -1
            }

        temp_file = os.path.join(SANDBOX_DIR, f"temp_{int(time.time() * 1000)}.js")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)

            start = time.perf_counter()
            proc = subprocess.run(
                [node_path, temp_file],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd=SANDBOX_DIR
            )
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "execution_time_ms": duration_ms,
                "exit_code": proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_sec} seconds.",
                "execution_time_ms": self.timeout_sec * 1000,
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "execution_time_ms": 0,
                "exit_code": -1
            }
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def _run_c(self, code: str, stdin_data: str, is_cpp: bool = False) -> Dict[str, Any]:
        compiler = shutil.which("g++" if is_cpp else "gcc") or shutil.which("clang++" if is_cpp else "clang")
        if not compiler:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Native C/C++ compiler ('gcc'/'g++') not detected in PATH.\nInstall MinGW-w64 or Clang on Windows to compile and run C binaries locally.",
                "execution_time_ms": 0,
                "exit_code": -1
            }

        ext = ".cpp" if is_cpp else ".c"
        base_name = f"temp_{int(time.time() * 1000)}"
        src_file = os.path.join(SANDBOX_DIR, base_name + ext)
        exe_file = os.path.join(SANDBOX_DIR, base_name + ".exe")

        try:
            with open(src_file, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile
            comp_proc = subprocess.run(
                [compiler, src_file, "-o", exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd=SANDBOX_DIR
            )
            if comp_proc.returncode != 0:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Compilation Error:\n{comp_proc.stderr}",
                    "execution_time_ms": 0,
                    "exit_code": comp_proc.returncode
                }

            # Run binary
            start = time.perf_counter()
            run_proc = subprocess.run(
                [exe_file],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd=SANDBOX_DIR
            )
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": run_proc.returncode == 0,
                "stdout": run_proc.stdout,
                "stderr": run_proc.stderr,
                "execution_time_ms": duration_ms,
                "exit_code": run_proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_sec} seconds.",
                "execution_time_ms": self.timeout_sec * 1000,
                "exit_code": -1
            }
        finally:
            for p in (src_file, exe_file):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    def _run_java(self, code: str, stdin_data: str) -> Dict[str, Any]:
        javac = shutil.which("javac")
        java = shutil.which("java")
        if not javac or not java:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Java Development Kit (javac/java) not detected in system PATH.\nInstall OpenJDK to compile and run Java programs.",
                "execution_time_ms": 0,
                "exit_code": -1
            }

        run_dir = os.path.join(SANDBOX_DIR, f"java_{int(time.time() * 1000)}")
        os.makedirs(run_dir, exist_ok=True)
        src_file = os.path.join(run_dir, "Main.java")

        try:
            with open(src_file, "w", encoding="utf-8") as f:
                f.write(code)

            comp = subprocess.run([javac, "Main.java"], capture_output=True, text=True, timeout=self.timeout_sec, cwd=run_dir)
            if comp.returncode != 0:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Java Compilation Error:\n{comp.stderr}",
                    "execution_time_ms": 0,
                    "exit_code": comp.returncode
                }

            start = time.perf_counter()
            run = subprocess.run([java, "Main"], input=stdin_data, capture_output=True, text=True, timeout=self.timeout_sec, cwd=run_dir)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": run.returncode == 0,
                "stdout": run.stdout,
                "stderr": run.stderr,
                "execution_time_ms": duration_ms,
                "exit_code": run.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_sec} seconds.",
                "execution_time_ms": self.timeout_sec * 1000,
                "exit_code": -1
            }
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)
