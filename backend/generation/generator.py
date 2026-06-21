import os
import re
from typing import List, Tuple
from backend.models.schemas import Chunk, Citation, GenerationResult
from backend.utils.logger import log_pipeline_stage
from backend.utils.openrouter import generate_chat_completion, MODEL_NAME
import logging

logger = logging.getLogger(__name__)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "generation_prompt.txt")

try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        GENERATION_PROMPT_TEMPLATE = f.read()
except Exception as e:
    logger.error(f"Failed to load generation prompt: {e}")
    GENERATION_PROMPT_TEMPLATE = "CONTEXT:\n{context}\n\nQUESTION:\n{question}"

def format_context_and_citations(scored_chunks: List[Tuple[Chunk, float]]) -> Tuple[str, List[Citation]]:
    """Formats the top chunks into a single context string and generates Citation objects."""
    context_blocks = []
    citations = []
    
    for i, (chunk, score) in enumerate(scored_chunks, start=1):
        source_tag = f"[SOURCE_{i}]"
        
        # Build context block
        block = f"{source_tag}\n{chunk.text}\n"
        context_blocks.append(block)
        
        # Build Citation object
        citations.append(
            Citation(
                chunk_id=chunk.metadata.chunk_id,
                doc_id=chunk.metadata.doc_id,
                page_number=chunk.metadata.page_number,
                section_heading=chunk.metadata.section_heading,
                relevance_score=float(score),
                chunk_text=chunk.text
            )
        )
        
    return "\n".join(context_blocks), citations

@log_pipeline_stage("Generation")
async def generate_answer(question: str, scored_chunks: List[Tuple[Chunk, float]]) -> GenerationResult:
    """
    Calls the LLM to generate an answer based on the provided scored chunks.
    Returns the initial GenerationResult without validation confidence.
    """
    context_str, citations = format_context_and_citations(scored_chunks)
    
    prompt = GENERATION_PROMPT_TEMPLATE.replace("{context}", context_str).replace("{question}", question)
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        answer = await generate_chat_completion(messages, temperature=0.1)
        
        cited_indices = set(int(m) - 1 for m in re.findall(r'\[SOURCE_(\d+)\]', answer))
        filtered_citations = [c for i, c in enumerate(citations) if i in cited_indices]
        if not filtered_citations:
            filtered_citations = citations
            
        return GenerationResult(
            answer=answer,
            citations=filtered_citations,
            confidence_score=0, # Default, to be updated by validator
            model_used=MODEL_NAME
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise
