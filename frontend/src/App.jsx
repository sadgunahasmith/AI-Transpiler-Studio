import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import ActionToolbar from './components/ActionToolbar';
import EditorPanel from './components/EditorPanel';
import ErrorsTab from './components/tabs/ErrorsTab';
import CompilerStagesTab from './components/tabs/CompilerStagesTab';
import AIExplanationTab from './components/tabs/AIExplanationTab';
import OutputTab from './components/tabs/OutputTab';
import CodeComparisonTab from './components/tabs/CodeComparisonTab';
import HistoryTab from './components/tabs/HistoryTab';
import MatrixTab from './components/tabs/MatrixTab';

import {
  getLanguages,
  getSamples,
  getSystemInfo,
  analyzeCode,
  detectErrors,
  autoCorrectCode,
  transpileCode,
  executeCode,
  compareExecutions,
  getHistory,
  clearHistory
} from './services/api';

import {
  AlertTriangle,
  Layers,
  Sparkles,
  Terminal,
  GitCompare,
  History,
  Table,
  GripHorizontal,
  ChevronsUpDown
} from 'lucide-react';

export default function App() {
  // Languages & Samples
  const [languages, setLanguages] = useState([]);
  const [samples, setSamples] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);

  // Editor states
  const [sourceLanguage, setSourceLanguage] = useState('c');
  const [targetLanguage, setTargetLanguage] = useState('python');
  const [sourceCode, setSourceCode] = useState('');
  const [targetCode, setTargetCode] = useState('');
  const [stdin, setStdin] = useState('');
  const [editorHeight, setEditorHeight] = useState(420);
  const [isDragging, setIsDragging] = useState(false);

  // Compiler & AI states
  const [compilerReport, setCompilerReport] = useState(null);
  const [errors, setErrors] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [correctedCode, setCorrectedCode] = useState('');
  const [modifications, setModifications] = useState([]);
  const [autoCorrectExplanation, setAutoCorrectExplanation] = useState('');
  const [aiExplanation, setAiExplanation] = useState('');
  const [optimize, setOptimize] = useState(true);
  const [aiMode, setAiMode] = useState('compiler_only');

  // Execution states
  const [executionResult, setExecutionResult] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [historyList, setHistoryList] = useState([]);

  // UI state
  const [activeTab, setActiveTab] = useState('errors');
  const [theme, setTheme] = useState(() => localStorage.getItem('transpiler-theme') || 'dark');
  const [showWorkspace, setShowWorkspace] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isFixing, setIsFixing] = useState(false);
  const [isTranspiling, setIsTranspiling] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('transpiler-theme', theme);
  }, [theme]);

  // Initial data loading
  useEffect(() => {
    async function init() {
      try {
        const [langs, smpls, sys, hist] = await Promise.all([
          getLanguages(),
          getSamples(),
          getSystemInfo(),
          getHistory()
        ]);
        setLanguages(langs);
        setSamples(smpls);
        setSystemInfo(sys);
        setHistoryList(hist);

        // Preload default sample (prompt C demo)
        const defaultSample = smpls.find(s => s.id === 'c-prompt-demo') || smpls[0];
        if (defaultSample) {
          setSourceLanguage(defaultSample.language);
          setTargetLanguage(defaultSample.target_default || 'python');
          setSourceCode(defaultSample.code);
        }
      } catch (err) {
        console.error("Initialization failed:", err);
      }
    }
    init();
  }, []);

  // Action 1: Analyze Code
  const handleAnalyze = async () => {
    setIsLoading(true);
    setIsAnalyzing(true);
    try {
      const res = await analyzeCode(sourceLanguage, sourceCode);
      setErrors(res.errors || []);
      setWarnings(res.warnings || []);
      setCompilerReport({
        stages: {
          lexical: { token_count: res.token_count, tokens: res.tokens },
          syntax: { ast: res.ast },
          semantic: { symbol_table: res.symbol_table, diagnostics: res.warnings },
          ir: null,
          optimized_ir: null,
          codegen: null
        }
      });
      setActiveTab('stages');
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
      setIsAnalyzing(false);
    }
  };

  // Action 2: Detect Errors
  const handleDetectErrors = async () => {
    setIsLoading(true);
    try {
      const res = await detectErrors(sourceLanguage, sourceCode);
      const compilerErrs = (res.compiler_errors || []).filter(e => e.severity === 'error');
      const warns = [
        ...(res.compiler_errors || []).filter(e => e.severity !== 'error'),
        ...(res.ai_suspicions || [])
      ];
      setErrors(compilerErrs);
      setWarnings(warns);
      setActiveTab('errors');
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Action 3: Auto-Correct
  const handleAutoCorrect = async () => {
    setIsLoading(true);
    setIsFixing(true);
    try {
      const res = await autoCorrectCode(sourceLanguage, sourceCode, errors);
      setCorrectedCode(res.corrected_code);
      setModifications(res.modifications || []);
      setAutoCorrectExplanation(res.explanation);
      setSourceCode(res.corrected_code); // apply correction to editor
      setErrors(res.remaining_errors || []);
      setActiveTab('comparison');
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
      setIsFixing(false);
    }
  };

  // Action 4: Transpile
  const handleTranspile = async () => {
    setIsLoading(true);
    setIsTranspiling(true);
    try {
      const res = await transpileCode(sourceLanguage, targetLanguage, sourceCode, optimize, aiMode);
      setCompilerReport(res);
      const generatedCode = res.transpiled_code || '';
      setTargetCode(generatedCode);
      setAiExplanation(res.ai_explanation || '');
      // Automatically run both programs with the same stdin after successful
      // transpilation, then compare their stdout. Execution may be blocked when
      // the local sandbox is disabled; that status is shown rather than guessed.
      if (res.success && generatedCode.trim()) {
        try {
          const comparison = await compareExecutions(
            sourceLanguage, targetLanguage, sourceCode, generatedCode, stdin
          );
          setComparisonResult(comparison);
        } catch (compareErr) {
          console.warn('Automatic output verification could not run:', compareErr);
          setComparisonResult(null);
        }
      } else {
        setComparisonResult(null);
      }
      if (res.corrected_source_code) {
        setCorrectedCode(res.corrected_source_code);
        setSourceCode(res.corrected_source_code);
      }
      if (res.errors?.length > 0) {
        setErrors(res.errors);
        setActiveTab('errors');
      } else {
        setActiveTab('output');
      }
      // Refresh history
      getHistory().then(setHistoryList);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
      setIsTranspiling(false);
    }
  };

  // Download Generated Code
  const handleDownloadTarget = () => {
    if (!targetCode) return;
    const extMap = { python: 'py', javascript: 'js', c: 'c', cpp: 'cpp', java: 'java' };
    const ext = extMap[targetLanguage] || 'txt';
    const blob = new Blob([targetCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `transpiled_output.${ext}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Cancel in-flight operation
  const handleCancel = () => {
    setIsLoading(false);
    setIsAnalyzing(false);
    setIsFixing(false);
    setIsTranspiling(false);
  };

  // Action 5: Run Code
  const handleRunCode = async () => {
    setIsLoading(true);
    try {
      // Execute target code or source code
      const res = await executeCode(targetLanguage, targetCode || sourceCode, stdin);
      setExecutionResult(res);
      setActiveTab('output');
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Action 6: Compare Outputs
  const handleCompare = async () => {
    setIsLoading(true);
    try {
      const res = await compareExecutions(
        sourceLanguage,
        targetLanguage,
        sourceCode,
        targetCode,
        stdin
      );
      setComparisonResult(res);
      setActiveTab('output');
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Action 7: Reset
  const handleReset = () => {
    setSourceCode('');
    setTargetCode('');
    setCompilerReport(null);
    setErrors([]);
    setWarnings([]);
    setCorrectedCode('');
    setModifications([]);
    setExecutionResult(null);
    setComparisonResult(null);
    setStdin('');
  };

  // Load sample code
  const handleSelectSample = (sampleId) => {
    const s = samples.find(x => x.id === sampleId);
    if (!s) return;
    setSourceLanguage(s.language);
    setTargetLanguage(s.target_default || 'python');
    setSourceCode(s.code);
    setTargetCode('');
    setCompilerReport(null);
    setErrors([]);
    setWarnings([]);
    setComparisonResult(null);
    setExecutionResult(null);
  };

  // Load past history run
  const handleLoadHistory = (item) => {
    setSourceLanguage(item.source_lang);
    setTargetLanguage(item.target_lang);
    setSourceCode(item.original_code);
    setTargetCode(item.target_code);
    setActiveTab('stages');
  };

  const handleClearHistory = async () => {
    await clearHistory();
    setHistoryList([]);
  };

  // Draggable Splitter Handler for Code vs Details Windows
  const handleSplitterMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    const startY = e.clientY;
    const startHeight = editorHeight;

    const onMouseMove = (moveEvent) => {
      const deltaY = moveEvent.clientY - startY;
      const newHeight = Math.max(160, Math.min(850, startHeight + deltaY));
      setEditorHeight(newHeight);
    };

    const onMouseUp = () => {
      setIsDragging(false);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  if (!showWorkspace) return <LandingPage onEnter={() => setShowWorkspace(true)} theme={theme} onToggleTheme={() => setTheme(current => current === 'dark' ? 'light' : 'dark')} />;

  return (
    <div className="flex flex-col min-h-screen bg-[#0d1117] text-[#c9d1d9] overflow-x-hidden overflow-y-auto">
      {/* Top Header */}
      <Navbar systemInfo={systemInfo} isAnalyzing={isAnalyzing} theme={theme} onToggleTheme={() => setTheme(current => current === 'dark' ? 'light' : 'dark')} onHome={() => setShowWorkspace(false)} />

      {/* Main Action Bar */}
      <ActionToolbar
        onAnalyze={handleAnalyze}
        onDetectErrors={handleDetectErrors}
        onAutoCorrect={handleAutoCorrect}
        onTranspile={handleTranspile}
        onRunCode={handleRunCode}
        onCompare={handleCompare}
        onReset={handleReset}
        optimize={optimize}
        setOptimize={setOptimize}
        aiMode={aiMode}
        setAiMode={setAiMode}
        onDownloadTarget={handleDownloadTarget}
        onCancel={handleCancel}
        samples={samples}
        onSelectSample={handleSelectSample}
        isLoading={isLoading}
        errorCount={errors.length}
      />

      {/* Main Dual Monaco Editor Layout */}
      <EditorPanel
        sourceLanguage={sourceLanguage}
        setSourceLanguage={setSourceLanguage}
        targetLanguage={targetLanguage}
        setTargetLanguage={setTargetLanguage}
        sourceCode={sourceCode}
        setSourceCode={setSourceCode}
        targetCode={targetCode}
        languages={languages}
        isTranspiling={isTranspiling}
        editorHeight={editorHeight}
      />

      {/* Draggable Resizer Splitter Bar */}
      <div
        onMouseDown={handleSplitterMouseDown}
        className={`h-4 bg-[#161b22] hover:bg-blue-600/20 border-y border-[#30363d] cursor-row-resize flex items-center justify-between px-4 select-none group transition-colors z-20 shrink-0 ${
          isDragging ? 'bg-blue-600/30 border-blue-500' : ''
        }`}
        title="Click and drag up/down to resize code editors vs details window"
      >
        <div className="flex items-center space-x-2 text-[10px] text-[#8b949e]">
          <span className="font-mono">Code Window: {editorHeight}px</span>
        </div>

        {/* Center Grip Handle */}
        <div className="flex items-center space-x-1.5 py-0.5 px-3 rounded-full bg-[#21262d] border border-[#30363d] group-hover:border-blue-500 transition-colors">
          <GripHorizontal className="w-3.5 h-3.5 text-[#8b949e] group-hover:text-blue-400" />
          <span className="text-[10px] text-[#8b949e] group-hover:text-blue-400 font-medium">Drag to Resize</span>
        </div>

        {/* Quick Size Presets */}
        <div className="flex items-center space-x-1" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => setEditorHeight(220)}
            className="px-2 py-0.5 rounded text-[10px] bg-[#21262d] hover:bg-blue-600 hover:text-white text-[#8b949e] border border-[#30363d] transition-colors"
            title="Expand Details Window"
          >
            ⬆ More Details
          </button>
          <button
            onClick={() => setEditorHeight(420)}
            className="px-2 py-0.5 rounded text-[10px] bg-[#21262d] hover:bg-blue-600 hover:text-white text-[#8b949e] border border-[#30363d] transition-colors"
            title="Balanced 50/50 View"
          >
            ↕ Balanced
          </button>
          <button
            onClick={() => setEditorHeight(650)}
            className="px-2 py-0.5 rounded text-[10px] bg-[#21262d] hover:bg-blue-600 hover:text-white text-[#8b949e] border border-[#30363d] transition-colors"
            title="Expand Code Window"
          >
            ⬇ More Code
          </button>
        </div>
      </div>

      {/* Bottom Inspector Tabs Panel */}
      <div className="border-t border-[#30363d] bg-[#161b22] flex flex-col flex-1 min-h-[360px] pb-6">
        {/* Tab Headers */}
        <div className="flex border-b border-[#30363d] px-3 space-x-1 overflow-x-auto text-xs bg-[#161b22]">
          <button
            onClick={() => setActiveTab('errors')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'errors'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Errors & Diagnostics</span>
            {errors.length > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-red-900/60 text-red-300 font-bold">
                {errors.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('stages')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'stages'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Compiler Stages (1–6)</span>
          </button>

          <button
            onClick={() => setActiveTab('explanation')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'explanation'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>AI Explanations</span>
          </button>

          <button
            onClick={() => setActiveTab('output')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'output'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            <span>Output & Verification</span>
          </button>

          <button
            onClick={() => setActiveTab('comparison')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'comparison'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <GitCompare className="w-3.5 h-3.5 text-cyan-400" />
            <span>Code Comparison (Diff)</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <History className="w-3.5 h-3.5 text-blue-400" />
            <span>History ({historyList.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('matrix')}
            className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'matrix'
                ? 'border-blue-500 text-blue-400 bg-[#21262d]/50'
                : 'border-transparent text-[#8b949e] hover:text-[#c9d1d9]'
            }`}
          >
            <Table className="w-3.5 h-3.5 text-gray-400" />
            <span>Feature Matrix</span>
          </button>
        </div>

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto bg-[#0d1117]/60">
          {activeTab === 'errors' && (
            <ErrorsTab
              errors={errors}
              warnings={warnings}
              onApplyFix={handleAutoCorrect}
              isFixing={isFixing}
            />
          )}

          {activeTab === 'stages' && (
            <CompilerStagesTab compilerReport={compilerReport} />
          )}

          {activeTab === 'explanation' && (
            <AIExplanationTab
              explanation={aiExplanation}
              autoCorrectExplanation={autoCorrectExplanation}
            />
          )}

          {activeTab === 'output' && (
            <OutputTab
              executionResult={executionResult}
              comparisonResult={comparisonResult}
              stdin={stdin}
              setStdin={setStdin}
            />
          )}

          {activeTab === 'comparison' && (
            <CodeComparisonTab
              originalCode={sourceCode}
              correctedCode={correctedCode}
              modifications={modifications}
              sourceLanguage={sourceLanguage}
              onApplyFix={handleAutoCorrect}
            />
          )}

          {activeTab === 'history' && (
            <HistoryTab
              history={historyList}
              onLoadHistory={handleLoadHistory}
              onClearHistory={handleClearHistory}
            />
          )}

          {activeTab === 'matrix' && <MatrixTab />}
        </div>
      </div>
    </div>
  );
}


