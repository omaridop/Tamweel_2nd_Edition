import React, { memo, useState } from 'react';
import { Copy, Check, RotateCcw, RefreshCw } from 'lucide-react';
import { formatTime } from './utils';
import { ChatMessageData } from './types';

interface MessageActionBarProps {
  message: ChatMessageData;
  onRegenerate?: () => void;
  onRetry?: () => void;
}

export const MessageActionBar = memo(({ message, onRegenerate, onRetry }: MessageActionBarProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    // Strip markdown formatting for pure text payload
    const pureText = message.text.replace(/\*\*/g, '').trim();
    navigator.clipboard.writeText(pureText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-1 mt-2 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
      <span className="text-[10px] mr-2 opacity-50 font-medium">{formatTime(message.timestamp)}</span>
      
      {message.role === 'agent' && (
        <button onClick={handleCopy} className="p-1 hover:text-slate-300 hover:bg-slate-700/50 rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-500" title="Copy message" aria-label="Copy message">
          {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
        </button>
      )}
      
      {message.role === 'agent' && onRegenerate && (
        <button onClick={onRegenerate} className="p-1 hover:text-slate-300 hover:bg-slate-700/50 rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-500" title="Regenerate response" aria-label="Regenerate response">
          <RotateCcw size={12} />
        </button>
      )}

      {message.role === 'error' && onRetry && (
        <button onClick={onRetry} className="p-1 hover:text-slate-300 hover:bg-slate-700/50 rounded transition-colors flex items-center gap-1 text-[11px] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-500" title="Retry request" aria-label="Retry request">
          <RefreshCw size={12} /> Retry
        </button>
      )}
    </div>
  );
});
