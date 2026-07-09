import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Terminal } from 'lucide-react';
import { WelcomeScreen } from './WelcomeScreen';
import { TypingSkeleton } from './TypingSkeleton';
import { DocumentDrawer } from './DocumentDrawer';
import { ChatMessageItem } from './ChatMessageItem';
import { generateId } from './utils';
import { ChatMessageData, Metric } from './types';
import { fetchWithAuth } from '../../services/api';
import { X } from 'lucide-react';

interface RAGChatWidgetProps {
  onClose?: () => void;
}

export const RAGChatWidget: React.FC<RAGChatWidgetProps> = ({ onClose }) => {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [activePreview, setActivePreview] = useState<{ citationId: string, metric: Metric | null } | null>(null);
  
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Store the latest submitQuery function in a ref for event listeners
  const submitQueryRef = useRef<(queryText: string, isRetry?: boolean) => Promise<void>>();

  const scrollToBottom = useCallback(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessageId, scrollToBottom]);

  useEffect(() => {
    const handleSendChatMessage = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail && customEvent.detail.message) {
        setTimeout(() => {
          if (submitQueryRef.current) {
            submitQueryRef.current(customEvent.detail.message);
          }
        }, 100);
      }
    };
    window.addEventListener('send-chat-message', handleSendChatMessage);
    return () => window.removeEventListener('send-chat-message', handleSendChatMessage);
  }, []);

  const submitQuery = async (queryText: string, isRetry = false) => {
    if (!queryText.trim() || isLoading) return;

    if (!isRetry) {
      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'user',
        text: queryText,
        timestamp: Date.now()
      }]);
    }

    setQuery('');
    setIsLoading(true);

    const agentMsgId = generateId();
    setStreamingMessageId(agentMsgId);

    try {
      const data = await fetchWithAuth('/chat', {
        method: 'POST',
        body: JSON.stringify({
          user_id: 'test_user',
          message: queryText,
          role: 'user',
          history: messages.filter(m => m.role !== 'error').map(m => ({
            role: m.role === 'agent' ? 'assistant' : m.role,
            content: m.text || m.answer || ''
          }))
        })
      });

      const responseText = data.answer || data.response || 'No valid response received.';

      setMessages(prev => {
        // filter out previous errors if this is a retry
        const filtered = isRetry ? prev.filter(m => m.role !== 'error') : prev;
        return [...filtered, {
          id: agentMsgId,
          role: 'agent',
          text: responseText,
          answer: data.answer,
          support_score: data.support_score,
          support_summary: data.support_summary,
          missing_information: data.missing_information,
          sources: data.sources || [],
          retrieval_stats: data.retrieval_stats,
          suggested_followups: data.suggested_followups || [],
          timestamp: Date.now(),
          originalQuery: queryText
        }];
      });
    } catch (err: any) {
      console.error(err);
      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'error',
        text: 'Failed to connect to the Tamweel AI service. Please try again.',
        timestamp: Date.now(),
        originalQuery: queryText
      }]);
    } finally {
      setIsLoading(false);
      setStreamingMessageId(null);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitQuery(query);
  };

  const handleRegenerate = (originalQuery?: string) => {
    if (!originalQuery) return;
    setMessages(prev => {
      const lastUserIdx = prev.map(m => m.role).lastIndexOf('user');
      return lastUserIdx >= 0 ? prev.slice(0, lastUserIdx + 1) : prev;
    });
    submitQuery(originalQuery, true);
  };

  // Update the ref to point to the latest submitQuery
  useEffect(() => {
    submitQueryRef.current = submitQuery;
  });

  const latestAgentIndex = messages.map(m => m.role).lastIndexOf('agent');

  return (
    <div className="flex flex-col h-full bg-[#0b1120] relative w-full border-l border-slate-800">
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-[#0f172a] shadow-sm z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Terminal className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-white font-bold text-sm tracking-tight">Enterprise RAG Assistant</h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></span>
              <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">System Online</span>
            </div>
          </div>
        </div>
        {onClose && (
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-white transition-colors p-1.5 hover:bg-slate-800 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {messages.length === 0 ? (
          <WelcomeScreen onSuggestionClick={submitQuery} />
        ) : (
          <div className="space-y-6 pb-2">
            {messages.map((msg, idx) => (
              <ChatMessageItem 
                key={msg.id}
                message={msg}
                isLatestAgent={idx === latestAgentIndex}
                isStreaming={streamingMessageId === msg.id}
                onRegenerate={() => handleRegenerate(msg.originalQuery)}
                onRetry={() => submitQuery(msg.originalQuery!, true)}
                onCitationClick={(id, metric) => setActivePreview({ citationId: id, metric })}
                onSuggestionClick={(text) => submitQuery(text)}
              />
            ))}
            {isLoading && !streamingMessageId && <TypingSkeleton />}
            <div ref={endOfMessagesRef} className="h-4" />
          </div>
        )}
      </div>

      <div className="p-4 bg-[#0f172a] border-t border-slate-800 shrink-0">
        <form onSubmit={handleSubmit} className="relative w-full max-w-3xl mx-auto flex items-center">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading && !streamingMessageId}
            placeholder="Ask about underwriting policies, limits, or risk guidelines..."
            className="w-full bg-[#1e293b] text-white border border-slate-700 rounded-xl px-4 py-3.5 pr-12 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 placeholder-slate-500 transition-colors shadow-inner"
          />
          <button
            type="submit"
            disabled={!query.trim() || (isLoading && !streamingMessageId)}
            className="absolute right-2 p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 shadow-md"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="text-center mt-3">
          <p className="text-[10px] text-slate-500 font-medium tracking-wide">
            Powered by Tamweel AI • Responses are generated from approved policy documents
          </p>
        </div>
      </div>

      <DocumentDrawer 
        isOpen={activePreview !== null}
        onClose={() => setActivePreview(null)}
        citationId={activePreview?.citationId || ''}
        metric={activePreview?.metric || null}
      />
    </div>
  );
};
