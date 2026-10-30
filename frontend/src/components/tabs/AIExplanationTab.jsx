import React from 'react';
import { Sparkles, BookOpen, Lightbulb } from 'lucide-react';

export default function AIExplanationTab({ explanation, autoCorrectExplanation }) {
  const content = autoCorrectExplanation || explanation;

  if (!content) {
    return (
      <div className="p-8 text-center text-[#8b949e]">
        <Sparkles className="w-10 h-10 mx-auto mb-2 text-purple-400 opacity-60" />
        <p className="text-sm">Run "Auto-Correct" or "Transpile" to generate pedagogical AI explanations.</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 text-xs">
      {/* Header */}
      <div className="flex items-center space-x-2 text-purple-400">
        <BookOpen className="w-4 h-4" />
        <span className="font-semibold text-sm">Academic AI Explanations & Rationale</span>
      </div>

      {/* Auto-correction details */}
      {autoCorrectExplanation && (
        <div className="p-4 rounded-lg bg-purple-950/20 border border-purple-800/40 text-[#c9d1d9] space-y-2">
          <div className="flex items-center space-x-1.5 text-purple-300 font-semibold">
            <Lightbulb className="w-3.5 h-3.5" />
            <span>Code Repair Diagnostics</span>
          </div>
          <div className="prose prose-invert max-w-none text-xs leading-relaxed whitespace-pre-wrap font-sans">
            {autoCorrectExplanation}
          </div>
        </div>
      )}

      {/* Transpilation architectural explanation */}
      {explanation && (
        <div className="p-4 rounded-lg bg-[#161b22] border border-[#30363d] text-[#c9d1d9] space-y-2">
          <div className="flex items-center space-x-1.5 text-blue-400 font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Cross-Language Translation Analysis</span>
          </div>
          <div className="prose prose-invert max-w-none text-xs leading-relaxed whitespace-pre-wrap font-sans">
            {explanation}
          </div>
        </div>
      )}
    </div>
  );
}
