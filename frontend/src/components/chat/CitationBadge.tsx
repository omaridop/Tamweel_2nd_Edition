import React, { memo } from 'react';
import { SourceCitation } from './types';

interface CitationBadgeProps {
  citationId: string;
  source: SourceCitation | undefined;
  onClick?: (id: string) => void;
}

export const CitationBadge = memo(({ citationId, source, onClick }: CitationBadgeProps) => {
  const handleClick = () => {
    if (onClick) onClick(citationId);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <span className="relative group inline-block align-baseline mx-0.5 transform -translate-y-[1px]">
      <span 
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={handleKeyDown}
        aria-label={`Citation ${citationId}. ${source ? source.document_name : ''}`}
        className="inline-flex items-center justify-center bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[11px] font-bold px-2 py-0.5 rounded-full cursor-pointer hover:bg-indigo-500/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 shadow-sm transition-all duration-200"
      >
        {citationId}
      </span>
      
      {source && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-[250px] opacity-0 group-hover:opacity-100 group-hover:-translate-y-1 translate-y-1 pointer-events-none transition-all duration-200 z-50">
          <div className="bg-slate-800 text-white text-[11px] p-3 rounded-lg border border-slate-700 shadow-xl flex flex-col gap-2">
            <span className="font-semibold truncate block w-full">{source.document_name}</span>
            <div className="flex justify-between items-center text-slate-400 gap-4 mt-1">
              <span className="font-medium">Page {source.page || 'N/A'}</span>
              <span className="text-emerald-400 font-mono bg-emerald-400/10 px-1.5 rounded">{Math.round(source.similarity * 100)}%</span>
            </div>
            {/* Graceful fallback: If we had a short snippet in the metadata, render it here */}
            {/* <div className="text-slate-400 italic mt-1 line-clamp-2">"..."</div> */}
          </div>
        </div>
      )}
    </span>
  );
});
