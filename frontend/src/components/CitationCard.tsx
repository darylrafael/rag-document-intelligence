import { Citation } from '../lib/types';
import { BookOpen } from 'lucide-react';

export function CitationCard({ citation, index }: { citation: Citation, index: number }) {
  return (
    <div className="flex flex-col bg-background rounded-md border border-border p-3 text-sm hover:border-primary/50 transition-colors">
      <div className="flex items-center justify-between mb-2 pb-2 border-b border-border/50">
        <div className="flex items-center space-x-2 text-primary font-medium">
          <BookOpen className="w-4 h-4" />
          <span>[SOURCE_{index + 1}]</span>
        </div>
        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
          {citation.page_number && <span>Page {citation.page_number}</span>}
          {citation.relevance_score && (
            <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full">
              Score: {citation.relevance_score.toFixed(2)}
            </span>
          )}
        </div>
      </div>
      <div className="text-foreground italic line-clamp-4">
        "{citation.chunk_text}"
      </div>
    </div>
  );
}
