import React, { useCallback, useState } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

export function UploadZone({ onUpload }: { onUpload: (file: File) => Promise<boolean> }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFile = async (file: File) => {
    if (!file) return;
    setIsUploading(true);
    setUploadStatus('idle');
    const success = await onUpload(file);
    setIsUploading(false);
    setUploadStatus(success ? 'success' : 'error');
    if (success) {
      setTimeout(() => setUploadStatus('idle'), 3000);
    }
  };

  const onDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      await handleFile(file);
    }
  }, [onUpload]);

  return (
    <div 
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={cn(
        "relative flex flex-col items-center justify-center w-full h-64 rounded-xl border-2 border-dashed transition-all duration-300",
        isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-card/50",
        isUploading && "opacity-50 pointer-events-none"
      )}
    >
      <input 
        type="file" 
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
        accept=".pdf,.docx,.txt"
      />
      <div className="flex flex-col items-center justify-center space-y-4 text-center p-6">
        <motion.div
          animate={{ y: isDragging ? -10 : 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          {uploadStatus === 'success' ? (
            <CheckCircle2 className="w-12 h-12 text-green-500" />
          ) : uploadStatus === 'error' ? (
            <AlertCircle className="w-12 h-12 text-destructive" />
          ) : (
            <UploadCloud className={cn("w-12 h-12 transition-colors", isDragging ? "text-primary" : "text-muted-foreground")} />
          )}
        </motion.div>
        <div>
          <p className="text-lg font-medium text-foreground">
            {isUploading ? 'Uploading...' : 'Click or drag file to upload'}
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            Supports PDF, DOCX, and TXT files
          </p>
        </div>
      </div>
    </div>
  );
}
