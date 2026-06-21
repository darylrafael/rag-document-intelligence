import pytest
from backend.generation.validator import validate_generation
from backend.models.schemas import ValidationResult

def test_validate_generation_with_citations():
    answer = "The sky is blue because of Rayleigh scattering as stated in [SOURCE_1]. It is also known to scatter shorter wavelengths more than longer ones [SOURCE_2]."
    result = validate_generation(answer)
    
    assert result.is_grounded == True
    assert result.confidence_score == 80 # 70 base + 2 tags * 5
    assert result.warning is None

def test_validate_generation_without_citations():
    answer = "The sky is blue because of Rayleigh scattering."
    result = validate_generation(answer)
    
    assert result.is_grounded == False
    assert result.confidence_score == 40
    assert "failed to cite" in result.warning

def test_validate_generation_fallback():
    answer = "I don't know based on the provided context."
    result = validate_generation(answer)
    
    assert result.is_grounded == False
    assert result.confidence_score == 10
    assert "could not find the answer" in result.warning
