from fastapi import APIRouter, Query
from backend.models.schemas import QueryHistoryResponse, AnalyticsStatsResponse
from backend.db.queries import get_query_history, get_analytics_stats, get_total_queries_count

router = APIRouter()

@router.get("/queries", response_model=QueryHistoryResponse)
async def list_queries(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    items = get_query_history(page=page, size=size)
    total = get_total_queries_count()
    return QueryHistoryResponse(items=items, total=total, page=page, size=size)

@router.get("/stats", response_model=AnalyticsStatsResponse)
async def get_stats():
    return get_analytics_stats()
