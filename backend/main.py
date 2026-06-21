from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.routes import documents, query, analytics
from backend.ingestion.embedder import get_embedder_model
from backend.retrieval.reranker import get_reranker_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models at startup
    get_embedder_model()
    get_reranker_model()
    yield
    # Cleanup on shutdown if needed

app = FastAPI(title="RAG Document Intelligence", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "details": str(exc)}
    )

# Routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "models_loaded": True}
