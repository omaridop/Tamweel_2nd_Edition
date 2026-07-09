export type MessageRole = 'user' | 'agent' | 'system' | 'error';

export interface SourceCitation {
  id: string;
  document_name: string;
  page: number | null;
  similarity: number;
}

export interface Metric {
  id: string;
  source: string;
  page: string;
  score: string;
  reason: string;
}

export interface RetrievalStats {
  chunks_retrieved: number;
  chunks_used: number;
  generation_time_ms: number;
}

export interface ChatMessageData {
  id: string;
  role: MessageRole;
  text: string;
  answer?: string;
  support_score?: number;
  support_summary?: string;
  missing_information?: string;
  sources?: SourceCitation[];
  retrieval_stats?: RetrievalStats;
  suggested_followups?: string[];
  timestamp: number;
  originalQuery?: string;
}
