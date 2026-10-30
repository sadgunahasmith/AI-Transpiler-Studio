import React, { useState } from 'react';
import { Cpu, Sparkles, Terminal, Layers, Sun, Moon, Info, X, ArrowUpRight, Code2, ShieldCheck, WandSparkles, Home } from 'lucide-react';

export default function Navbar({ systemInfo, isAnalyzing, theme = 'dark', onToggleTheme = () => {}, onHome = () => {} }) {
  const [aboutOpen, setAboutOpen] = useState(false);
  const aiProvider = systemInfo?.ai_provider || "Heuristic Expert Engine";
  const pythonOk = systemInfo?.runtimes?.python?.available;
  const nodeOk = systemInfo?.runtimes?.javascript?.available;
  const cOk = systemInfo?.runtimes?.c?.available;

  return (
    <>
    <header className="app-navbar bg-[#161b22] border-b border-[#30363d] px-4 py-2.5 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-white text-base tracking-tight">UniversalTranspiler</h1>
            <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Compiler Design & AI
            </span>
          </div>
          <p className="text-xs text-[#8b949e]">
            Academic 6-Stage Compilation Pipeline & AI Auto-Repair IDE
          </p>
        </div>
      </div>

      {/* Navigation and live system status */}
      <div className="flex items-center space-x-2 text-xs">
        <button onClick={onHome} className="nav-action" aria-label="Back to intro page" title="Back to intro page"><Home size={15}/><span>Home</span></button>
        <button onClick={() => setAboutOpen(true)} className="nav-action" aria-label="About UniversalTranspiler"><Info size={15}/><span>About us</span></button>
        <button onClick={onToggleTheme} className="theme-toggle" aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
          {theme === 'dark' ? <Sun size={16}/> : <Moon size={16}/>}<span>{theme === 'dark' ? 'Light' : 'Dark'} mode</span>
        </button>
        {/* Compiler stages badge */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#21262d] border border-[#30363d] text-[#c9d1d9]">
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
          <span>Stages 1–6 Active</span>
        </div>

        {/* AI Engine Status */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-purple-950/40 border border-purple-800/40 text-purple-300">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          <span className="font-medium">{aiProvider}</span>
        </div>

        {/* System Runtimes */}
        <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded bg-[#21262d] border border-[#30363d]">
          <Terminal className="w-3.5 h-3.5 text-[#8b949e]" />
          <div className="flex items-center space-x-1.5">
            <span className={`inline-block w-2 h-2 rounded-full ${pythonOk ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
            <span className="text-[#8b949e]">Py</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className={`inline-block w-2 h-2 rounded-full ${nodeOk ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
            <span className="text-[#8b949e]">Node</span>
          </div>
          <div className="flex items-center space-x-1.5" title={cOk ? "Native C compiler ready" : "MinGW/Clang not in PATH"}>
            <span className={`inline-block w-2 h-2 rounded-full ${cOk ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
            <span className="text-[#8b949e]">GCC</span>
          </div>
        </div>

        {isAnalyzing && (
          <div className="flex items-center space-x-2 text-blue-400 animate-pulse">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
            <span>Compiling...</span>
          </div>
        )}
      </div>
    </header>
    {aboutOpen && <div className="about-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget) setAboutOpen(false); }}>
      <section className="about-dialog" role="dialog" aria-modal="true" aria-labelledby="about-title">
        <button className="about-close" onClick={() => setAboutOpen(false)} aria-label="Close about dialog"><X size={18}/></button>
        <div className="about-emblem"><Cpu size={28}/></div>
        <div className="about-eyebrow">MEET THE WORKSPACE</div>
        <h2 id="about-title">Code in one language.<br/><span>Think in any language.</span></h2>
        <p>UniversalTranspiler is an AI-assisted compiler design workspace for exploring code analysis, error detection, automatic repair, and cross-language transpilation in one place.</p>
        <div className="about-features">
          <div><span className="about-icon"><Code2 size={17}/></span><b>Six-stage pipeline</b><small>Explore the journey from tokens to generated code.</small></div>
          <div><span className="about-icon"><WandSparkles size={17}/></span><b>AI-assisted repair</b><small>Find issues and review suggested corrections.</small></div>
          <div><span className="about-icon"><ShieldCheck size={17}/></span><b>Compare & verify</b><small>Inspect output and compare program behavior.</small></div>
        </div>
        <div className="about-foot"><span className="status-dot"/> Built for learning, experimenting, and understanding code <ArrowUpRight size={14}/></div>
      </section>
    </div>}
    </>
  );
}


