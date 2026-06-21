from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

# ==========================================
# Internal Pipeline Schemas
# ==========================================

class ExtractedText(BaseModel):
    model_config = ConfigDict(strict=True)
    text: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    file_type: Literal["pdf", "docx", "txt"]

class ChunkMetadata(BaseModel):
    model_config = ConfigDict(strict=True)
    chunk_id: str
    doc_id: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    char_start: int
    char_end: int
    token_count: int

class Chunk(BaseModel):
    model_config = ConfigDict(strict=True)
    text: str
    metadata: ChunkMetadata

class Citation(BaseModel):
    model_config = ConfigDict(strict=True)
    chunk_id: str
    doc_id: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    relevance_score: float
    chunk_text: str

class GenerationResult(BaseModel):
    model_config = ConfigDict(strict=True)
    answer: str
    citations: List[Citation]
    confidence_score: int = Field(ge=0, le=100)
    model_used: str

class ValidationResult(BaseModel):
    model_config = ConfigDict(strict=True)
    is_grounded: bool
    confidence_score: int = Field(ge=0, le=100)
    warning: Optional[str] = None

# ==========================================
# API Request/Response Schemas
# ==========================================

class DocumentResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    filename: str
    file_type: str
    chunk_count: int
    indexed_at: datetime
    file_size_kb: float
    status: str

class UploadResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    doc_id: str
    chunk_count: int

class QueryRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    doc_ids: Optional[List[str]] = None # Optional filter by document

class PipelineTiming(BaseModel):
    model_config = ConfigDict(strict=True)
    expansion_ms: float = 0.0
    retrieval_ms: float = 0.0
    reranking_ms: float = 0.0
    generation_ms: float = 0.0
    total_ms: float = 0.0

class QueryResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    answer: str
    citations: List[Citation]
    confidence_score: int
    warning: Optional[str] = None
    timing: PipelineTiming

class QueryHistoryItem(BaseModel):
    model_config = ConfigDict(strict=True)
    query_id: str
    question: str
    timestamp: datetime
    confidence_score: int
    doc_count: int
    answer: Optional[str] = None
    citations: Optional[List[Citation]] = None
    timing: Optional[PipelineTiming] = None

class QueryHistoryResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    items: List[QueryHistoryItem]
    total: int
    page: int
    size: int

class DocumentQueryCount(BaseModel):
    model_config = ConfigDict(strict=True)
    doc_id: str
    filename: str
    query_count: int

class AnalyticsStatsResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    total_docs: int
    total_queries: int
    avg_confidence: float
    most_queried_docs: List[DocumentQueryCount]
