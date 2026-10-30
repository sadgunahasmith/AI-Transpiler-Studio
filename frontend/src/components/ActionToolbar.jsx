import React from 'react';
import { 
  Search, AlertTriangle, Wand2, RefreshCw, Play, 
  Scale, Sliders, RotateCcw, FileCode, Check, Download, XCircle, Sparkles 
} from 'lucide-react';

export default function ActionToolbar({
  onAnalyze,
  onDetectErrors,
  onAutoCorrect,
  onTranspile,
  onRunCode,
  onCompare,
  onReset,
  optimize,
  setOptimize,
  aiMode,
  setAiMode,
  onDownloadTarget,
  onCancel,
  samples,
  onSelectSample,
  isLoading,
  errorCount
}) {
  return (
    <div className="bg-[#161b22] border-b border-[#30363d] px-4 py-2 flex flex-wrap items-center justify-between gap-2">
      {/* Primary Actions */}
      <div className="flex items-center flex-wrap gap-2">
        <button
          onClick={onAnalyze}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] border border-[#30363d] transition-colors disabled:opacity-50"
          title="Run Stage 1-3 Lexical, Syntax, and Semantic Analysis"
        >
          <Search className="w-3.5 h-3.5 text-blue-400" />
          <span>Analyze Code</span>
        </button>

        <button
          onClick={onDetectErrors}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] border border-[#30363d] transition-colors disabled:opacity-50"
          title="Identify syntax, semantic, and AI-suspected issues"
        >
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          <span>Detect Errors</span>
          {errorCount > 0 && (
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-red-900/60 text-red-300 font-bold border border-red-700/50">
              {errorCount}
            </span>
          )}
        </button>

        <button
          onClick={onAutoCorrect}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-purple-900/40 hover:bg-purple-900/60 text-purple-200 border border-purple-700/50 transition-colors shadow-sm disabled:opacity-50"
          title="AI automatic error correction and logic preservation"
        >
          <Wand2 className="w-3.5 h-3.5 text-purple-400" />
          <span>Auto-Correct</span>
        </button>

        <button
          onClick={onTranspile}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-colors shadow-sm shadow-blue-600/30 disabled:opacity-50"
          title="Execute Stage 1-6 Compilation Pipeline into Target Language"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Transpile</span>
        </button>

        {/* AI Mode Selector */}
        <div className="flex items-center space-x-1.5 bg-[#21262d] px-2.5 py-1 rounded-md border border-[#30363d]">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          <span className="text-[11px] text-[#8b949e] font-medium hidden sm:inline">AI Mode:</span>
          <select
            value={aiMode || 'compiler_only'}
            onChange={(e) => setAiMode(e.target.value)}
            disabled={isLoading}
            className="bg-transparent text-xs text-[#c9d1d9] font-medium focus:outline-none cursor-pointer"
            title="Select Translation Engine Mode"
          >
            <option value="compiler_only" className="bg-[#161b22] text-[#c9d1d9]">⚡ Compiler Only</option>
            <option value="hybrid_correction" className="bg-[#161b22] text-purple-300">✨ Compiler + Gemini Correction</option>
            <option value="ai_assisted" className="bg-[#161b22] text-blue-300">🌐 AI-Assisted Translation</option>
          </select>
        </div>

        <button
          onClick={onRunCode}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-emerald-900/40 hover:bg-emerald-900/60 text-emerald-200 border border-emerald-700/50 transition-colors disabled:opacity-50"
          title="Execute source and target programs in isolated sandbox"
        >
          <Play className="w-3.5 h-3.5 text-emerald-400 fill-emerald-400" />
          <span>Run Code</span>
        </button>

        <button
          onClick={onCompare}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] border border-[#30363d] transition-colors disabled:opacity-50"
          title="Verify identical test output equivalence"
        >
          <Scale className="w-3.5 h-3.5 text-indigo-400" />
          <span>Compare Outputs</span>
        </button>

        <button
          onClick={onDownloadTarget}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] border border-[#30363d] transition-colors disabled:opacity-50"
          title="Download generated target code file"
        >
          <Download className="w-3.5 h-3.5 text-blue-400" />
          <span className="hidden lg:inline">Download</span>
        </button>

        {isLoading && onCancel && (
          <button
            onClick={onCancel}
            className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-md text-xs font-medium bg-red-900/40 hover:bg-red-900/60 text-red-200 border border-red-700/50 transition-colors"
            title="Cancel current operation"
          >
            <XCircle className="w-3.5 h-3.5 text-red-400" />
            <span>Cancel</span>
          </button>
        )}
      </div>

      {/* Secondary Controls: Optimization, Samples, Reset */}
      <div className="flex items-center space-x-3">
        {/* Optimization Toggle */}
        <div className="flex items-center space-x-2 bg-[#21262d] px-2.5 py-1 rounded-md border border-[#30363d]">
          <Sliders className="w-3.5 h-3.5 text-[#8b949e]" />
          <span className="text-xs text-[#8b949e]">Optimization</span>
          <button
            onClick={() => setOptimize(!optimize)}
            className={`w-8 h-4 rounded-full transition-colors relative flex items-center ${
              optimize ? 'bg-blue-600 justify-end' : 'bg-gray-600 justify-start'
            } px-0.5`}
            title="Toggle Stage 5 constant folding & dead code elimination"
          >
            <span className="w-3 h-3 bg-white rounded-full shadow-md"></span>
          </button>
        </div>

        {/* Sample Code Dropdown */}
        <div className="relative flex items-center">
          <FileCode className="w-3.5 h-3.5 text-[#8b949e] absolute left-2 pointer-events-none" />
          <select
            onChange={(e) => onSelectSample(e.target.value)}
            defaultValue=""
            className="pl-7 pr-3 py-1 bg-[#21262d] text-xs text-[#c9d1d9] border border-[#30363d] rounded-md focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="" disabled>Load Sample Code...</option>
            {samples?.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} {s.has_errors ? '⚠️' : '✓'}
              </option>
            ))}
          </select>
        </div>

        {/* Reset */}
        <button
          onClick={onReset}
          className="p-1.5 rounded-md text-[#8b949e] hover:text-white hover:bg-[#21262d] transition-colors"
          title="Reset editors and diagnostics"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
