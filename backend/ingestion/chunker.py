import re
import uuid
import tiktoken
import nltk
nltk.download('punkt_tab', quiet=True)
from nltk.tokenize import sent_tokenize
from typing import List, Tuple
from backend.models.schemas import ExtractedText, Chunk, ChunkMetadata
from backend.utils.logger import log_pipeline_stage

# Initialize tiktoken encoder
# using 'cl100k_base' which is standard for OpenAI models (and roughly approximates others)
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Counts tokens using tiktoken."""
    return len(enc.encode(text))

def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using NLTK.
    """
    return [s for s in sent_tokenize(text) if s.strip()]

@log_pipeline_stage("Chunking")
def chunk_document(doc_id: str, extracted_texts: List[ExtractedText], 
                   target_chunk_size: int = 400, 
                   overlap_size: int = 50) -> List[Chunk]:
    chunks = []
    chunk_index = 0
    global_char_offset = 0
    
    for ext_text in extracted_texts:
        if not ext_text.text.strip():
            continue
            
        sentences = split_into_sentences(ext_text.text)
        
        current_chunk_sentences = []
        current_chunk_tokens = 0
        current_chunk_char_length = 0
        
        # We need to track the char start of the current chunk
        # relative to the entire document.
        chunk_start_char = global_char_offset
        
        def finalize_chunk(sentences_to_include: List[str], token_count: int, char_length: int, start_char: int):
            nonlocal chunk_index
            chunk_text = " ".join(sentences_to_include)
            chunks.append(
                Chunk(
                    text=chunk_text,
                    metadata=ChunkMetadata(
                        chunk_id=f"{doc_id}_{chunk_index}",
                        doc_id=doc_id,
                        page_number=ext_text.page_number,
                        section_heading=ext_text.section_heading,
                        char_start=start_char,
                        char_end=start_char + len(chunk_text),
                        token_count=token_count
                    )
                )
            )
            chunk_index += 1
            
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            # Approximate sentence length + space
            sentence_char_length = len(sentence) + (1 if current_chunk_sentences else 0)
            sentence_tokens = count_tokens(sentence)
            
            # If a single sentence is larger than the target, we must include it anyway
            # as the spec says "Never split mid-sentence".
            if not current_chunk_sentences and sentence_tokens >= target_chunk_size:
                finalize_chunk([sentence], sentence_tokens, sentence_char_length, chunk_start_char)
                chunk_start_char += sentence_char_length
                i += 1
                continue
                
            if current_chunk_tokens + sentence_tokens > target_chunk_size:
                # Chunk is full, finalize it
                finalize_chunk(current_chunk_sentences, current_chunk_tokens, current_chunk_char_length, chunk_start_char)
                
                # Setup overlap for the next chunk
                overlap_sentences = []
                overlap_tokens = 0
                overlap_char_length = 0
                
                # Go backwards through current chunk sentences to build overlap
                for s in reversed(current_chunk_sentences):
                    s_toks = count_tokens(s)
                    if overlap_tokens + s_toks > overlap_size and overlap_sentences:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_tokens += s_toks
                    overlap_char_length += len(s) + 1 # +1 for space
                
                # Advance chunk_start_char
                # The next chunk starts at the end of the previous chunk MINUS the overlap
                chunk_start_char += (current_chunk_char_length - overlap_char_length)
                
                current_chunk_sentences = overlap_sentences
                current_chunk_tokens = overlap_tokens
                current_chunk_char_length = overlap_char_length
            
            current_chunk_sentences.append(sentence)
            current_chunk_tokens += sentence_tokens
            current_chunk_char_length += sentence_char_length
            i += 1
            
        # Finalize the last chunk for this extracted text block
        if current_chunk_sentences:
            finalize_chunk(current_chunk_sentences, current_chunk_tokens, current_chunk_char_length, chunk_start_char)
            
        global_char_offset += len(ext_text.text) + 1 # +1 for newline separation between blocks
        
    return chunks
