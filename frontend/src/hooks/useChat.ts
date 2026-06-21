import { useState } from 'react';
import { api } from '../lib/api';
import { QueryResponse } from '../lib/types';

export function useChat() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, response?: QueryResponse }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (question: string, topK: number = 5, docIds?: string[]) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Optimistically add user message
      setMessages(prev => [...prev, { role: 'user', content: question }]);
      
      const res = await api.query.execute(question, topK, docIds);
      
      setMessages(prev => [...prev, { role: 'assistant', content: res.answer, response: res }]);
      return res;
    } catch (err: any) {
      setError(err.message || 'Query failed');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => setMessages([]);

  return { messages, isLoading, error, sendMessage, clearChat };
}
