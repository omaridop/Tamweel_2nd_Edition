import React, { memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface FollowUpChipsProps {
  suggestions: string[];
  onClick: (text: string) => void;
}

export const FollowUpChips = memo(({ suggestions, onClick }: FollowUpChipsProps) => {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-3 ml-12 pl-1">
      <AnimatePresence>
        {suggestions.map((suggestion, idx) => (
          <motion.button
            key={idx}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            onClick={() => onClick(suggestion)}
            className="bg-slate-800/80 hover:bg-indigo-500/20 text-slate-300 hover:text-indigo-300 border border-slate-700 hover:border-indigo-500/50 px-3.5 py-1.5 rounded-full text-[11.5px] font-medium shadow-sm transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 active:scale-95"
            aria-label={`Follow-up question: ${suggestion}`}
          >
            {suggestion}
          </motion.button>
        ))}
      </AnimatePresence>
    </div>
  );
});
