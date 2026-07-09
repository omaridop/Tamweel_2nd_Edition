import React, { memo } from 'react';

export const TypingSkeleton = memo(() => (
  <div className="flex flex-col gap-3 w-full max-w-[85%] mb-4 ml-12">
    <div className="h-4 bg-slate-700/40 rounded w-3/4 animate-pulse"></div>
    <div className="h-4 bg-slate-700/40 rounded w-full animate-pulse" style={{ animationDelay: '150ms' }}></div>
    <div className="h-4 bg-slate-700/40 rounded w-5/6 animate-pulse" style={{ animationDelay: '300ms' }}></div>
  </div>
));
