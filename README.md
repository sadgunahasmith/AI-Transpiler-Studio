# AI-Powered Multi-Language Transpiler & Compiler IDE

A full-stack, academic-grade application combining **Compiler Design** and **Artificial Intelligence**. The application allows users to write or paste code in **C, C++, Python, Java, or JavaScript**, inspect all 6 traditional compilation stages, detect and auto-correct errors using an intelligent hybrid AI pipeline, and transpile & verify the code in an isolated execution sandbox.

---

## 1. Academic Context & Core Innovations

This project was built to demonstrate both traditional compiler engineering principles and artificial intelligence repair techniques working in harmony:

1. **Independent Compiler Pipeline**: The compiler pipeline does **not** rely on an LLM for translation. It implements concrete Lexical, Syntax, Semantic, Intermediate Representation (Three-Address Code), Optimization, and Target Code Generation stages.
2. **Pedagogical AI Integration**: AI is leveraged for error diagnosis, intent-preserving repair, pedagogical explanations, and translation rationale.
3. **Dual AI Architecture**:
   - **Cloud LLM Support**: Integrates with Google Gemini and OpenAI when an API key is provided.
   - **Offline Heuristic Expert System**: Functions 100% reliably without requiring any API key or Internet connection.
4. **Behavioral Equivalence Verification**: Runtimes execute both programs in isolated sandboxes with identical inputs, comparing stdout character-by-character and displaying visual diffs.

---

## 2. Compiler Pipeline Implementation (Stages 1–6)

### Stage 1: Lexical Analysis
- **Tokenizers**: Dedicated lexers for C, C++, Python, JavaScript, and Java (`c_lexer.py`, `py_lexer.py`, `js_lexer.py`, `java_lexer.py`).
- **Token Classes**: `KEYWORD`, `IDENTIFIER`, `NUMBER`, `STRING`, `BOOLEAN`, `OPERATOR`, `DELIMITER`, `PREPROCESSOR`, `COMMENT`.
- **Lexical Errors**: Detects unclosed string literals, unclosed comments, and illegal characters.
- **Visual Token Table**: Displays token index, type badge, lexeme value, line, and column.

### Stage 2: Syntax Analysis
- **AST Construction**: Builds a normalized, language-neutral `ProgramNode` AST (`ast_nodes.py`).
- **Language Parsers**:
  - `PythonParser`: Uses Python's native `ast` engine with line/offset error diagnostics.
  - `CParser`: Multi-level parser detecting missing semicolons, unmatched braces `{}`, unclosed parens `()`.
  - `JSParser`: Parses ES6 constructs, functions, loops, and delimiters.
  - `JavaParser`: Parses classes, static methods, loops, and statement blocks.
- **Syntax Error Detection**: Precise reporting of missing semicolons (e.g. `int a = 10` and `printf(...)`), unmatched brackets, and missing colons.

### Stage 3: Semantic Analysis
- **Scoped Symbol Table**: Tracks scope levels (0 = global, 1 = function, $\ge 2$ = block), identifier name, type, declaration line, initialization status, and reference count.
- **Diagnostics**:
  - Undeclared variables in typed languages.
  - Variable redeclaration in identical scopes.
  - Unused variable warnings.
  - Return statements outside function bodies.

### Stage 4: Intermediate Representation (IR)
- **Universal IR & Three-Address Code (TAC)**:
  - Generates linear Quadruples / Three-Address Code with explicit temporaries (`t0`, `t1`, `t2`...) and labels (`L_loop_start`, `L_endif`).
  - Decouples source-language syntax from target-language code emission.

### Stage 5: Optimization
- **Optimization Passes**:
  - **Constant Folding**: Computes constant binary operations at compile time (e.g. `10 + 20` $\to$ `30`).
  - **Constant Propagation**: Propagates constant bindings into downstream operations while safely invalidating variables mutated across loops.
  - **Dead Code Elimination**: Prunes statements after unconditional returns or within unreachable branches.
  - **Algebraic Simplification**: Simplifies identity expressions (`x * 1` $\to$ `x`, `x + 0` $\to$ `x`).
- **Telemetry**: Displays folded instructions count, dead code removed, and optimization logs.

### Stage 6: Code Generation
- **Target Generators**:
  - `PythonCodeGen`: Generates Python 3 code with 4-space indentation and `if __name__ == '__main__':` execution guards.
  - `JSCodeGen`: Generates modern JavaScript with `let`/`const`, `console.log()`, and entry calls.
  - `CCodeGen`: Generates C with `#include <stdio.h>`, types, `printf()`, and `int main()`.
  - `CPPCodeGen`: Generates C++ with `<iostream>`, `cout << ... << endl`.
  - `JavaCodeGen`: Generates `public class Main { public static void main(...) { ... } }`.
