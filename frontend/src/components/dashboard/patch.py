import re

with open('frontend/src/components/dashboard/RAGChatWidget.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace ChatMessageData
old_types = '''interface ChatMessageData {
  id: string;
  role: MessageRole;
  text: string;
  timestamp: number;
  originalQuery?: string;
}'''
new_types = '''interface SourceCitation {
  id: string;
  document_name: string;
  page: number | null;
  similarity: number;
}

interface ChatMessageData {
  id: string;
  role: MessageRole;
  text: string;
  answer?: string;
  confidence?: string;
  confidence_score?: number | null;
  sources?: SourceCitation[];
  retrieval_stats?: {
    chunks_retrieved: number;
    chunks_used: number;
    generation_time_ms: number;
  };
  suggested_followups?: string[];
  timestamp: number;
  originalQuery?: string;
}'''
content = content.replace(old_types, new_types)

# 2. Replace TrustCard with SourcesAndDetails
trust_card_pattern = re.compile(r'// 2\. Trust Card\nconst TrustCard = memo\(\(\{ trustContent \}: \{ trustContent: string \}\) => \{.*?\n\}\);\n', re.DOTALL)
new_sources_and_details = r'''// 2. Sources and Details Card
const SourcesAndDetails = memo(({ message }: { message: ChatMessageData }) => {
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
'''
content = trust_card_pattern.sub(lambda m: new_sources_and_details, content)

# 3. Replace ChatMessageItem
chat_msg_item_pattern = re.compile(r'// 7\. Chat Message Wrapper\nconst ChatMessageItem = memo\(\(\{.*?\n\}\);\n', re.DOTALL)
new_chat_msg_item = r'''// 7. Chat Message Wrapper
const ChatMessageItem = memo(({ 
  message, 
  isLatestAgent, 
  isStreaming,
  onRegenerate,
  onRetry,
  onCitationClick,
  onSuggestionClick
}: { 
  message: ChatMessageData, 
  isLatestAgent: boolean, 
  isStreaming: boolean,
  onRegenerate?: () => void,
  onRetry?: () => void,
  onCitationClick?: (citationId: string, metric: Metric | null) => void,
  onSuggestionClick?: (text: string) => void
}) => {
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

  const getConfidenceColor = (conf: string) => {
    if (conf === 'high') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (conf === 'medium') return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    if (conf === 'low') return 'text-red-400 bg-red-500/10 border-red-500/30';
    return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
  };

  const confidenceScoreLabel = message.confidence_score ? ` (${Math.round(message.confidence_score * 100)}%)` : '';

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
                    <ProgressiveText text={message.answer || message.text} onCitationClick={handleCitationClick} />
                  ) : (
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={getMarkdownComponents(handleCitationClick)}>
                      {(message.answer || message.text).replace(/\[(C\d+)\]/g, '`$1`')}
                    </ReactMarkdown>
                  )}
                </div>
                
                {!isStreaming && message.confidence && (
                  <div className="flex items-center mt-2 mb-2">
                    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-bold uppercase tracking-wider ${getConfidenceColor(message.confidence)}`}>
                      <div className="w-1.5 h-1.5 rounded-full bg-current" />
                      {message.confidence} Confidence{confidenceScoreLabel}
                    </div>
                  </div>
                )}
                
                {!isStreaming && <SourcesAndDetails message={message} />}
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
'''
content = chat_msg_item_pattern.sub(lambda m: new_chat_msg_item, content)

# 4. Modify RAGChatWidget to pass onSuggestionClick
old_chat_msg_render = '''<ChatMessageItem 
                      message={msg} 
                      isLatestAgent={isLatestAgent}
                      isStreaming={streamingMessageId === msg.id}
                      onRegenerate={() => handleRegenerate(msg.originalQuery)}
                      onRetry={() => submitQuery(msg.originalQuery!, true)}
                      onCitationClick={(id, metric) => setActivePreview({ citationId: id, metric })}
                    />'''
new_chat_msg_render = '''<ChatMessageItem 
                      message={msg} 
                      isLatestAgent={isLatestAgent}
                      isStreaming={streamingMessageId === msg.id}
                      onRegenerate={() => handleRegenerate(msg.originalQuery)}
                      onRetry={() => submitQuery(msg.originalQuery!, true)}
                      onCitationClick={(id, metric) => setActivePreview({ citationId: id, metric })}
                      onSuggestionClick={(text) => submitQuery(text)}
                    />'''
content = content.replace(old_chat_msg_render, new_chat_msg_render)

# 5. Update fetch in submitQuery
old_fetch = '''const data = await fetchWithAuth('/chat', {
        method: 'POST',
        body: JSON.stringify({
          user_id: 'test_user',
          message: queryText,
          role: 'user',
          history: messages.filter(m => m.role !== 'error').map(m => ({
            role: m.role === 'agent' ? 'assistant' : m.role,
            content: m.text
          }))
        })
      });
      
      const responseText = data.response || 'No valid response received.';'''
      
new_fetch = '''const data = await fetchWithAuth('/rag/chat', {
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
      
      const responseText = data.answer || data.response || 'No valid response received.';'''
content = content.replace(old_fetch, new_fetch)

# 6. Update setMessages in submitQuery
old_set_msgs = '''setMessages(prev => [...prev, { 
        id: agentMsgId,
        role: 'agent', 
        text: responseText,
        timestamp: Date.now(),
        originalQuery: queryText
      }]);'''
new_set_msgs = '''setMessages(prev => [...prev, { 
        id: agentMsgId,
        role: 'agent', 
        text: responseText,
        answer: data.answer,
        confidence: data.confidence,
        confidence_score: data.confidence_score,
        sources: data.sources || [],
        retrieval_stats: data.retrieval_stats,
        suggested_followups: data.suggested_followups || [],
        timestamp: Date.now(),
        originalQuery: queryText
      }]);'''
content = content.replace(old_set_msgs, new_set_msgs)

with open('frontend/src/components/dashboard/RAGChatWidget.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('File updated successfully.')
