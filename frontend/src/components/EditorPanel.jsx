import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Copy, Download, Trash2, Upload, Check, Code, ArrowRight } from 'lucide-react';

export default function EditorPanel({
  sourceLanguage,
  setSourceLanguage,
  targetLanguage,
  setTargetLanguage,
  sourceCode,
  setSourceCode,
  targetCode,
  languages,
  isTranspiling,
  editorHeight = 420
}) {
  const [copied, setCopied] = useState(false);

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

  const handleCopy = () => {
    if (!targetCode) return;
    navigator.clipboard.writeText(targetCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!targetCode) return;
    const extMap = { c: 'c', cpp: 'cpp', python: 'py', javascript: 'js', java: 'java' };
    const ext = extMap[targetLanguage] || 'txt';
    const blob = new Blob([targetCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `transpiled_output.${ext}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      if (typeof content === 'string') {
        setSourceCode(content);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div 
      className="grid grid-cols-1 lg:grid-cols-2 gap-2 px-3 pt-2 pb-1 bg-[#0d1117] shrink-0 transition-all duration-75"
      style={{ height: `${editorHeight}px` }}
    >
      {/* Left Panel: Source Code Editor */}
      <div className="flex flex-col rounded-lg border border-[#30363d] bg-[#161b22] overflow-hidden shadow-sm h-full">
        {/* Source Header */}
        <div className="px-3 py-2 bg-[#1c2128] border-b border-[#30363d] flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
              <Code className="w-3.5 h-3.5" /> Source Code
            </span>
            <select
              value={sourceLanguage}
              onChange={(e) => setSourceLanguage(e.target.value)}
              className="bg-[#21262d] text-xs font-medium text-[#c9d1d9] border border-[#30363d] rounded px-2.5 py-1 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              {languages.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <label className="flex items-center space-x-1 px-2 py-1 rounded text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] cursor-pointer transition-colors" title="Upload local source file">
              <Upload className="w-3.5 h-3.5" />
              <span>Upload</span>
              <input type="file" onChange={handleFileUpload} className="hidden" />
            </label>
            <span className="text-[#6e7681]">|</span>
            <span className="text-[#8b949e] font-mono text-[11px]">
              {sourceCode.split('\n').length} lines
            </span>
          </div>
        </div>

        {/* Monaco Editor Source */}
        <div className="flex-1 w-full h-[calc(100%-42px)]">
          <Editor
            height="100%"
            language={getMonacoLang(sourceLanguage)}
            theme="vs-dark"
            value={sourceCode}
            onChange={(val) => setSourceCode(val || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              wordWrap: 'on',
              lineNumbers: 'on',
              renderWhitespace: 'selection',
            }}
          />
        </div>
      </div>

      {/* Right Panel: Transpiled Code Editor */}
      <div className="flex flex-col rounded-lg border border-[#30363d] bg-[#161b22] overflow-hidden shadow-sm h-full">
        {/* Target Header */}
        <div className="px-3 py-2 bg-[#1c2128] border-b border-[#30363d] flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <ArrowRight className="w-3.5 h-3.5" /> Transpiled Code
            </span>
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              className="bg-[#21262d] text-xs font-medium text-[#c9d1d9] border border-[#30363d] rounded px-2.5 py-1 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              {languages.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-1.5">
            <button
              onClick={handleCopy}
              disabled={!targetCode}
              className="p-1.5 rounded text-[#8b949e] hover:text-white hover:bg-[#21262d] transition-colors disabled:opacity-40"
              title="Copy transpiled code"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={handleDownload}
              disabled={!targetCode}
              className="p-1.5 rounded text-[#8b949e] hover:text-white hover:bg-[#21262d] transition-colors disabled:opacity-40"
              title="Download file"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Monaco Editor Target */}
        <div className="flex-1 w-full h-[calc(100%-42px)] relative">
          {isTranspiling && (
            <div className="absolute inset-0 bg-[#0d1117]/80 backdrop-blur-xs flex items-center justify-center z-10">
              <div className="flex flex-col items-center space-y-2 text-blue-400">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs font-medium">Running Compiler Transformation...</span>
              </div>
            </div>
          )}
          <Editor
            height="100%"
            language={getMonacoLang(targetLanguage)}
            theme="vs-dark"
            value={targetCode || "// Transpiled code will appear here after clicking Transpile or Auto-Correct"}
            options={{
              readOnly: false,
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              wordWrap: 'on',
              lineNumbers: 'on',
            }}
          />
        </div>
      </div>
    </div>
  );
}
