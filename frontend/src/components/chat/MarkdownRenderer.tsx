import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { remarkHighlightValues } from './remarkHighlightValues';
import { CitationBadge } from './CitationBadge';
import { SourceCitation } from './types';

interface MarkdownRendererProps {
  content: string;
  sources?: SourceCitation[];
  onCitationClick?: (citationId: string) => void;
}

export const MarkdownRenderer = memo(({ content, sources, onCitationClick }: MarkdownRendererProps) => {
  // Pre-process citations in the content for easier rendering: [C1] -> `C1`
  const processedContent = content.replace(/\[(C\d+)\]/g, '`$1`');

  return (
    <ReactMarkdown 
      remarkPlugins={[remarkGfm, remarkHighlightValues]}
      components={{
        code({node, inline, className, children, ...props}: any) {
          const text = String(children).replace(/\n$/, '');
          const citationMatch = /^C\d+$/.exec(text);
          if (inline && citationMatch) {
            return (
              <CitationBadge 
                id={text} 
                onClick={() => onCitationClick && onCitationClick(text)} 
              />
            );
          }
          return <code className={className} {...props}>{children}</code>;
        }
      }}
    >
      {processedContent}
    </ReactMarkdown>
  );
});
