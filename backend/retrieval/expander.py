import os
from typing import List
import logging
from backend.utils.logger import log_pipeline_stage
from backend.utils.openrouter import generate_chat_completion

logger = logging.getLogger(__name__)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "query_expansion_prompt.txt")

try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        EXPANSION_PROMPT_TEMPLATE = f.read()
except Exception as e:
    logger.error(f"Failed to load query expansion prompt: {e}")
    EXPANSION_PROMPT_TEMPLATE = "Expand this query into 2 alternative phrasings:\n{query}"

@log_pipeline_stage("Query Expansion")
async def expand_query(query: str) -> List[str]:
    """
    Expands the original query into 2 alternative phrasings.
    Returns: List of 2 alternative query phrasings. 
    Does NOT include the original query.
    """
    prompt = EXPANSION_PROMPT_TEMPLATE.replace("{query}", query)
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = await generate_chat_completion(messages, temperature=0.7)
        # Parse the response (expecting two lines)
        lines = [line.strip() for line in response.strip().split("\n") if line.strip() and not line.startswith("Here are")]
        
        alts = lines[:2]
        return alts
    except Exception as e:
        logger.warning(f"Query expansion failed, falling back to original query. Error: {e}")
        # Fallback on failure
        return []
