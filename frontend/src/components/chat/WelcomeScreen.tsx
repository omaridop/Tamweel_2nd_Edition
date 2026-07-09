import React, { memo } from 'react';
import { Brain, Zap, Info } from 'lucide-react';

export const WelcomeScreen = memo(({ onSuggestionClick }: { onSuggestionClick: (text: string) => void }) => {
  const suggestions = [
    "What are the underwriting criteria for commercial real estate?",
    "How does the LTV ratio affect the final score?",
    "Summarize the recent changes to the credit policy.",
    "Explain the risk factors for unsecured lending."
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center animate-fade-in pb-10 mt-8">
      <div className="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(99,102,241,0.15)] border border-indigo-500/20">
        <Brain className="w-8 h-8 text-indigo-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Tamweel Policy Assistant</h2>
      <p className="text-slate-400 text-sm max-w-md mb-10 leading-relaxed">
        I'm an AI assistant grounded securely in Tamweel's financial policies. Ask me anything about underwriting, credit scoring, or risk guidelines.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
        {suggestions.map((text, i) => (
          <button 
            key={i}
            onClick={() => onSuggestionClick(text)}
            className="text-left bg-slate-800/40 hover:bg-slate-800/80 border border-slate-700/50 p-4 rounded-xl transition-all duration-200 group flex items-start gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            aria-label={`Suggestion: ${text}`}
          >
            <Zap className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0 opacity-70 group-hover:opacity-100 transition-opacity" />
            <span className="text-sm text-slate-300 group-hover:text-white leading-snug">{text}</span>
          </button>
        ))}
      </div>
      
      <div className="mt-12 flex items-center gap-2 text-[11px] text-slate-500 bg-slate-900/50 px-4 py-2 rounded-full border border-slate-800">
        <Info className="w-3.5 h-3.5" />
        <span>Financial decisions should be verified by a human underwriter.</span>
      </div>
    </div>
  );
});
