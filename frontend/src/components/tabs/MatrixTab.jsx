import React from 'react';
import { Layers, Check, Minus, Info } from 'lucide-react';

export default function MatrixTab() {
  const features = [
    { feature: "Variable Declarations", c: "✓ Explicit (int, float)", cpp: "✓ Explicit (int, auto)", py: "✓ Dynamic binding", js: "✓ let, const, var", java: "✓ Static typing" },
    { feature: "Arithmetic & Logic (+, -, *, /, %, &&, ||, !)", c: "✓ Full", cpp: "✓ Full", py: "✓ Full", js: "✓ Full", java: "✓ Full" },
    { feature: "Conditionals (if, else if, else)", c: "✓ Full", cpp: "✓ Full", py: "✓ if, elif, else", js: "✓ Full", java: "✓ Full" },
    { feature: "While Loops", c: "✓ Full", cpp: "✓ Full", py: "✓ Full", js: "✓ Full", java: "✓ Full" },
    { feature: "For Loops & Ranges", c: "✓ 3-part for", cpp: "✓ 3-part for", py: "✓ range() based", js: "✓ 3-part for", java: "✓ 3-part for" },
    { feature: "Functions & Parameters", c: "✓ Typed params", cpp: "✓ Typed params", py: "✓ def name()", js: "✓ function", java: "✓ Static methods" },
    { feature: "Standard I/O Operations", c: "✓ printf()", cpp: "✓ cout << endl", py: "✓ print()", js: "✓ console.log()", java: "✓ System.out.println" },
    { feature: "Stage 1: Lexical Token Table", c: "✓ Supported", cpp: "✓ Supported", py: "✓ Supported", js: "✓ Supported", java: "✓ Supported" },
    { feature: "Stage 2: Syntax AST Generation", c: "✓ Supported", cpp: "✓ Supported", py: "✓ Supported", js: "✓ Supported", java: "✓ Supported" },
    { feature: "Stage 3: Symbol Table & Scopes", c: "✓ Scoped levels", cpp: "✓ Scoped levels", py: "✓ Scoped levels", js: "✓ Scoped levels", java: "✓ Scoped levels" },
    { feature: "Stage 4: Three-Address Code (TAC)", c: "✓ Supported", cpp: "✓ Supported", py: "✓ Supported", js: "✓ Supported", java: "✓ Supported" },
    { feature: "Stage 5: Constant Folding & DCE", c: "✓ Opt passes", cpp: "✓ Opt passes", py: "✓ Opt passes", js: "✓ Opt passes", java: "✓ Opt passes" },
    { feature: "Stage 6: Target Code Generation", c: "✓ Idiomatic", cpp: "✓ Idiomatic", py: "✓ Idiomatic", js: "✓ Idiomatic", java: "✓ Idiomatic" },
    { feature: "Live Sandbox Execution", c: "⚠️ Requires GCC", cpp: "⚠️ Requires G++", py: "✓ Live Python 3.13", js: "✓ Live Node.js v24", java: "⚠️ Requires JDK" },
  ];

  return (
    <div className="p-4 space-y-4 text-xs">
      <div className="flex items-center space-x-2">
        <Layers className="w-4 h-4 text-indigo-400" />
        <span className="font-semibold text-sm text-[#c9d1d9]">
          Academic Language Subset & Supported Feature Matrix
        </span>
      </div>

      <p className="text-[#8b949e] leading-relaxed">
        In accordance with academic compiler design criteria, this system defines explicit transformation semantics for core computational constructs across all five languages. Complex idiomatic language extensions not yet lowered to IR are safely identified during analysis.
      </p>

      <div className="overflow-x-auto rounded-lg border border-[#30363d] bg-[#161b22]">
        <table className="w-full text-left font-mono text-[11px]">
          <thead className="bg-[#21262d] text-[#8b949e] uppercase border-b border-[#30363d]">
            <tr>
              <th className="p-2.5">Construct / Compiler Stage</th>
              <th className="p-2.5 text-blue-400">C</th>
              <th className="p-2.5 text-indigo-400">C++</th>
              <th className="p-2.5 text-amber-400">Python</th>
              <th className="p-2.5 text-yellow-300">JavaScript</th>
              <th className="p-2.5 text-red-400">Java</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#30363d]">
            {features.map((f, i) => (
              <tr key={i} className="hover:bg-[#1f242c] transition-colors">
                <td className="p-2.5 font-bold text-[#c9d1d9] font-sans">{f.feature}</td>
                <td className="p-2.5 text-[#c9d1d9]">{f.c}</td>
                <td className="p-2.5 text-[#c9d1d9]">{f.cpp}</td>
                <td className="p-2.5 text-[#c9d1d9]">{f.py}</td>
                <td className="p-2.5 text-[#c9d1d9]">{f.js}</td>
                <td className="p-2.5 text-[#c9d1d9]">{f.java}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
