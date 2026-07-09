import React, { memo, useCallback } from 'react';
import { User, ShieldCheck, AlertCircle } from 'lucide-react';
import { ChatMessageData, Metric } from './types';
import { ProgressiveText } from './ProgressiveText';
import { MarkdownRenderer } from './MarkdownRenderer';
import { SourcesPanel } from './SourcesPanel';
import { MessageActionBar } from './MessageActionBar';
import { ConfidenceWidget } from './ConfidenceWidget';

interface ChatMessageItemProps {
  message: ChatMessageData;
  isLatestAgent: boolean;
  isStreaming: boolean;
  onRegenerate?: () => void;
  onRetry?: () => void;
  onCitationClick?: (citationId: string, metric: Metric | null) => void;
  onSuggestionClick?: (text: string) => void;
}

export const ChatMessageItem = memo(({ 
  message, 
  isLatestAgent, 
  isStreaming,
  onRegenerate,
  onRetry,
  onCitationClick,
  onSuggestionClick
}: ChatMessageItemProps) => {
  const isUser = message.role === 'user';
  const isError = message.role === 'error';

  const handleCitationClick = useCallback((citationId: string) => {
    if (onCitationClick) {
      const source = message.sources?.find(s => s.id === citationId);
      let metric: Metric | null = null;
      if (source) {
        metric = {
          id: source.id,
          source: source.document_name,
          page: source.page ? source.page.toString() : 'N/A',
          score: source.similarity.toFixed(4),
          reason: 'Source identified by semantic similarity search.'
        };
      }
      onCitationClick(citationId, metric);
    }
  }, [onCitationClick, message.sources]);

  return (
    <div className={`flex flex-col w-full gap-2`} dir="auto">
      <div className={`flex w-full gap-4 group ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className="shrink-0 mt-1">
          {isUser ? (
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shadow-md border border-indigo-500/30">
              <User size={16} className="text-white" />
            </div>
          ) : (
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shadow-md border ${isError ? 'bg-red-500/20 border-red-500/50' : 'bg-[#0f172a] border-slate-700'}`}>
              {isError ? <AlertCircle size={16} className="text-red-400" /> : <ShieldCheck size={16} className="text-indigo-400" />}
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col max-w-3xl w-full ${isUser ? 'items-end' : 'items-start'}`}>
          <div 
            className={`p-5 rounded-2xl ${
              isUser 
                ? 'bg-indigo-600 text-white rounded-tr-sm shadow-lg shadow-indigo-900/20' 
                : isError
                  ? 'bg-red-500/10 text-red-200 border border-red-500/30 rounded-tl-sm w-full'
                  : 'bg-[#1e293b]/80 border border-slate-700/50 text-slate-200 rounded-tl-sm shadow-md w-full backdrop-blur-sm'
            }`}
          >
            {isUser ? (
              <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</div>
            ) : isError ? (
              <div className="text-sm leading-relaxed flex items-center gap-2">
                <AlertCircle size={18} className="text-red-400 shrink-0" />
                {message.text}
              </div>
            ) : (
              <div className="w-full flex flex-col">
                <div className="w-full markdown-body mb-2">
                  {isStreaming ? (
                    <ProgressiveText 
                      text={message.answer || message.text} 
                      onCitationClick={handleCitationClick} 
                    />
                  ) : (
                    <MarkdownRenderer 
                      content={message.answer || message.text}
                      onCitationClick={handleCitationClick}
                    />
                  )}
                </div>
                
                {!isStreaming && (
                  <ConfidenceWidget score={message.support_score} />
                )}

                {!isStreaming && message.support_summary && (
                  <div className="mt-2 text-xs bg-slate-800/40 border border-slate-700 p-3 rounded-lg text-slate-300">
                    <span className="font-bold text-slate-400 block mb-1">Support Summary</span>
                    {message.support_summary}
                  </div>
                )}
                
                {!isStreaming && message.missing_information && message.missing_information.toLowerCase() !== 'none' && (
                  <div className="mt-2 text-xs bg-amber-500/10 border border-amber-500/30 p-3 rounded-lg text-amber-200">
                    <span className="font-bold text-amber-500 block mb-1">Missing Information</span>
                    {message.missing_information}
                  </div>
                )}

                {!isStreaming && <SourcesPanel message={message} />}
              </div>
            )}
          </div>
          
          <MessageActionBar 
            message={message} 
            onRegenerate={isLatestAgent ? onRegenerate : undefined} 
            onRetry={isError ? onRetry : undefined} 
          />
        </div>
      </div>
      
      {/* Suggested Follow-ups */}
      {!isStreaming && message.role === 'agent' && message.suggested_followups && message.suggested_followups.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3 ml-12 pl-1">
          {message.suggested_followups.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => onSuggestionClick && onSuggestionClick(suggestion)}
              className="bg-slate-800/80 hover:bg-indigo-500/20 text-slate-300 hover:text-indigo-300 border border-slate-700 hover:border-indigo-500/30 px-3 py-1.5 rounded-full text-[11px] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
});
