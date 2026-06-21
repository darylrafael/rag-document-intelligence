from typing import List, Dict, Tuple
from collections import defaultdict
from backend.ingestion.embedder import embed_texts
from backend.ingestion.indexer import get_collection, _load_bm25_corpus, BM25_INDEX_PATH
from backend.models.schemas import Chunk, ChunkMetadata
from backend.utils.logger import log_pipeline_stage
from nltk.tokenize import word_tokenize
import pickle
import logging

logger = logging.getLogger(__name__)

def get_bm25_data():
    try:
        with open(BM25_INDEX_PATH, "rb") as f:
            data = pickle.load(f)
            return data["index"], data["chunk_ids"]
    except Exception as e:
        logger.warning(f"Failed to load BM25 index: {e}")
        return None, []

def reciprocal_rank_fusion(ranked_lists: List[List[str]], k: int = 60) -> List[Tuple[str, float]]:
    """
    Combines multiple ranked lists using Reciprocal Rank Fusion (RRF).
    Returns a sorted list of (chunk_id, rrf_score).
    """
    rrf_scores = defaultdict(float)
    
    for ranked_list in ranked_lists:
        for rank, chunk_id in enumerate(ranked_list, start=1):
            rrf_scores[chunk_id] += 1.0 / (k + rank)
            
    # Sort by descending score
    sorted_scores = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores

@log_pipeline_stage("Hybrid Search")
def hybrid_search(original_query: str, expanded_queries: List[str], doc_ids: List[str] = None) -> List[Tuple[str, float]]:
    """
    Executes semantic search for all queries and keyword search for original query.
    Merges results via RRF and returns the top 20 candidates.
    Returns: List of (chunk_id, rrf_score)
    """
    # 1. Semantic Search
    collection = get_collection()
    semantic_ranked_lists = []
    
    all_queries = [original_query] + expanded_queries
    query_embeddings = embed_texts(all_queries)
    
    where_clause = None
    if doc_ids:
        if len(doc_ids) == 1:
            where_clause = {"doc_id": doc_ids[0]}
        else:
            where_clause = {"doc_id": {"$in": doc_ids}}
    
    # Query ChromaDB (top 10 per query)
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=10,
        where=where_clause
    )
    
    # results["ids"] is a list of lists, one per query
    for ids_list in results["ids"]:
        semantic_ranked_lists.append(ids_list)
        
    # 2. Keyword Search (BM25)
    keyword_ranked_list = []
    bm25_index, chunk_ids_map = get_bm25_data()
    
    if bm25_index and chunk_ids_map:
        tokenized_query = word_tokenize(original_query.lower())
        # Get scores
        scores = bm25_index.get_scores(tokenized_query)
        
        # Sort indices by score descending
        # Zip with chunk_ids_map and sort
        scored_chunks = list(zip(chunk_ids_map, scores))
        
        # If doc filtering is needed, filter here
        if doc_ids:
            # chunk_id format is "{doc_id}_{chunk_index}"
            # Extract actual_doc_id by splitting on the LAST underscore
            scored_chunks = [sc for sc in scored_chunks if "_".join(sc[0].split("_")[:-1]) in doc_ids]
            
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        # Take top 10 non-zero scored chunks
        top_keyword = [sc[0] for sc in scored_chunks[:10] if sc[1] > 0]
        keyword_ranked_list = top_keyword

    # 3. Merge via RRF
    all_ranked_lists = semantic_ranked_lists + [keyword_ranked_list]
    merged_results = reciprocal_rank_fusion(all_ranked_lists, k=60)
    
    # Return top 20
    return merged_results[:20]

def fetch_chunks_by_ids(chunk_ids: List[str]) -> List[Chunk]:
    """Fetches full chunk data from ChromaDB given a list of chunk IDs."""
    if not chunk_ids:
        return []
        
    collection = get_collection()
    results = collection.get(ids=chunk_ids)
    
    chunks = []
    # Rebuild Chunks
    for i in range(len(results["ids"])):
        c_id = results["ids"][i]
        text = results["documents"][i]
        meta = results["metadatas"][i]
        
        chunks.append(
            Chunk(
                text=text,
                metadata=ChunkMetadata(**meta)
            )
        )
    return chunks
