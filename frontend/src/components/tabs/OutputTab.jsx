import React from 'react';
import { Terminal, CheckCircle2, XCircle, AlertTriangle, Clock, ArrowRight } from 'lucide-react';

export default function OutputTab({ executionResult, comparisonResult, stdin, setStdin }) {
  const hasExec = Boolean(executionResult || comparisonResult);

  return (
    <div className="p-4 space-y-4 text-xs">
      {/* Optional Stdin Controls */}
      <div className="flex items-center space-x-2 bg-[#161b22] p-2.5 rounded-lg border border-[#30363d]">
        <Terminal className="w-3.5 h-3.5 text-[#8b949e]" />
        <span className="text-[#8b949e] font-medium">Standard Input (stdin):</span>
        <input
          type="text"
          placeholder="Provide inputs for scanf / input() / readline..."
          value={stdin}
          onChange={(e) => setStdin(e.target.value)}
          className="flex-1 bg-[#21262d] border border-[#30363d] rounded px-2.5 py-1 text-xs text-[#c9d1d9] font-mono focus:outline-none focus:border-blue-500"
        />
      </div>

      {!hasExec ? (
        <div className="p-8 text-center text-[#8b949e]">
          <Terminal className="w-10 h-10 mx-auto mb-2 text-emerald-400 opacity-60" />
          <p className="text-sm">Click "Run Code" or "Compare Outputs" to execute in the secure sandbox.</p>
        </div>
      ) : (
        <>
          {/* Equivalence Summary Badge if Comparison was run */}
          {comparisonResult && (
            <div className={`p-3 rounded-lg border flex items-center justify-between ${
              comparisonResult.comparison?.is_equivalent
                ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-200'
                : 'bg-red-950/20 border-red-800/40 text-red-200'
            }`}>
              <div className="flex items-center space-x-2.5">
                {comparisonResult.comparison?.is_equivalent ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
                <div>
                  <span className="font-bold text-sm block">
                    Equivalence Status: {comparisonResult.comparison?.status}
                  </span>
                  <span className="text-[11px] text-[#8b949e]">
                    Output Similarity: {comparisonResult.comparison?.similarity_percentage == null ? 'N/A (execution failed)' : `${comparisonResult.comparison.similarity_percentage}%`}
                  </span>
                </div>
              </div>

              <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                comparisonResult.comparison?.is_equivalent
                  ? 'bg-emerald-900/60 text-emerald-300 border-emerald-700'
                  : 'bg-red-900/60 text-red-300 border-red-700'
              }`}>
                {comparisonResult.comparison?.is_equivalent ? 'PASSED (100% MATCH)' : 'MISMATCH DETECTED'}
              </span>
            </div>
          )}

          {/* Side by side outputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Source Output */}
            <div className="rounded-lg border border-[#30363d] bg-[#161b22] overflow-hidden">
              <div className="px-3 py-1.5 bg-[#21262d] border-b border-[#30363d] flex items-center justify-between text-[11px]">
                <span className="font-semibold text-blue-400">Source Program Output</span>
                {comparisonResult?.source_execution && (
                  <div className="flex items-center space-x-2 text-[#8b949e]">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{comparisonResult.source_execution.execution_time_ms} ms</span>
                    </span>
                    <span>exit: {comparisonResult.source_execution.exit_code}</span>
                  </div>
                )}
              </div>
              <pre className="p-3 bg-[#0d1117] font-mono text-xs text-[#c9d1d9] overflow-x-auto min-h-[100px] max-h-[200px]">
                {comparisonResult?.source_execution?.stdout || executionResult?.stdout || "// (No output or program did not execute)"}
                {comparisonResult?.source_execution?.stderr && (
                  <span className="text-red-400 block mt-1">{comparisonResult.source_execution.stderr}</span>
                )}
              </pre>
            </div>

            {/* Target Output */}
            <div className="rounded-lg border border-[#30363d] bg-[#161b22] overflow-hidden">
              <div className="px-3 py-1.5 bg-[#21262d] border-b border-[#30363d] flex items-center justify-between text-[11px]">
                <span className="font-semibold text-emerald-400">Target Transpiled Output</span>
                {comparisonResult?.target_execution && (
                  <div className="flex items-center space-x-2 text-[#8b949e]">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{comparisonResult.target_execution.execution_time_ms} ms</span>
                    </span>
                    <span>exit: {comparisonResult.target_execution.exit_code}</span>
                  </div>
                )}
              </div>
              <pre className="p-3 bg-[#0d1117] font-mono text-xs text-[#c9d1d9] overflow-x-auto min-h-[100px] max-h-[200px]">
                {comparisonResult?.target_execution?.stdout || "// (No target output)"}
                {comparisonResult?.target_execution?.stderr && (
                  <span className="text-red-400 block mt-1">{comparisonResult.target_execution.stderr}</span>
                )}
              </pre>
            </div>
          </div>

          {/* Diff Output */}
          {comparisonResult?.comparison?.diff && !comparisonResult.comparison?.is_equivalent && (
            <div className="rounded-lg border border-[#30363d] bg-[#161b22] p-3 space-y-1">
              <span className="font-semibold text-[#c9d1d9] block">Execution Difference (Unified Diff)</span>
              <pre className="p-2 bg-[#0d1117] font-mono text-[11px] text-amber-300 rounded overflow-x-auto">
                {comparisonResult.comparison.diff}
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}
