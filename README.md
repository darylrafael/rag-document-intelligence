# RAG Document Intelligence System

A production-grade, local-first Retrieval-Augmented Generation (RAG) Document Intelligence System designed for advanced document analysis. Built using a robust Python (FastAPI) backend and a sleek, modern Next.js 16 (React) frontend styled with Tailwind CSS v4 and animated using Framer Motion.


## UI Preview & Demo

Here is a visual walk-through of the system interface:

### 1. Document Library (`/`)
A clean drag-and-drop workspace for uploading and indexing files (supporting PDF, DOCX, TXT) with automatic text extraction, chunking, and dual-indexing.
![Document Library](assets/document_library.png)

### 2. Query Engine (`/chat`)
A real-time search interface displaying multi-query expansion, inline source citations, and query response validation checks.
![Query Engine Chat](assets/chat_interface.png)

### 3. System Analytics (`/analytics`)
Tracks total documents, average confidence scores, total queries executed, and displays interactive historical audit logs.
![System Analytics Dashboard](assets/analytics_dashboard.png)

### 4. Query Execution Report
Clicking any query in the analytics logs opens a rich, glassmorphic performance execution report displaying the exact question, generated answer, and source document citation text alongside the execution speed breakdown of the RAG pipeline.
![Query Execution Report](assets/query_report_modal.png)

---

## Key Features & Architecture

This application employs a high-performance hybrid retrieval pipeline utilizing state-of-the-art information retrieval patterns:

*   **Hybrid Search**: Combines semantic search (vector embeddings via `sentence-transformers/all-MiniLM-L6-v2` in ChromaDB) and keyword search (BM25 lexical scoring) to achieve highly relevant candidate selection.
*   **Reciprocal Rank Fusion (RRF)**: Merges keyword and vector search results using RRF ($k=60$) to balance the strengths of semantic context and precise keyword matching.
*   **Cross-Encoder Reranking**: Re-evaluates the top 20 candidates retrieved by RRF using a local Cross-Encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`), narrowing them down to the top 5 most critical context chunks.
*   **DeepSeek V4 Flash via OpenRouter**: Orchestrates advanced multi-query expansion (phrasing 2 alternative queries) and contextual generation using the DeepSeek model.
*   **Citations & Groundedness Verification**: 
    *   Generates inline citations matching actual retrieved source indices (e.g., `[SOURCE_1]`).
    *   A validator analyzes the model output, filters citations down to the source tags actually cited, and computes a dynamic confidence score (ranging from 10 to 95+) depending on citation completeness, fallback usage, and source matching.
*   **SQLite Metadata Engine**: Manages document processing state, chunks, query history, and analytics records.
*   **Modern Admin Dashboard**:
    *   **Document Library**: Interactive drag-and-drop file upload supporting PDF, DOCX, and TXT files, showing index status, size, and chunk count.
    *   **Chat Workspace**: Features timing metrics for each retrieval step (expansion, retrieval, reranking, generation) and dynamically renders cited source text blocks when hovering over or selecting inline citations.
    *   **System Analytics**: Visual dashboard tracking document indexing history, average generation confidence scores, and historical query logs.

---

## Workflow Architecture

### Ingestion Pipeline

When a document is uploaded, it flows through extraction → chunking → dual indexing:

```mermaid
flowchart LR
    A["📄 Upload\n(PDF / DOCX / TXT)"] --> B["🔍 Extract Text\npdfplumber\npython-docx"]
    B --> C["✂️ Chunk\nNLTK Sentence\nTokenizer"]
    C --> D["🧠 Embed\nall-MiniLM-L6-v2"]
    C --> F["📊 BM25\nLexical Index"]
    D --> E["🗄️ ChromaDB\nVector Store"]
    E --> G["💾 SQLite\nMetadata"]
    F --> G

    style A fill:#4f46e5,stroke:#3730a3,color:#fff
    style B fill:#7c3aed,stroke:#6d28d9,color:#fff
    style C fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style D fill:#2563eb,stroke:#1d4ed8,color:#fff
    style E fill:#0891b2,stroke:#0e7490,color:#fff
    style F fill:#0891b2,stroke:#0e7490,color:#fff
    style G fill:#059669,stroke:#047857,color:#fff
