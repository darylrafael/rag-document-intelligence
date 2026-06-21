import pytest
from backend.retrieval.reranker import rerank_candidates
from backend.models.schemas import Chunk, ChunkMetadata

# Mock the reranker model to avoid downloading the real model during tests
class MockCrossEncoder:
    def predict(self, pairs):
        # Return a higher score if the chunk text contains the query word
        scores = []
        for q, text in pairs:
            if q.lower() in text.lower():
                scores.append(0.9)
            else:
                scores.append(0.1)
        return scores

def test_reranker_output_format(monkeypatch):
    # Monkeypatch the get_reranker_model function
    import backend.retrieval.reranker as reranker_module
    monkeypatch.setattr(reranker_module, "get_reranker_model", lambda: MockCrossEncoder())
    
    query = "apple"
    chunks = [
        Chunk(text="Banana is yellow.", metadata=ChunkMetadata(chunk_id="1", doc_id="d1", char_start=0, char_end=10, token_count=5)),
        Chunk(text="An apple a day keeps the doctor away.", metadata=ChunkMetadata(chunk_id="2", doc_id="d1", char_start=0, char_end=10, token_count=5)),
        Chunk(text="Orange is round.", metadata=ChunkMetadata(chunk_id="3", doc_id="d1", char_start=0, char_end=10, token_count=5)),
    ]
    
    results = rerank_candidates(query, chunks, top_k=2)
    
    # Check format: List[Tuple[Chunk, float]]
    assert isinstance(results, list)
    assert len(results) == 2
    
    top_chunk, top_score = results[0]
    assert isinstance(top_chunk, Chunk)
    assert isinstance(top_score, float)
    
    # Our mock scores the "apple" chunk highest
    assert top_chunk.metadata.chunk_id == "2"
    assert top_score == 0.9
