import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Wand2, Info } from 'lucide-react';

export default function ErrorsTab({ errors, warnings, onApplyFix, isFixing }) {
  const allItems = [...(errors || []), ...(warnings || [])];

  if (!allItems || allItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center text-[#8b949e]">
        <CheckCircle className="w-10 h-10 text-emerald-500 mb-2" />
        <h3 className="text-sm font-semibold text-[#c9d1d9]">No Errors or Warnings Detected</h3>
        <p className="text-xs max-w-sm mt-1">
          Source code parsed cleanly across Lexical, Syntax, and Semantic analysis stages.
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-[#c9d1d9]">
            Detected Issues ({allItems.length})
          </span>
          <span className="text-xs text-[#8b949e]">
            ({errors?.length || 0} errors, {warnings?.length || 0} warnings/suspicions)
          </span>
        </div>

        <button
          onClick={onApplyFix}
          disabled={isFixing}
          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition-colors shadow-sm disabled:opacity-50"
        >
          <Wand2 className="w-3.5 h-3.5" />
          <span>{isFixing ? "Applying Fixes..." : "Apply Auto-Correction"}</span>
        </button>
      </div>

      <div className="space-y-2">
        {allItems.map((item, idx) => {
          const isError = item.severity === 'error';
          const isAI = item.source === 'ai';

          return (
            <div
              key={idx}
              className={`p-3 rounded-lg border text-xs flex flex-col md:flex-row md:items-center justify-between gap-2 ${
                isError
                  ? 'bg-red-950/20 border-red-800/40 text-red-200'
                  : isAI
                  ? 'bg-purple-950/20 border-purple-800/40 text-purple-200'
                  : 'bg-amber-950/20 border-amber-800/40 text-amber-200'
              }`}
            >
              <div className="flex items-start space-x-2.5">
                {isError ? (
                  <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                ) : isAI ? (
                  <Info className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                )}

                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-[#c9d1d9]">
                      Line {item.line || 1}{item.column ? `:${item.column}` : ''}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                        isError
                          ? 'bg-red-900/60 text-red-300'
                          : isAI
                          ? 'bg-purple-900/60 text-purple-300'
                          : 'bg-amber-900/60 text-amber-300'
                      }`}
                    >
                      {item.category || (isAI ? "AI Suspicion" : "Compiler Error")}
                    </span>
                    <span className="text-[10px] text-[#8b949e]">
                      Source: {item.source === 'ai' ? 'AI Diagnostic' : 'Traditional Compiler'}
                    </span>
                  </div>

                  <p className="mt-1 text-[#c9d1d9] font-mono text-xs">
                    {item.message}
                  </p>

                  {item.suggested_fix && (
                    <div className="mt-1.5 flex items-center space-x-1.5 text-emerald-400 font-mono text-[11px] bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-900/50">
                      <span>Suggested Fix:</span>
                      <span className="font-semibold">{item.suggested_fix}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