```

### Query & Retrieval Pipeline

When a user asks a question, it flows through expansion → hybrid search → reranking → generation:

```mermaid
flowchart LR
    Q["❓ User\nQuestion"] --> EX["🔀 Query\nExpansion\nDeepSeek V4 Flash"]
    EX --> S1["🧠 Semantic\nSearch\nChromaDB"]
    EX --> S2["📊 Keyword\nSearch\nBM25"]
    S1 --> RRF["⚡ Reciprocal\nRank Fusion\nk=60"]
    S2 --> RRF
    RRF --> RR["🎯 Cross-Encoder\nReranking\nTop 20 → Top 5"]
    RR --> GEN["💬 Generation\nDeepSeek V4 Flash\nContextual Answer"]
    GEN --> VAL["✅ Validation\nGroundedness\nConfidence Score"]
    VAL --> OUT["📋 Response\nAnswer + Cited\nSources"]

    style Q fill:#4f46e5,stroke:#3730a3,color:#fff
    style EX fill:#7c3aed,stroke:#6d28d9,color:#fff
    style S1 fill:#2563eb,stroke:#1d4ed8,color:#fff
    style S2 fill:#2563eb,stroke:#1d4ed8,color:#fff
    style RRF fill:#d97706,stroke:#b45309,color:#fff
    style RR fill:#dc2626,stroke:#b91c1c,color:#fff
    style GEN fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style VAL fill:#059669,stroke:#047857,color:#fff
    style OUT fill:#059669,stroke:#047857,color:#fff
```

---

## Project Structure

```
rag-document-intelligence/
├── backend/
│   ├── api/
│   │   └── routes/             # Endpoints: documents, query, analytics
│   ├── db/
│   │   ├── database.py         # SQLite initialization and connections
│   │   └── queries.py          # SQLite database query functions
│   ├── generation/
│   │   ├── generator.py        # LLM contextual response generation
│   │   └── validator.py        # Groundedness evaluation and scoring
│   ├── ingestion/
│   │   ├── chunker.py          # NLTK token-aware text chunking
│   │   ├── embedder.py         # Local SentenceTransformer embeddings
│   │   ├── extractor.py        # PDF, DOCX, and TXT parser
│   │   └── indexer.py          # Vector (Chroma) and BM25 indexer
│   ├── models/
│   │   └── schemas.py          # Pydantic schema validation
│   ├── prompts/                # Prompt templates for LLM instruction
│   ├── retrieval/
│   │   ├── expander.py         # Query expansion engine
│   │   ├── reranker.py         # Local Cross-Encoder reranker
│   │   └── searcher.py         # Hybrid search engine (BM25 + Chroma + RRF)
│   ├── tests/                  # Pytest unit testing suite
│   ├── utils/
│   │   ├── logger.py           # Pipeline execution timer logs
│   │   └── openrouter.py       # OpenRouter API client wrapper
│   ├── main.py                 # FastAPI application root
│   └── requirements.txt        # Python dependency manifest
├── frontend/
│   ├── src/
│   │   ├── app/                # App Router pages: Dashboard, Chat, Analytics
│   │   ├── components/         # Reusable UI components (Sidebar, UploadZone, etc.)
│   │   ├── hooks/              # Custom React hooks (useChat, useDocuments)
│   │   └── lib/                # API client helper and TypeScript types
│   ├── next.config.ts          # Next.js configurations
│   ├── package.json            # Node dependency manifest
│   └── tsconfig.json           # TypeScript configuration
├── rag_system.db               # Local SQLite database (auto-generated)
├── chroma_data/                # Local ChromaDB persistent database (auto-generated)
└── README.md                   # Project documentation
```

---

## Getting Started

### Prerequisites
*   Python 3.11+
*   Node.js 18+

### 1. Backend Setup (FastAPI)
1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure your local environment. Create a `.env` file in the `backend/` directory using `.env.example` as a template:
    ```env
    OPENROUTER_API_KEY=your_openrouter_api_key_here
    LLM_MODEL=deepseek/deepseek-v4-flash
    DB_PATH=rag_system.db
    ```
4.  Run the API server from the project root directory:
    ```bash
    cd ..
    uvicorn backend.main:app --reload --port 8000
    ```
    *The server will initialize the SQLite database (`rag_system.db`) and download the local models (`all-MiniLM-L6-v2` and `ms-marco-MiniLM-L-6-v2`) on its first launch.*

### 2. Frontend Setup (Next.js)
1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install Node dependencies:
    ```bash
    npm install
    ```
3.  Run the Next.js development server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000) in your web browser to upload documents and begin testing the pipeline.

---

## Running Verification & Tests

### Backend Unit Tests
We use `pytest` to verify individual components in the retrieval, chunking, and validation layers. Run the test suite from the project root:
```bash
python -m pytest
```

### Production Build
To verify type-checking and Next.js compiler correctness, build the production Next.js bundle:
```bash
cd frontend
npm run build
```
