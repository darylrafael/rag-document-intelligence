import { User, Bot, AlertTriangle, Clock } from 'lucide-react';
import { cn } from '../lib/utils';
import { QueryResponse } from '../lib/types';
import { CitationCard } from './CitationCard';
import { motion } from 'framer-motion';

export function ChatMessage({ role, content, response }: { role: 'user' | 'assistant', content: string, response?: QueryResponse }) {
  
  // A simple function to bold citation tags like [SOURCE_1]
  const renderContent = (text: string) => {
    const parts = text.split(/(\[SOURCE_\d+\])/g);
    return parts.map((part, i) => {
      if (part.match(/\[SOURCE_\d+\]/)) {
        return <span key={i} className="text-primary font-bold cursor-help" title="Citation reference">{part}</span>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex w-full space-x-4 mb-6", role === 'user' ? "justify-end" : "justify-start")}
    >
      {role === 'assistant' && (
        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-1">
          <Bot className="w-5 h-5 text-primary" />
        </div>
      )}
      
      <div className={cn(
        "max-w-[80%] rounded-2xl px-5 py-4",
        role === 'user' ? "bg-primary text-primary-foreground rounded-tr-sm" : "bg-card border border-border text-foreground rounded-tl-sm shadow-sm"
      )}>
        <div className="leading-relaxed whitespace-pre-wrap">
          {renderContent(content)}
        </div>
        
        {response?.warning && (
          <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-start space-x-2 text-sm text-destructive">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{response.warning}</span>
          </div>
        )}

        {response?.citations && response.citations.length > 0 && (
          <div className="mt-6 pt-4 border-t border-border/50">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Sources Cited</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {response.citations.map((cit, i) => (
                <CitationCard key={i} citation={cit} index={i} />
              ))}
            </div>
          </div>
        )}

        {response?.timing && (
          <div className="mt-4 flex items-center space-x-2 text-xs text-muted-foreground opacity-60">
            <Clock className="w-3 h-3" />
            <span>{(response.timing.total_ms / 1000).toFixed(2)}s generation</span>
            <span className="bg-background px-1.5 py-0.5 rounded text-[10px] font-mono">Conf: {response.confidence_score}/100</span>
          </div>
        )}
      </div>

      {role === 'user' && (
        <div className="w-8 h-8 rounded-full bg-accent text-accent-foreground flex items-center justify-center shrink-0 mt-1">
          <User className="w-5 h-5" />
        </div>
      )}
    </motion.div>
  );
}