- **Target Validation**: Validates generated code using target parsers and structural balance verification.

---

## 3. Project Directory Structure

```
ai_transpiler_studio/
├── backend/
│   ├── app/
│   │   ├── compiler/
│   │   │   ├── lexer/             # Stage 1: C, CPP, Python, JS, Java Lexers
│   │   │   ├── parser/            # Stage 2: AST Nodes and Parsers
│   │   │   ├── semantic/          # Stage 3: Scoped Symbol Table & Analyzer
│   │   │   ├── ir/                # Stage 4: Three-Address Code & IR Builder
│   │   │   ├── optimizer/         # Stage 5: Constant folding & DCE
│   │   │   ├── codegen/           # Stage 6: Python, JS, C, CPP, Java Generators
│   │   │   └── pipeline.py        # Master Compiler Coordinator
│   │   ├── ai/                    # Stage 7: Gemini/OpenAI & Heuristic Engine
│   │   ├── execution/             # Safe Execution Sandbox & Comparator
│   │   ├── database/              # SQLite Database History
│   │   ├── samples/               # Code Sample Library
│   │   ├── api/                   # FastAPI Routes and Schemas
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_compiler.py       # Automated unit tests
│   ├── requirements.txt
│   └── run_backend.bat
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx         # Status badges & runtimes
│   │   │   ├── ActionToolbar.jsx  # Action buttons & optimization switch
│   │   │   ├── EditorPanel.jsx    # Dual Monaco Editors (Source + Target)
│   │   │   └── tabs/
│   │   │       ├── ErrorsTab.jsx          # Error diagnostics & 1-click fixes
│   │   │       ├── CompilerStagesTab.jsx  # Tokens, AST, Symbol Table, TAC, Opt
│   │   │       ├── AIExplanationTab.jsx   # Pedagogical rationale
│   │   │       ├── OutputTab.jsx          # Live execution & output diffs
│   │   │       ├── CodeComparisonTab.jsx  # Monaco Diff Editor
│   │   │       ├── HistoryTab.jsx         # SQLite history viewer
│   │   │       └── MatrixTab.jsx          # Supported feature matrix
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── run_frontend.bat
├── run_all.bat                    # One-click Windows Launcher
└── README.md
```

---

## 4. Setup and Installation Instructions (Windows)

### Prerequisites
- **Python 3.10+** (Python 3.13 tested)
- **Node.js v18+** (Node.js v24 tested)

### 1. Install Backend Dependencies
Open PowerShell or Command Prompt:
```powershell
cd C:\Users\koush\.gemini\antigravity\scratch\ai_transpiler_studio\backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```powershell
cd C:\Users\koush\.gemini\antigravity\scratch\ai_transpiler_studio\frontend
npm install
```

---

## 5. How to Run the Application on Windows

### Option A: One-Click Launcher (Recommended)
Double-click `run_all.bat` in the project root:
```powershell
C:\Users\koush\.gemini\antigravity\scratch\ai_transpiler_studio\run_all.bat
```
This automatically starts both the FastAPI backend server (`http://127.0.0.1:8000`) and the Vite React frontend (`http://localhost:5173`) in dedicated console windows.

### Option B: Manual Execution

**Start Backend:**
```powershell
cd C:\Users\koush\.gemini\antigravity\scratch\ai_transpiler_studio\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Start Frontend:**
```powershell
cd C:\Users\koush\.gemini\antigravity\scratch\ai_transpiler_studio\frontend
npm run dev
```

Then navigate to **`http://localhost:5173`** in your browser.

---

## 6. Configuring an AI API Key (Optional)

The application includes an internal **Heuristic Expert Engine** that performs syntax repair, missing semicolon restoration, delimiter balancing, and pedagogical diagnosis **100% offline without any API key**.

If you wish to use Google Gemini or OpenAI:
1. In PowerShell before running:
   ```powershell
   $env:GEMINI_API_KEY="your-gemini-api-key-here"
   # OR
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   ```
2. Or set it permanently in Windows System Environment Variables.
The application will automatically detect the key on startup and display the active provider badge in the header.

---

## 7. Running Automated Verification Tests

The test suite verifies:
1. C Semicolon Error Detection, Auto-Correction, Transpilation to Python, and Execution printing `30`.
2. Python $\leftrightarrow$ JavaScript Vertical Slice with Sandbox Execution Equivalence.
3. Stage 5 Constant Folding, Constant Propagation, and Loop Invalidation.
4. Stages 1–6 Telemetry and Validation.

Run the test suite with:
```powershell
cd C:\Users\koush\.gemini\antigravity\scratch\ai_transpiler_studio
python backend/tests/test_compiler.py
```
Expected output:
```text
ALL TESTS PASSED WITH 100% SUCCESS!
```
