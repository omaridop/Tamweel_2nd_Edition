import React, { memo, useEffect, useState, useRef } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { SourceCitation } from './types';

interface ProgressiveTextProps {
  text: string;
  sources?: SourceCitation[];
  onCitationClick?: (citationId: string) => void;
}

export const ProgressiveText = memo(({ text, sources, onCitationClick }: ProgressiveTextProps) => {
  const [displayedText, setDisplayedText] = useState(text);
  const textRef = useRef(text);

  useEffect(() => {
    if (text !== textRef.current) {
      setDisplayedText(text);
      textRef.current = text;
    }
  }, [text]);

  return (
    <div className="progressive-text">
      <MarkdownRenderer 
        content={displayedText} 
        sources={sources} 
        onCitationClick={onCitationClick} 
      />
      <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-400 animate-pulse align-middle" />
    </div>
  );
});
