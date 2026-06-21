import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';
import { DocumentResponse } from '../lib/types';

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await api.documents.list();
      setDocuments(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch documents');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const uploadDocument = async (file: File) => {
    try {
      await api.documents.upload(file);
      await fetchDocuments();
      return true;
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      return false;
    }
  };

  const deleteDocument = async (docId: string) => {
    try {
      await api.documents.delete(docId);
      await fetchDocuments();
    } catch (err: any) {
      setError(err.message || 'Delete failed');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return { documents, isLoading, error, uploadDocument, deleteDocument, refresh: fetchDocuments };
}
