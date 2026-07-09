import React, { memo } from 'react';
import { SourceCitation } from './types';

export const SourceCard = memo(({ source }: { source: SourceCitation }) => {
  const simPct = Math.round(source.similarity * 100);
  
  return (
    <div className="bg-slate-800/80 rounded-xl p-3 text-xs flex flex-col gap-2 hover:bg-slate-700/80 transition-colors border border-slate-700 shadow-sm">
      <div className="flex justify-between items-center text-slate-200">
        <span className="font-bold flex items-center gap-2 truncate pr-2">
          <span className="bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded text-[10px] font-mono shrink-0 border border-indigo-500/20 shadow-sm">{source.id}</span>
          <span className="truncate">{source.document_name} {source.page ? `(p.${source.page})` : ''}</span>
        </span>
        <span className="text-emerald-400 font-mono bg-emerald-400/10 px-1.5 py-0.5 rounded shrink-0 text-[10px] border border-emerald-500/20">
          {simPct}%
        </span>
      </div>
      {/* Graceful fallback snippet placeholder */}
      {/* <div className="text-slate-400 italic leading-relaxed text-[11px] mt-1 line-clamp-2">"Snippet matching semantic search intent..."</div> */}
    </div>
  );
});
