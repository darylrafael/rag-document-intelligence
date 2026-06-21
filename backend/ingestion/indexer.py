import os
import pickle
import chromadb
from rank_bm25 import BM25Okapi
from typing import List, Dict
from backend.models.schemas import Chunk
from backend.db.queries import insert_document
from backend.utils.logger import log_pipeline_stage
import logging

logger = logging.getLogger(__name__)

DB_DIR = os.environ.get("CHROMA_DB_DIR", "./chroma_data")
BM25_CORPUS_PATH = os.path.join(DB_DIR, "bm25_corpus.pkl")
BM25_INDEX_PATH = os.path.join(DB_DIR, "bm25_index.pkl")

# Initialize ChromaDB client
os.makedirs(DB_DIR, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=DB_DIR)

def get_collection():
    return chroma_client.get_or_create_collection(
        name="document_chunks",
        metadata={"hnsw:space": "cosine"}
    )

def _load_bm25_corpus() -> Dict[str, List[str]]:
    """Loads the existing chunk_id -> tokenized text mapping."""
    if os.path.exists(BM25_CORPUS_PATH):
        try:
            with open(BM25_CORPUS_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load BM25 corpus: {e}")
    return {}

def _save_bm25(corpus_dict: Dict[str, List[str]]):
    """Saves the corpus dict and builds/saves the BM25 index."""
    # Build ordered lists
    chunk_ids = list(corpus_dict.keys())
    tokenized_texts = list(corpus_dict.values())
    
    # Build index
    if tokenized_texts:
        bm25_index = BM25Okapi(tokenized_texts)
    else:
        bm25_index = None
        
    # Save corpus dict
    with open(BM25_CORPUS_PATH, "wb") as f:
        pickle.dump(corpus_dict, f)
        
    # Save index & chunk_ids map so searcher knows which chunk_id corresponds to which index
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({"index": bm25_index, "chunk_ids": chunk_ids}, f)

@log_pipeline_stage("Indexing")
def index_document(doc_id: str, filename: str, file_type: str, file_size_kb: float, 
                   chunks: List[Chunk], embeddings: List[List[float]]):
    """
    Indexes the document into SQLite, ChromaDB, and BM25.
    """
    if not chunks:
        logger.warning(f"No chunks to index for document {doc_id}")
        return

    # 1. SQLite Document Record
    insert_document(
        doc_id=doc_id, 
        filename=filename, 
        file_type=file_type, 
        chunk_count=len(chunks), 
        file_size_kb=file_size_kb
    )
    
    # 2. ChromaDB
    collection = get_collection()
    
    ids = [c.metadata.chunk_id for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [c.metadata.model_dump(exclude_none=True) for c in chunks]
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    # 3. BM25
    # Tokenization approach: simple lowercase split. 
    # For a production system, a better tokenizer (like NLTK or Spacy) is preferred, 
    # but basic splitting is often sufficient for keyword paths.
    corpus_dict = _load_bm25_corpus()
    for c in chunks:
        tokens = c.text.lower().split()
        corpus_dict[c.metadata.chunk_id] = tokens
        
    _save_bm25(corpus_dict)
    
    logger.info(f"Indexed {len(chunks)} chunks for document {doc_id}")
