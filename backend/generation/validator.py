import re
from backend.models.schemas import ValidationResult
from backend.utils.logger import log_pipeline_stage
import logging

logger = logging.getLogger(__name__)

@log_pipeline_stage("Validation")
def validate_generation(answer: str) -> ValidationResult:
    """
    Validates the LLM generation.
    Checks for citations and fallback phrases.
    """
    # 1. Check for 'I don't know' phrasing
    fallback_phrases = [
        "i don't know",
        "i do not know",
        "does not contain the answer",
        "cannot answer",
        "information is not available"
    ]
    
    lower_answer = answer.lower()
    
    # The prompt explicitly tells the model to say "I don't know based on the provided context."
    # We should specifically look for that.
    is_fallback = "i don't know based on the provided context" in lower_answer or \
                  any(phrase in lower_answer for phrase in fallback_phrases)
    
    # 2. Check for citations
    # Look for [SOURCE_X]
    citation_pattern = r"\[SOURCE_(\d+)\]"
    cited_tags = set(re.findall(citation_pattern, answer))
    has_citations = len(cited_tags) > 0
    
    is_grounded = has_citations and not is_fallback
    
    # Calculate a rough confidence score
    confidence_score = 100
    warning = None
    
    if is_fallback:
        confidence_score = 10
        warning = "The model indicated it could not find the answer in the context."
    elif not has_citations:
        confidence_score = 40
        warning = "The model provided an answer but failed to cite its sources."
    else:
        bonus = min(25, 5 * len(cited_tags))
        confidence_score = 70 + bonus
        
    return ValidationResult(
        is_grounded=is_grounded,
        confidence_score=confidence_score,
        warning=warning
    )
