import React, { memo } from 'react';
import { motion } from 'framer-motion';

interface ConfidenceWidgetProps {
  score: number | undefined;
}

export const ConfidenceWidget = memo(({ score }: ConfidenceWidgetProps) => {
  if (score === undefined || score === null) return null;
  
  const getConfidenceTheme = (s: number) => {
    if (s >= 4) return { color: 'bg-emerald-500', text: 'text-emerald-400', label: 'Strong Support' };
    if (s >= 3) return { color: 'bg-amber-500', text: 'text-amber-400', label: 'Partial Support' };
    return { color: 'bg-red-500', text: 'text-red-400', label: 'Unsupported' };
  };

  const theme = getConfidenceTheme(score);
  const pct = (score / 5) * 100;
  
  return (
    <div className="flex flex-col gap-1 w-full max-w-[220px] mt-2 mb-3 bg-[#0f172a]/50 p-2.5 rounded-xl border border-slate-700/50 shadow-sm" aria-label={`Confidence level: ${theme.label}`}>
      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-wider">
        <span className={theme.text}>{theme.label}</span>
        <span className="text-slate-400">{score}/5</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={`h-full rounded-full ${theme.color} shadow-[0_0_8px_currentColor]`} 
          aria-hidden="true"
        />
      </div>
    </div>
  );
});
