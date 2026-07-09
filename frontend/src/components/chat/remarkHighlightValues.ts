import { visit } from 'unist-util-visit';
import type { Plugin } from 'unified';
import type { Node, Parent } from 'unist';

// Custom Type Guard for Text nodes
interface TextNode extends Node {
  type: 'text';
  value: string;
}
interface ElementNode extends Parent {
  type: string;
  data?: {
    hName?: string;
    hProperties?: Record<string, any>;
  };
}

export const remarkHighlightValues: Plugin = () => {
  return (tree) => {
    visit(tree, 'text', (node: Node, index: number | undefined, parent: Parent | undefined) => {
      // Safely narrow node to TextNode
      if (node.type !== 'text' || !parent) return;
      const textNode = node as TextNode;
      
      // Skip code blocks and headings to preserve structural integrity
      if (['code', 'heading', 'strong', 'em', 'link'].includes(parent.type)) return;

      const regex = /\b(\d+(?:,\d{3})*(?:\.\d+)?\s*(?:JOD|USD|%|percent))\b|\b(\d+\s*(?:months?|years?|days?|weeks?))\b|\b(\d{1,4}[-/]\d{1,2}[-/]\d{1,4})\b/gi;
      const text = textNode.value;
      if (!text.match(regex)) return;

      const newNodes: Node[] = [];
      let lastIndex = 0;
      let match;
      regex.lastIndex = 0;

      while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
          newNodes.push({ type: 'text', value: text.slice(lastIndex, match.index) });
        }
        
        // Wrap the matched value in an AST node that will render as <mark>
        const markNode: ElementNode = {
          type: 'strong', // Fallback for pure markdown environments
          data: {
            hName: 'mark',
            hProperties: { className: 'highlight-value bg-indigo-500/15 text-indigo-300 font-semibold px-1 rounded shadow-sm' }
          },
          children: [{ type: 'text', value: match[0] }]
        };
        newNodes.push(markNode);
        lastIndex = regex.lastIndex;
      }
      
      if (lastIndex < text.length) {
        newNodes.push({ type: 'text', value: text.slice(lastIndex) });
      }
      
      if (index !== undefined) {
        parent.children.splice(index, 1, ...newNodes);
        return index + newNodes.length;
      }
    });
  };
};
