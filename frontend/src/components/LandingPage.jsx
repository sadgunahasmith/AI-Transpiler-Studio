import React from 'react';
import {
  ArrowDown, ArrowRight, ArrowUpRight, Braces, Cpu, FileCode2,
  GitBranch, Layers3, Moon, Play, Sparkles, Sun, WandSparkles, Zap
} from 'lucide-react';

const phases = [
  { n: '01', title: 'Lexical scan', sub: 'Source → tokens', icon: Braces },
  { n: '02', title: 'Syntax tree', sub: 'Tokens → AST', icon: GitBranch },
  { n: '03', title: 'Semantic check', sub: 'Types & scope', icon: Layers3 },
  { n: '04', title: 'Intermediate code', sub: 'Build neutral IR', icon: FileCode2 },
  { n: '05', title: 'Optimize', sub: 'Refine the logic', icon: Zap },
  { n: '06', title: 'Generate target', sub: 'IR → new language', icon: ArrowRight },
];

export default function LandingPage({ onEnter, theme, onToggleTheme }) {
  const goToPipeline = () => document.getElementById('landing-pipeline')?.scrollIntoView({ behavior: 'smooth' });

  return (
    <main className="landing-page">
      <header className="landing-nav">
        <a className="landing-brand" href="#top" aria-label="UniversalTranspiler home">
          <span className="landing-brand-mark"><Cpu size={21} /></span>
          <span><b>UniversalTranspiler</b><small>COMPILER DESIGN & AI</small></span>
        </a>
        <div className="landing-nav-actions">
          <span className="landing-live"><i /> 6-stage pipeline</span>
          <button className="landing-icon-button" onClick={onToggleTheme} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          </button>
          <button className="landing-nav-cta" onClick={onEnter}>Open workspace <ArrowUpRight size={15} /></button>
        </div>
      </header>

      <section className="landing-hero" id="top">
        <div className="landing-copy">
          <div className="landing-eyebrow"><span className="eyebrow-spark"><Sparkles size={13} /></span> A COMPILER LAB FOR EVERY LANGUAGE</div>
          <h1>See how your code<br />becomes <em>something new.</em></h1>
          <p className="landing-intro">Trace a program through every compiler stage. Analyze, repair, optimize, and translate code in a workspace built to make the process visible.</p>
          <div className="landing-actions">
            <button className="landing-primary" onClick={onEnter}><Play size={16} fill="currentColor" /> Launch compiler <ArrowRight size={17} /></button>
            <button className="landing-secondary" onClick={goToPipeline}><span>Explore the pipeline</span><ArrowDown size={15} /></button>
          </div>
          <div className="landing-proof"><span className="proof-separator" /><span>LEX · PARSE · ANALYZE · TRANSPILE</span></div>
        </div>

        <div className="landing-visual" aria-label="Animated diagram showing source code flowing through compiler stages into generated code">
          <div className="visual-grid" />
          <div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" />
          <div className="visual-arc arc-one" /><div className="visual-arc arc-two" />
          <div className="visual-core"><div className="core-halo" /><div className="core-glyph"><Cpu size={34} strokeWidth={1.45} /></div><small>TRANSPILER</small></div>
          <div className="visual-code-chip chip-source"><span className="chip-dots"><i /><i /><i /></span><small>source.c</small><code><b>int</b> main() {'{'}<br />&nbsp;&nbsp;printf(<i>"Hello"</i>);<br />{'}'}</code></div>
          <div className="visual-code-chip chip-target"><span className="chip-status"><i /> READY</span><small>target.py</small><code><b>def</b> main():<br />&nbsp;&nbsp;print(<i>"Hello"</i>)</code></div>
          <div className="visual-tag tag-lex"><Braces size={13} /> TOKENS</div>
          <div className="visual-tag tag-ast"><GitBranch size={13} /> AST</div>
          <div className="visual-tag tag-ir"><Layers3 size={13} /> IR</div>
          <div className="visual-bottom-label"><span className="signal-bars"><i /><i /><i /><i /><i /></span> CODE IN MOTION <span>01 / 06</span></div>
        </div>
      </section>

      <section className="landing-pipeline" id="landing-pipeline">
        <div className="pipeline-intro">
          <div><span className="section-kicker">UNDER THE HOOD</span><h2>One source. <em>Six clear stages.</em></h2></div>
          <p>Follow the compilation journey from the first token to executable target code—with each transformation laid out for inspection.</p>
        </div>
        <div className="landing-stage-track">
          {phases.map(({ n, title, sub, icon: Icon }) => (
            <div className="landing-stage" key={n}>
              <span className="stage-icon"><Icon size={16} /></span>
              <span className="stage-num">{n}</span>
              <b>{title}</b><small>{sub}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-capabilities">
        <div className="capability"><span><Layers3 size={17} /></span><div><b>Understand each stage</b><small>Tokens, AST, symbols, IR, optimization, and generated output.</small></div></div>
        <div className="capability"><span><WandSparkles size={17} /></span><div><b>Repair with context</b><small>Detect issues and review AI-assisted corrections.</small></div></div>
        <div className="capability"><span><GitBranch size={17} /></span><div><b>Verify the result</b><small>Run both programs and compare their outputs.</small></div></div>
        <button className="landing-bottom-cta" onClick={onEnter}>Go to the compiler <ArrowRight size={16} /></button>
      </section>
      <footer className="landing-footer"><span>UniversalTranspiler</span><span>ACADEMIC 6-STAGE COMPILATION PIPELINE</span><span>BUILT TO MAKE COMPILERS VISIBLE <span className="footer-glow">✳</span></span></footer>
    </main>
  );
}
