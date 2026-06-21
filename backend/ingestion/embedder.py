from sentence_transformers import SentenceTransformer
from typing import List
from backend.utils.logger import log_pipeline_stage
import logging

logger = logging.getLogger(__name__)

# Global model variable for caching
_embedder_model = None

def get_embedder_model() -> SentenceTransformer:
    global _embedder_model
    if _embedder_model is None:
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _embedder_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedder_model

@log_pipeline_stage("Embedding")
def embed_texts(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Generates normalized embeddings for a list of texts in batches.
    """
    if not texts:
        return []
    
    model = get_embedder_model()
    # encode returns a numpy array. We need a list of lists of floats.
    embeddings = model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
    
    return embeddings.tolist()
