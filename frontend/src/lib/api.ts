import { DocumentResponse, QueryResponse, QueryHistoryResponse, AnalyticsStatsResponse } from './types';

// On Windows, 'localhost' can resolve to IPv6 (::1) while uvicorn listens on IPv4 (127.0.0.1).
// Using '127.0.0.1' directly prevents 'Failed to fetch' connection errors.
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const api = {
    documents: {
        list: async (): Promise<DocumentResponse[]> => {
            const res = await fetch(`${API_BASE_URL}/documents`);
            if (!res.ok) throw new Error('Failed to fetch documents');
            return res.json();
        },
        upload: async (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            const res = await fetch(`${API_BASE_URL}/documents/upload`, {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) throw new Error('Upload failed');
            return res.json();
        },
        delete: async (docId: string) => {
            const res = await fetch(`${API_BASE_URL}/documents/${docId}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Delete failed');
            return res.json();
        }
    },
    query: {
        execute: async (question: string, topK: number = 5, docIds?: string[]): Promise<QueryResponse> => {
            const res = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, top_k: topK, doc_ids: docIds })
            });
            if (!res.ok) throw new Error('Query failed');
            return res.json();
        }
    },
    analytics: {
        getHistory: async (page = 1, size = 20): Promise<QueryHistoryResponse> => {
            const res = await fetch(`${API_BASE_URL}/analytics/queries?page=${page}&size=${size}`);
            if (!res.ok) throw new Error('Failed to fetch history');
            return res.json();
        },
        getStats: async (): Promise<AnalyticsStatsResponse> => {
            const res = await fetch(`${API_BASE_URL}/analytics/stats`);
            if (!res.ok) throw new Error('Failed to fetch stats');
            return res.json();
        }
    }
};
