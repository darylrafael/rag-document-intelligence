import { FileText, Trash2 } from 'lucide-react';
import { DocumentResponse } from '../lib/types';
import { formatDistanceToNow } from 'date-fns';

export function DocumentCard({ doc, onDelete }: { doc: DocumentResponse, onDelete: (id: string) => void }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-card border border-border hover:border-primary/30 transition-colors">
      <div className="flex items-center space-x-4">
        <div className="p-3 rounded-full bg-primary/10 text-primary">
          <FileText className="w-6 h-6" />
        </div>
        <div>
          <h4 className="text-sm font-medium text-foreground line-clamp-1" title={doc.filename}>{doc.filename}</h4>
          <p className="text-xs text-muted-foreground mt-1">
            {doc.file_size_kb.toFixed(1)} KB • {doc.chunk_count} chunks • Added {formatDistanceToNow(new Date(doc.indexed_at))} ago
          </p>
        </div>
      </div>
      <button 
        onClick={() => onDelete(doc.id)}
        className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors"
        title="Delete document"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  );
}
