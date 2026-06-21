import pytest
from backend.ingestion.chunker import count_tokens, split_into_sentences, chunk_document
from backend.models.schemas import ExtractedText

def test_count_tokens():
    # "Hello world" -> 2 tokens
    assert count_tokens("Hello world") == 2
    # tiktoken cl100k_base specific cases
    assert count_tokens("This is a test sentence.") > 0
    assert count_tokens("") == 0

def test_split_into_sentences():
    text = "This is sentence one. And this is sentence two! Is this sentence three? Yes."
    sentences = split_into_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "This is sentence one."
    assert sentences[1] == "And this is sentence two!"
    assert sentences[2] == "Is this sentence three?"
    assert sentences[3] == "Yes."

def test_chunk_document_basic():
    text = "Sentence one. " * 50  # Lots of short sentences
    extracted = [
        ExtractedText(
            text=text,
            page_number=1,
            section_heading="Test",
            file_type="txt"
        )
    ]
    
    # Very small target to force chunking
    chunks = chunk_document("doc_1", extracted, target_chunk_size=10, overlap_size=2)
    
    assert len(chunks) > 1
    # Check that metadata is preserved
    for chunk in chunks:
        assert chunk.metadata.doc_id == "doc_1"
        assert chunk.metadata.page_number == 1
        assert chunk.metadata.section_heading == "Test"
        assert chunk.metadata.char_end > chunk.metadata.char_start
        assert chunk.metadata.token_count <= 15 # slightly over target due to "never split mid-sentence"
