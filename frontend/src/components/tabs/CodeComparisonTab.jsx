import React from 'react';
import { DiffEditor } from '@monaco-editor/react';
import { GitCompare, Check, Wand2 } from 'lucide-react';

export default function CodeComparisonTab({ originalCode, correctedCode, modifications, sourceLanguage, onApplyFix }) {
  const getMonacoLang = (langId) => {
    switch (langId?.toLowerCase()) {
      case 'c':
      case 'cpp':
      case 'c++':
        return 'cpp';
      case 'python':
      case 'py':
        return 'python';
      case 'javascript':
      case 'js':
        return 'javascript';
      case 'java':
        return 'java';
      default:
        return 'plaintext';
    }
  };

  const hasChanges = originalCode !== correctedCode && Boolean(correctedCode);

  return (
    <div className="flex flex-col h-full p-4 space-y-3 text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <GitCompare className="w-4 h-4 text-purple-400" />
          <span className="font-semibold text-sm text-[#c9d1d9]">
            Source Code Correction Comparison (Before vs After)
          </span>
        </div>

        {hasChanges && (
          <span className="px-2.5 py-0.5 rounded-full bg-purple-950/60 text-purple-300 font-semibold border border-purple-800 text-[11px]">
            {modifications?.length || 1} Modification(s) Applied
          </span>
        )}
      </div>

      {/* Modifications List */}
      {modifications && modifications.length > 0 && (
        <div className="p-3 bg-[#161b22] rounded-lg border border-[#30363d] space-y-1.5">
          <span className="font-semibold text-purple-300 block text-[11px] uppercase tracking-wider">
            Applied Repairs:
          </span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {modifications.map((m, i) => (
              <div key={i} className="flex items-start space-x-2 text-[11px] bg-[#21262d] p-2 rounded">
                <Check className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <span className="font-bold text-[#c9d1d9]">Line {m.line}:</span>{' '}
                  <span className="text-[#8b949e]">{m.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Monaco Diff Editor */}
      <div className="h-[280px] rounded-lg border border-[#30363d] overflow-hidden bg-[#0d1117]">
        <DiffEditor
          height="100%"
          language={getMonacoLang(sourceLanguage)}
          original={originalCode || "// Original source code"}
          modified={correctedCode || originalCode || "// Corrected source code"}
          theme="vs-dark"
          options={{
            readOnly: true,
            renderSideBySide: true,
            fontSize: 12,
            fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  );
}
