"use client";
import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Settings2 } from 'lucide-react';
import { ChatMessage } from '../../components/ChatMessage';
import { useChat } from '../../hooks/useChat';
import { cn } from '../../lib/utils';

export default function ChatInterface() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();
  const [input, setInput] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const query = input;
    setInput('');
    await sendMessage(query);
  };

  return (
    <div className="flex flex-col h-full relative max-h-screen">
      <div className="flex items-center justify-between p-4 border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-10">
        <div>
          <h1 className="text-xl font-bold">Query Engine</h1>
          <p className="text-xs text-muted-foreground">Ask questions against your document library</p>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={clearChat}
            className="p-2 text-muted-foreground hover:bg-muted rounded-md transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 md:p-8">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                <Settings2 className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">How can I help you today?</h3>
                <p className="text-muted-foreground mt-2 max-w-sm">
                  I can search through your indexed documents and provide answers with precise citations.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg, idx) => (
                <ChatMessage 
                  key={idx} 
                  role={msg.role} 
                  content={msg.content} 
                  response={msg.response} 
                />
              ))}
              {isLoading && (
                <div className="flex items-center space-x-2 text-muted-foreground ml-14">
                  <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              )}
              {error && (
                <div className="p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive/20 ml-14">
                  {error}
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}
        </div>
      </div>

      <div className="p-4 bg-background/80 backdrop-blur-md border-t border-border">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="w-full bg-card border border-border rounded-full pl-6 pr-14 py-4 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              "absolute right-2 top-2 bottom-2 p-2 rounded-full transition-colors flex items-center justify-center",
              input.trim() && !isLoading ? "bg-primary text-primary-foreground hover:bg-primary/90" : "bg-muted text-muted-foreground"
            )}
          >
            <Send className="w-5 h-5 ml-0.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
