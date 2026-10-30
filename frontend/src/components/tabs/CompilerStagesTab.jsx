import React, { useState } from 'react';
import { 
  Binary, Network, Table, FileCode2, Zap, 
  CheckCircle2, Search, SlidersHorizontal, ChevronLeft, ChevronRight, Copy, Check 
} from 'lucide-react';
const pipelineStages = [
  { number: '01', title: 'Lexical analysis', detail: 'Source → tokens' },
  { number: '02', title: 'Syntax analysis', detail: 'Tokens → AST' },
  { number: '03', title: 'Semantic analysis', detail: 'Scopes & types' },
  { number: '04', title: 'Intermediate code', detail: 'Three-address code' },
  { number: '05', title: 'Optimization', detail: 'Fold & dead-code pass' },
  { number: '06', title: 'Code generation', detail: 'Target language' }
];

function CompilerPipelineDiagram() {
  return (
    <section className="compiler-pipeline-diagram" aria-label="Six-stage compiler pipeline">
      <div className="pipeline-heading">
        <span className="pipeline-pulse" aria-hidden="true" />
        <span>COMPILATION PIPELINE</span>
        <span className="pipeline-caption">SOURCE CODE <span aria-hidden="true">→</span> TARGET CODE</span>
      </div>
      <div className="pipeline-track">
        {pipelineStages.map((stage) => (
          <div className="pipeline-stage" key={stage.number}>
            <span className="pipeline-number">{stage.number}</span>
            <span className="pipeline-name">{stage.title}</span>
            <span className="pipeline-detail">{stage.detail}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function CompilerStagesTab({ compilerReport }) {
  const [activeStage, setActiveStage] = useState('stage1');
  const [tokenSearch, setTokenSearch] = useState('');
  const [tokenPage, setTokenPage] = useState(1);
  const [copiedAst, setCopiedAst] = useState(false);
  const TOKENS_PER_PAGE = 50;

  if (!compilerReport || !compilerReport.stages) {
    return (
      <div className="p-8 text-center text-[#8b949e]">
        <Binary className="w-10 h-10 mx-auto mb-2 text-indigo-400 opacity-60" />
        <CompilerPipelineDiagram />
        <p className="text-sm">Click "Analyze Code" or "Transpile" to inspect the compilation stages.</p>
      </div>
    );
  }

  const { lexical, syntax, semantic, ir, optimized_ir, codegen } = compilerReport.stages;

  const filteredTokens = (lexical?.tokens || []).filter(t => 
    t.value.toLowerCase().includes(tokenSearch.toLowerCase()) ||
    t.type.toLowerCase().includes(tokenSearch.toLowerCase())
  );

  const totalPages = Math.max(1, Math.ceil(filteredTokens.length / TOKENS_PER_PAGE));
  const displayedTokens = filteredTokens.slice((tokenPage - 1) * TOKENS_PER_PAGE, tokenPage * TOKENS_PER_PAGE);

  const getTokenTypeColor = (type) => {
    switch (type) {
      case 'KEYWORD': return 'bg-purple-900/50 text-purple-300 border-purple-700/50';
      case 'IDENTIFIER': return 'bg-blue-900/50 text-blue-300 border-blue-700/50';
      case 'NUMBER': return 'bg-emerald-900/50 text-emerald-300 border-emerald-700/50';
      case 'STRING': return 'bg-amber-900/50 text-amber-300 border-amber-700/50';
      case 'OPERATOR': return 'bg-cyan-900/50 text-cyan-300 border-cyan-700/50';
      case 'DELIMITER': return 'bg-gray-800 text-gray-300 border-gray-600';
      default: return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const timings = compilerReport.stage_timings || {};

  return (
    <div className="flex flex-col h-full text-xs">
      <CompilerPipelineDiagram />
      {/* Real-time Compiler Telemetry Header */}
      {timings.total_ms !== undefined && (
        <div className="bg-[#0d1117] border-b border-[#30363d] px-4 py-2 flex flex-wrap items-center justify-between gap-2 text-[11px]">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-emerald-400">⚡ Stage Telemetry:</span>
            <span className="text-[#8b949e]">Total: <strong className="text-white">{timings.total_ms} ms</strong></span>
          </div>
          <div className="flex items-center flex-wrap gap-2 text-[#8b949e] font-mono text-[10px]">
            <span className="bg-[#161b22] px-2 py-0.5 rounded border border-[#30363d]">S1 (Lex): <strong className="text-cyan-300">{timings.lexical_ms}ms</strong></span>
            <span className="bg-[#161b22] px-2 py-0.5 rounded border border-[#30363d]">S2 (Syn): <strong className="text-blue-300">{timings.syntax_ms}ms</strong></span>
            <span className="bg-[#161b22] px-2 py-0.5 rounded border border-[#30363d]">S3 (Sem): <strong className="text-purple-300">{timings.semantic_ms}ms</strong></span>
            <span className="bg-[#161b22] px-2 py-0.5 rounded border border-[#30363d]">S4 (IR): <strong className="text-amber-300">{timings.ir_ms}ms</strong></span>
            <span className="bg-[#161b22] px-2 py-0.5 rounded border border-[#30363d]">S5 (Opt): <strong className="text-emerald-300">{timings.optimizer_ms}ms</strong></span>
            <span className="bg-[#161b22] px-2 py-0.5 rounded border border-[#30363d]">S6 (CodeGen): <strong className="text-indigo-300">{timings.codegen_ms}ms</strong></span>
          </div>
        </div>
      )}

      {/* Substage Navigation Tabs */}
      <div className="flex border-b border-[#30363d] bg-[#161b22] px-3 space-x-1 overflow-x-auto">
        <button
          onClick={() => setActiveStage('stage1')}
          className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors whitespace-nowrap ${
            activeStage === 'stage1'
              ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
              : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <Binary className="w-3.5 h-3.5" />
          <span>Stage 1: Tokens ({lexical?.token_count || 0}) {timings.lexical_ms ? `[${timings.lexical_ms}ms]` : ''}</span>
        </button>

        <button
          onClick={() => setActiveStage('stage2')}
          className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors whitespace-nowrap ${
            activeStage === 'stage2'
              ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
              : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <Network className="w-3.5 h-3.5" />
          <span>Stage 2: Syntax AST {timings.syntax_ms ? `[${timings.syntax_ms}ms]` : ''}</span>
        </button>

        <button
          onClick={() => setActiveStage('stage3')}
          className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors whitespace-nowrap ${
            activeStage === 'stage3'
              ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
              : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <Table className="w-3.5 h-3.5" />
          <span>Stage 3: Symbol Table {timings.semantic_ms ? `[${timings.semantic_ms}ms]` : ''}</span>
        </button>

        <button
          onClick={() => setActiveStage('stage4')}
          className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors whitespace-nowrap ${
            activeStage === 'stage4'
              ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
              : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <FileCode2 className="w-3.5 h-3.5" />
          <span>Stage 4: Intermediate TAC {timings.ir_ms ? `[${timings.ir_ms}ms]` : ''}</span>
        </button>

        <button
          onClick={() => setActiveStage('stage5')}
          className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors whitespace-nowrap ${
            activeStage === 'stage5'
              ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
              : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>Stage 5: Optimization {timings.optimizer_ms ? `[${timings.optimizer_ms}ms]` : ''}</span>
        </button>

        <button
          onClick={() => setActiveStage('stage6')}
          className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors whitespace-nowrap ${
            activeStage === 'stage6'
              ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
              : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Stage 6: CodeGen Validation {timings.codegen_ms ? `[${timings.codegen_ms}ms]` : ''}</span>
        </button>
      </div>

      {/* Stage Content Panel */}
      <div className="p-4 overflow-y-auto flex-1">
        {/* Stage 1: Lexical Tokens */}
        {activeStage === 'stage1' && (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-semibold text-[#c9d1d9]">
                Token Stream Table ({filteredTokens.length} tokens total)
              </span>

              <div className="flex items-center space-x-2">
                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="flex items-center space-x-1.5 bg-[#21262d] px-2 py-0.5 rounded border border-[#30363d] text-[#c9d1d9]">
                    <button
                      onClick={() => setTokenPage(p => Math.max(1, p - 1))}
                      disabled={tokenPage <= 1}
                      className="p-1 rounded hover:bg-[#30363d] disabled:opacity-30 disabled:hover:bg-transparent"
                      title="Previous Page"
                    >
                      <ChevronLeft className="w-3.5 h-3.5" />
                    </button>
                    <span className="text-[11px] font-mono">
                      {tokenPage} / {totalPages}
                    </span>
                    <button
                      onClick={() => setTokenPage(p => Math.min(totalPages, p + 1))}
                      disabled={tokenPage >= totalPages}
                      className="p-1 rounded hover:bg-[#30363d] disabled:opacity-30 disabled:hover:bg-transparent"
                      title="Next Page"
                    >
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}

                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-[#8b949e] absolute left-2 top-2 pointer-events-none" />
                  <input
                    type="text"
                    placeholder="Filter token type or value..."
                    value={tokenSearch}
                    onChange={(e) => {
                      setTokenSearch(e.target.value);
                      setTokenPage(1);
                    }}
                    className="pl-7 pr-3 py-1 bg-[#21262d] border border-[#30363d] rounded text-xs text-[#c9d1d9] focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="overflow-x-auto rounded border border-[#30363d]">
              <table className="w-full text-left font-mono text-[11px]">
                <thead className="bg-[#21262d] text-[#8b949e] uppercase border-b border-[#30363d]">
                  <tr>
                    <th className="p-2">#</th>
                    <th className="p-2">Token Type</th>
                    <th className="p-2">Lexeme (Value)</th>
                    <th className="p-2">Line</th>
                    <th className="p-2">Col</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#30363d]">
                  {displayedTokens.map((t, idx) => (
                    <tr key={idx} className="hover:bg-[#1f242c] transition-colors">
                      <td className="p-2 text-[#8b949e]">{(tokenPage - 1) * TOKENS_PER_PAGE + idx + 1}</td>
                      <td className="p-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getTokenTypeColor(t.type)}`}>
                          {t.type}
                        </span>
                      </td>
                      <td className="p-2 font-bold text-[#c9d1d9] truncate max-w-xs">{t.value}</td>
                      <td className="p-2 text-[#8b949e]">{t.line}</td>
                      <td className="p-2 text-[#8b949e]">{t.column}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-between text-[11px] text-[#8b949e] px-1">
                <span>Showing {(tokenPage - 1) * TOKENS_PER_PAGE + 1} to {Math.min(filteredTokens.length, tokenPage * TOKENS_PER_PAGE)} of {filteredTokens.length} tokens</span>
                <div className="flex space-x-1">
                  <button
                    onClick={() => setTokenPage(p => Math.max(1, p - 1))}
                    disabled={tokenPage <= 1}
                    className="px-2 py-0.5 rounded bg-[#21262d] hover:bg-[#30363d] disabled:opacity-30"
                  >
                    Prev
                  </button>
                  <button
                    onClick={() => setTokenPage(p => Math.min(totalPages, p + 1))}
                    disabled={tokenPage >= totalPages}
                    className="px-2 py-0.5 rounded bg-[#21262d] hover:bg-[#30363d] disabled:opacity-30"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Stage 2: Abstract Syntax Tree */}
        {activeStage === 'stage2' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-[#c9d1d9]">Abstract Syntax Tree (AST Hierarchy)</span>
              <button
                onClick={() => {
                  if (syntax?.ast) {
                    navigator.clipboard.writeText(JSON.stringify(syntax.ast, null, 2));
                    setCopiedAst(true);
                    setTimeout(() => setCopiedAst(false), 2000);
                  }
                }}
                className="flex items-center space-x-1 px-2.5 py-1 rounded bg-[#21262d] hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] transition-colors"
              >
                {copiedAst ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedAst ? 'Copied AST' : 'Copy AST JSON'}</span>
              </button>
            </div>
            <pre className="p-3 bg-[#0d1117] rounded-lg border border-[#30363d] font-mono text-[11px] text-blue-300 overflow-x-auto min-h-[180px]">
              {JSON.stringify(syntax?.ast, null, 2)}
            </pre>
          </div>
        )}

        {/* Stage 3: Symbol Table */}
        {activeStage === 'stage3' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-[#c9d1d9]">
                Scoped Symbol Table ({semantic?.symbol_table?.length || 0} symbols)
              </span>
            </div>

            <div className="overflow-x-auto rounded border border-[#30363d]">
              <table className="w-full text-left font-mono text-[11px]">
                <thead className="bg-[#21262d] text-[#8b949e] uppercase border-b border-[#30363d]">
                  <tr>
                    <th className="p-2">Name</th>
                    <th className="p-2">Category</th>
                    <th className="p-2">Type</th>
                    <th className="p-2">Scope</th>
                    <th className="p-2">Decl Line</th>
                    <th className="p-2">Initialized</th>
                    <th className="p-2">Refs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#30363d]">
                  {(semantic?.symbol_table || []).map((s, idx) => (
                    <tr key={idx} className="hover:bg-[#1f242c]">
                      <td className="p-2 font-bold text-blue-400">{s.name}</td>
                      <td className="p-2 capitalize text-[#8b949e]">{s.category}</td>
                      <td className="p-2 text-purple-300">{s.type}</td>
                      <td className="p-2 text-[#8b949e]">Level {s.scope_level}</td>
                      <td className="p-2 text-[#8b949e]">{s.line}</td>
                      <td className="p-2">
                        {s.is_initialized ? (
                          <span className="text-emerald-400 font-semibold">Yes</span>
                        ) : (
                          <span className="text-amber-400 font-semibold">No</span>
                        )}
                      </td>
                      <td className="p-2 font-bold text-cyan-300">{s.reference_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Stage 4: Intermediate Representation (TAC) */}
        {activeStage === 'stage4' && (
          <div className="space-y-2">
            <span className="font-semibold text-[#c9d1d9]">Language-Neutral Three-Address Code (TAC)</span>
            <pre className="p-3 bg-[#0d1117] rounded-lg border border-[#30363d] font-mono text-[11px] text-emerald-400 overflow-x-auto max-h-[320px]">
              {ir?.tac || "// Intermediate representation will be generated upon analysis"}
            </pre>
          </div>
        )}

        {/* Stage 5: Optimization */}
        {activeStage === 'stage5' && (
          <div className="space-y-3">
            {/* Optimization Stats Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div className="p-2.5 bg-[#21262d] border border-[#30363d] rounded-lg text-center">
                <span className="text-[10px] uppercase text-[#8b949e] font-semibold">Constants Folded</span>
                <p className="text-base font-bold text-emerald-400">{optimized_ir?.stats?.constants_folded || 0}</p>
              </div>
              <div className="p-2.5 bg-[#21262d] border border-[#30363d] rounded-lg text-center">
                <span className="text-[10px] uppercase text-[#8b949e] font-semibold">Propagated</span>
                <p className="text-base font-bold text-blue-400">{optimized_ir?.stats?.constants_propagated || 0}</p>
              </div>
              <div className="p-2.5 bg-[#21262d] border border-[#30363d] rounded-lg text-center">
                <span className="text-[10px] uppercase text-[#8b949e] font-semibold">Simplified</span>
                <p className="text-base font-bold text-purple-400">{optimized_ir?.stats?.expressions_simplified || 0}</p>
              </div>
              <div className="p-2.5 bg-[#21262d] border border-[#30363d] rounded-lg text-center">
                <span className="text-[10px] uppercase text-[#8b949e] font-semibold">Dead Code Eliminated</span>
                <p className="text-base font-bold text-amber-400">{optimized_ir?.stats?.dead_code_eliminated || 0}</p>
              </div>
            </div>

            {/* Optimization Log Details */}
            {optimized_ir?.stats?.details?.length > 0 && (
              <div className="p-2.5 bg-[#21262d]/50 rounded-lg border border-[#30363d]">
                <span className="text-[10px] uppercase font-bold text-[#8b949e]">Optimization Log:</span>
                <ul className="mt-1 space-y-1 list-disc list-inside font-mono text-[11px] text-emerald-300">
                  {optimized_ir.stats.details.map((d, i) => (
                    <li key={i}>{d}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Optimized TAC */}
            <div>
              <span className="font-semibold text-[#c9d1d9] block mb-1">Optimized Three-Address Code</span>
              <pre className="p-3 bg-[#0d1117] rounded-lg border border-[#30363d] font-mono text-[11px] text-cyan-300 overflow-x-auto max-h-[220px]">
                {optimized_ir?.tac || "// Optimized TAC"}
              </pre>
            </div>
          </div>
        )}

        {/* Stage 6: CodeGen Validation */}
        {activeStage === 'stage6' && (
          <div className="space-y-3">
            <div className="p-3 bg-[#21262d] border border-[#30363d] rounded-lg flex items-center justify-between">
              <div>
                <span className="font-semibold text-[#c9d1d9] block">Target Syntax Verification</span>
                <p className="text-[#8b949e] mt-0.5">
                  {codegen?.validation?.message || "Target code successfully verified by compiler pipeline."}
                </p>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                codegen?.validation?.valid !== false
                  ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800'
                  : 'bg-red-950/60 text-red-300 border-red-800'
              }`}>
                {codegen?.validation?.valid !== false ? 'VALID' : 'INVALID'}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

