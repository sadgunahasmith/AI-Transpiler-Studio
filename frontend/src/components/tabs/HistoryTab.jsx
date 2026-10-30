import React from 'react';
import { History, Clock, ArrowRight, Trash2, ArrowUpRight } from 'lucide-react';

export default function HistoryTab({ history, onLoadHistory, onClearHistory }) {
  if (!history || history.length === 0) {
    return (
      <div className="p-8 text-center text-[#8b949e]">
        <History className="w-10 h-10 mx-auto mb-2 text-blue-400 opacity-60" />
        <p className="text-sm">No translation history yet. Transpiled programs are automatically saved here.</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3 text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <History className="w-4 h-4 text-blue-400" />
          <span className="font-semibold text-sm text-[#c9d1d9]">Translation Run History ({history.length})</span>
        </div>

        <button
          onClick={onClearHistory}
          className="flex items-center space-x-1 px-2.5 py-1 rounded bg-[#21262d] hover:bg-red-950/40 text-[#8b949e] hover:text-red-400 border border-[#30363d] transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear History</span>
        </button>
      </div>

      <div className="divide-y divide-[#30363d] border border-[#30363d] rounded-lg overflow-hidden bg-[#161b22]">
        {history.map((item) => (
          <div key={item.id} className="p-3 flex items-center justify-between hover:bg-[#1f242c] transition-colors">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-blue-400 uppercase">{item.source_lang}</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#8b949e]" />
                <span className="font-bold text-emerald-400 uppercase">{item.target_lang}</span>
                <span className="text-[10px] text-[#8b949e] flex items-center space-x-1 ml-2">
                  <Clock className="w-3 h-3" />
                  <span>{item.timestamp}</span>
                </span>
              </div>
              <p className="text-[11px] text-[#8b949e] font-mono truncate max-w-md">
                {item.original_code?.split('\n')[0] || "Code snippet"}
              </p>
            </div>

            <button
              onClick={() => onLoadHistory(item)}
              className="flex items-center space-x-1 px-2.5 py-1 rounded bg-[#21262d] hover:bg-blue-600 hover:text-white text-[#c9d1d9] border border-[#30363d] transition-colors"
            >
              <span>Load</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
