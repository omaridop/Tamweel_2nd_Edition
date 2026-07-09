import React, { memo, useState } from 'react';
import { Database, ChevronUp, ChevronDown, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatMessageData } from './types';

export const SourcesPanel = memo(({ message }: { message: ChatMessageData }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const sources = message.sources || [];
  
  if (sources.length === 0) return null;

  return (
    <div className="mt-4 w-full bg-slate-900/40 rounded-xl border border-slate-700/50 overflow-hidden text-left shadow-sm">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-slate-800/40 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-500"
      >
        <div className="flex items-center gap-3">
          <Database className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-semibold text-slate-300">Sources & Details</span>
          <div className="text-[10px] px-2 py-0.5 rounded-full border bg-slate-800 text-slate-400 border-slate-700">
            {sources.length} sources
          </div>
        </div>
        <div className="text-slate-500">
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="p-3 pt-0 border-t border-slate-700/30 mx-3">
              <div className="space-y-2 mt-3">
                {sources.map((src, i) => {
                  const simPct = Math.round(src.similarity * 100);
                  return (
                    <div key={i} className="bg-slate-800/50 rounded-lg p-2.5 text-xs flex flex-col gap-1.5 hover:bg-slate-800 transition-colors border border-slate-700/50">
                      <div className="flex justify-between items-center text-slate-300">
                        <span className="font-bold text-indigo-300 flex items-center gap-1.5 truncate pr-2">
                          <FileText size={12} className="shrink-0"/> 
                          <span className="bg-indigo-500/20 text-indigo-300 px-1 rounded text-[10px] font-mono shrink-0">{src.id}</span>
                          <span className="truncate">{src.document_name} {src.page ? `(p.${src.page})` : ''}</span>
                        </span>
                        <span className="text-emerald-400 font-mono bg-emerald-400/10 px-1.5 py-0.5 rounded shrink-0 text-[10px]">
                          {simPct}% Match
                        </span>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-1 mt-1 overflow-hidden">
                        <div className="bg-indigo-500 h-1 rounded-full" style={{ width: `${simPct}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {message.retrieval_stats && (
                <div className="mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between text-[10px] text-slate-500">
                  <span>Generation Time: {message.retrieval_stats.generation_time_ms}ms</span>
                  <span>Chunks: {message.retrieval_stats.chunks_used} used / {message.retrieval_stats.chunks_retrieved} retrieved</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});
