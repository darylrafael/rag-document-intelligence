import time
import uuid
from fastapi import APIRouter, HTTPException
from backend.models.schemas import QueryRequest, QueryResponse, PipelineTiming
from backend.retrieval.expander import expand_query
from backend.retrieval.searcher import hybrid_search, fetch_chunks_by_ids
from backend.retrieval.reranker import rerank_candidates
from backend.generation.generator import generate_answer
from backend.generation.validator import validate_generation
from backend.db.queries import record_query
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=QueryResponse)
async def execute_query(req: QueryRequest):
    """
    Executes the full RAG pipeline: Expansion -> Retrieval -> Reranking -> Generation -> Validation.
    """
    start_total = time.perf_counter()
    timing = PipelineTiming()
    
    try:
        # 1. Expansion
        t0 = time.perf_counter()
        expanded_queries = await expand_query(req.question)
        timing.expansion_ms = (time.perf_counter() - t0) * 1000
        
        # 2. Retrieval
        t0 = time.perf_counter()
        merged_results = hybrid_search(req.question, expanded_queries, doc_ids=req.doc_ids)
        
        chunk_ids = [res[0] for res in merged_results]
        candidate_chunks = fetch_chunks_by_ids(chunk_ids)
        timing.retrieval_ms = (time.perf_counter() - t0) * 1000
        
        # 3. Reranking
        t0 = time.perf_counter()
        reranked_results = rerank_candidates(req.question, candidate_chunks, top_k=req.top_k)
        timing.reranking_ms = (time.perf_counter() - t0) * 1000
        
        # 4. Generation & Validation
        t0 = time.perf_counter()
        gen_result = await generate_answer(req.question, reranked_results)
        
        val_result = validate_generation(gen_result.answer)
        confidence_score = val_result.confidence_score
        
        timing.generation_ms = (time.perf_counter() - t0) * 1000
        timing.total_ms = (time.perf_counter() - start_total) * 1000
        
        # 5. Record Query in DB
        query_id = str(uuid.uuid4())
        referenced_doc_ids = [c.doc_id for c in gen_result.citations]
        record_query(query_id, req.question, confidence_score, referenced_doc_ids)
        
        return QueryResponse(
            answer=gen_result.answer,
            citations=gen_result.citations,
            confidence_score=confidence_score,
            warning=val_result.warning,
            timing=timing
        )
        
    except Exception as e:
        logger.error(f"Query pipeline failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing failed.")
