"use client";
import { UploadZone } from '../components/UploadZone';
import { DocumentCard } from '../components/DocumentCard';
import { useDocuments } from '../hooks/useDocuments';

export default function Dashboard() {
  const { documents, isLoading, error, uploadDocument, deleteDocument } = useDocuments();

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Document Library</h1>
        <p className="text-muted-foreground mt-2">Manage your knowledge base for the RAG system.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <h2 className="text-xl font-semibold mb-4">Upload</h2>
          <UploadZone onUpload={uploadDocument} />
          {error && <p className="text-destructive text-sm mt-2">{error}</p>}
        </div>

        <div className="md:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Indexed Documents ({documents.length})</h2>
          
          {isLoading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-20 bg-muted/50 rounded-lg"></div>
              ))}
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center p-12 border-2 border-dashed border-border rounded-xl">
              <p className="text-muted-foreground">No documents uploaded yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((doc) => (
                <DocumentCard key={doc.id} doc={doc} onDelete={deleteDocument} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
