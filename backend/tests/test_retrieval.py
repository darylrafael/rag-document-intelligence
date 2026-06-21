import pytest
from backend.retrieval.searcher import reciprocal_rank_fusion

def test_rrf_scoring():
    # Simulate ranked lists returned by different search paths
    # List of chunk IDs ordered by rank (best first)
    list1 = ["chunk_A", "chunk_B", "chunk_C"]
    list2 = ["chunk_B", "chunk_D", "chunk_A"]
    list3 = ["chunk_E", "chunk_C", "chunk_B"]
    
    k = 60
    
    merged = reciprocal_rank_fusion([list1, list2, list3], k=k)
    
    # We expect chunk_B to be ranked highly because it appears in all 3 lists
    # Score for chunk_B: 1/(60+2) + 1/(60+1) + 1/(60+3) = 0.0161 + 0.0163 + 0.0158
    # Score for chunk_A: 1/(60+1) + 1/(60+3) = 0.0163 + 0.0158
    # Score for chunk_C: 1/(60+3) + 1/(60+2) = 0.0158 + 0.0161
    
    # Extract just the sorted IDs
    sorted_ids = [chunk_id for chunk_id, score in merged]
    
    # chunk_B should be first
    assert sorted_ids[0] == "chunk_B"
    # It should contain all unique chunks: A, B, C, D, E (len 5)
    assert len(sorted_ids) == 5
    
    # Check that scores are strictly descending
    scores = [score for chunk_id, score in merged]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i+1]
