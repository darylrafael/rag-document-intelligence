from sentence_transformers import CrossEncoder
from typing import List, Tuple, Dict
from backend.models.schemas import Chunk
from backend.utils.logger import log_pipeline_stage
import logging

logger = logging.getLogger(__name__)

# Global model variable for caching
_reranker_model = None

def get_reranker_model() -> CrossEncoder:
    global _reranker_model
    if _reranker_model is None:
        logger.info("Loading reranker model: cross-encoder/ms-marco-MiniLM-L-6-v2")
        _reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _reranker_model

@log_pipeline_stage("Reranking")
def rerank_candidates(query: str, chunks: List[Chunk], top_k: int = 5) -> List[Tuple[Chunk, float]]:
    """
    Reranks a list of candidate chunks against the original query using a cross-encoder.
    Returns the top_k chunks along with their cross-encoder scores.
    """
    if not chunks:
        return []
        
    model = get_reranker_model()
    
    # Prepare pairs of (query, chunk_text)
    pairs = [(query, chunk.text) for chunk in chunks]
    
    # Get scores
    scores = model.predict(pairs)
    
    # Pair up chunks with their scores
    scored_chunks = list(zip(chunks, scores))
    
    # Sort by score descending
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    # Return top_k
    return scored_chunks[:top_k]
