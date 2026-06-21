import uuid
import os
import aiofiles
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
from backend.models.schemas import DocumentResponse, UploadResponse
from backend.db.queries import get_all_documents, delete_document_record
from backend.ingestion.extractor import extract_document
from backend.ingestion.chunker import chunk_document
from backend.ingestion.embedder import embed_texts
from backend.ingestion.indexer import index_document

logger = logging.getLogger(__name__)
router = APIRouter()

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Accepts a multipart file upload and triggers the ingestion pipeline.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.pdf', '.docx', '.txt']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use pdf, docx, or txt.")

    doc_id = str(uuid.uuid4())
    temp_file_path = os.path.join(TEMP_DIR, f"{doc_id}{ext}")
    
    try:
        # Save uploaded file temporarily
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            
        file_size_kb = len(content) / 1024
        
        # We can run the ingestion pipeline synchronously or in the background.
        # Running it synchronously for now to immediately return chunk_count,
        # but in a production app with huge files, it should be backgrounded.
        
        # 1. Extract
        with open(temp_file_path, "rb") as f:
            extracted_texts = extract_document(f, file.filename)
            
        # 2. Chunk
        chunks = chunk_document(doc_id, extracted_texts)
        chunk_count = len(chunks)
        
        # 3. Embed
        chunk_texts = [c.text for c in chunks]
        embeddings = embed_texts(chunk_texts)
        
        # 4. Index
        index_document(doc_id, file.filename, ext[1:], file_size_kb, chunks, embeddings)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        return UploadResponse(doc_id=doc_id, chunk_count=chunk_count)
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    """Lists all indexed documents."""
    return get_all_documents()

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Deletes a document from SQLite and ChromaDB."""
    try:
        # Delete from SQLite
        delete_document_record(doc_id)
        
        # Delete from ChromaDB
        from backend.ingestion.indexer import get_collection
        collection = get_collection()
        collection.delete(where={"doc_id": doc_id})
        
        # BM25 is not easily deletable, so we leave it (orphaned tokens won't match existing doc_ids 
        # because the searcher filters by valid doc_ids if needed, or RRF drops them if they 
        # aren't in ChromaDB). Rebuilding BM25 corpus is intensive, so we skip here for performance.
        
        return {"status": "success", "message": f"Document {doc_id} deleted."}
    except Exception as e:
        logger.error(f"Failed to delete document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document.")
