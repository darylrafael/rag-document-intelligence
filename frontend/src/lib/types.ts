export interface DocumentResponse {
    id: string;
    filename: string;
    file_type: string;
    chunk_count: number;
    indexed_at: string;
    file_size_kb: number;
    status: string;
}

export interface Citation {
    chunk_id: string;
    doc_id: string;
    page_number?: number;
    section_heading?: string;
    relevance_score: number;
    chunk_text: string;
}

export interface PipelineTiming {
    expansion_ms: number;
    retrieval_ms: number;
    reranking_ms: number;
    generation_ms: number;
    total_ms: number;
}

export interface QueryResponse {
    answer: string;
    citations: Citation[];
    confidence_score: number;
    warning?: string;
    timing: PipelineTiming;
}

export interface QueryHistoryItem {
    query_id: string;
    question: string;
    confidence_score: number;
    timestamp: string;
    referenced_doc_ids: string[];
    answer?: string;
    citations?: Citation[];
    timing?: PipelineTiming;
}

export interface QueryHistoryResponse {
    items: QueryHistoryItem[];
    total: number;
    page: number;
    size: number;
}

export interface AnalyticsStatsResponse {
    total_documents: number;
    total_queries: number;
    avg_confidence: number;
    most_queried_documents: Record<string, number>;
}
