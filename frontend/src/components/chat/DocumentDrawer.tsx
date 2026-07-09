import React, { memo, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, X, Brain, Activity, Check, Copy, AlertCircle } from 'lucide-react';
import { Metric } from './types';
import { getConfidenceTheme } from './confidenceUtils'; // Re-use colors if desired, or duplicate small getScoreColor

interface DocumentPreviewDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  citationId: string;
  metric: Metric | null;
}

export const DocumentDrawer = memo(({ isOpen, onClose, citationId, metric }: DocumentPreviewDrawerProps) => {
  const [copied, setCopied] = useState(false);
  
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  const handleCopy = () => {
    if (!metric) return;
    const metaText = `Document: ${metric.source}\nPage: ${metric.page}\nSimilarity Score: ${metric.score}\nSelection Reason: ${metric.reason}`;
    navigator.clipboard.writeText(metaText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getScoreColor = (scoreStr: string) => {
    const score = parseFloat(scoreStr);
    if (isNaN(score)) return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    if (score >= 0.8) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (score >= 0.6) return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm z-40 rounded-3xl"
            aria-hidden="true"
          />
          <motion.div 
            initial={{ x: '100%', opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute top-0 right-0 bottom-0 w-full sm:w-96 bg-[#0f172a] border-l border-slate-700/50 shadow-2xl z-50 flex flex-col rounded-r-3xl overflow-hidden"
            role="dialog" aria-modal="true" aria-label="Document Preview Drawer" tabIndex={-1}
          >
            <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-[#0b1120]/50 shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <FileText className="w-4 h-4 text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-white font-bold text-sm truncate max-w-[200px]" title={metric?.source || "Source Document"}>{metric?.source || "Source Document"}</h3>
                  <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Citation [{citationId}]</p>
                </div>
              </div>
              <button 
                onClick={onClose}
                className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                aria-label="Close drawer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
              {metric ? (
                <>
                  <div className="bg-[#1e293b]/50 border border-slate-700/50 rounded-2xl p-5 space-y-4 shadow-sm">
                    <div>
                      <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Filename</span>
                      <div className="text-sm font-medium text-slate-200 flex items-center gap-2">{metric.source}</div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Page</span>
                        <div className="text-sm font-medium text-slate-200">{metric.page}</div>
                      </div>
                      <div>
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Similarity</span>
                        <div className={`inline-flex px-2 py-0.5 rounded text-[11px] font-bold border ${getScoreColor(metric.score)}`}>
                          {metric.score}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                      <Brain className="w-4 h-4 text-indigo-400" /> Retrieval Reason
                    </h4>
                    <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-4 text-sm text-slate-300 leading-relaxed italic">
                      "{metric.reason.replace('Selected because: ', '')}"
                    </div>
                  </div>
                  <div>
                    <h4 className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                      <Activity className="w-4 h-4 text-slate-400" /> Raw Chunk Content
                    </h4>
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center flex flex-col items-center">
                      <Activity className="w-8 h-8 text-slate-600 mb-3" />
                      <p className="text-[13px] text-slate-400 leading-relaxed font-medium">
                        Raw document preview is intentionally unavailable to minimize payload size and improve response latency.
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center pb-12">
                  <AlertCircle className="w-10 h-10 text-amber-500/50 mb-4" />
                  <p className="text-slate-400 text-sm">Metadata unavailable for this citation.</p>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-slate-800 bg-[#0b1120]/50 shrink-0">
              <button 
                onClick={handleCopy} disabled={!metric}
                className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed border border-slate-700"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied Metadata' : 'Copy Metadata'}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
});
