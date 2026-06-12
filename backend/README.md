# 🧠 DSM-5 RAG Backend

FastAPI backend service for the DSM-5 psychological analysis system. Handles document processing, vector embeddings, RAG pipelines, and symptom analysis.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# From the backend directory
uv sync
```

### 2. Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Required variables:
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 3. Ingest Documents

From the **project root**, run:
```bash
python backend/scripts/ingest.py
```

### 4. Start the Server

```bash
# From the backend directory
python main.py
```

Server will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Health**: http://localhost:8000/health

## 📁 Directory Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management (Pydantic Settings)
├── models.py               # Pydantic models for requests/responses
├── database.py             # ChromaDB vector database management
├── rag_pipeline.py         # RAG implementation with LangChain
├── .env.example            # Environment variable template
├── .env                    # Local environment variables (not committed)
├── pyproject.toml          # Python dependencies
├── uv.lock                 # Dependency lock file
├── scripts/
│   └── ingest.py           # Document ingestion and vector DB population
├── chunking/
│   ├── metadata_extractor.py    # Stage 1: Extract metadata from DSM-5
│   ├── semantic_splitter.py     # Stage 2: Semantic chunking
│   └── hybrid_processor.py      # Orchestrates both stages
├── data/
│   └── chroma_db/          # Vector database storage (created at runtime)
└── logs/
    └── app.log             # Application logs (created at runtime)
```

## 🔧 Configuration

### Environment Variables

All configuration is in `.env`:

**Core Settings:**
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-small)
- `LLM_MODEL` - LLM for analysis (default: gpt-4o)
- `LLM_TEMPERATURE` - Model temperature 0-1 (default: 0.3)

**Database:**
- `CHROMA_PERSIST_DIRECTORY` - Where to store embeddings (default: ./data/chroma_db)
- `COLLECTION_NAME` - ChromaDB collection name (default: dsm5_collection)

**Chunking (Document Processing):**
- `SEMANTIC_BREAKPOINT_THRESHOLD` - Semantic similarity threshold (default: 0.75)
- `MIN_CHUNK_SIZE` - Minimum chunk size (default: 500)
- `MAX_CHUNK_SIZE` - Maximum chunk size (default: 2000)
- `CHUNK_OVERLAP` - Overlap between chunks (default: 100)

**RAG:**
- `TOP_K_RESULTS` - Documents to retrieve (default: 5)
- `SIMILARITY_THRESHOLD` - Minimum similarity score (default: 0.7)
- `RERANK_ENABLED` - Enable reranking (default: true)

**API:**
- `API_HOST` - Bind address (default: 0.0.0.0)
- `API_PORT` - Port number (default: 8000)
- `API_RELOAD` - Auto-reload on changes (default: true)

**Safety:**
- `ENABLE_DISCLAIMER` - Show medical disclaimer (default: true)
- `REQUIRE_DISCLAIMER_ACCEPTANCE` - Require acceptance (default: true)
- `LOG_USER_QUERIES` - Log queries (default: false)

## 📚 API Endpoints

### `POST /analyze` - Analyze Symptoms

Analyzes user symptoms against DSM-5 diagnostic criteria.

**Request:**
```json
{
  "symptoms": "I have been feeling very sad for weeks, no energy, can't concentrate",
  "duration": "4 weeks"
}
```

**Response:**
```json
{
  "analysis": "Based on DSM-5 criteria...",
  "disclaimer": "This is not a medical diagnosis...",
  "sources": [
    {
      "content": "DSM-5 text chunk...",
      "disorder_name": "Major Depressive Disorder",
      "disorder_category": "Depressive Disorders",
      "criteria_label": "Criterion A",
      "icd_code": "F32.x",
      "page_number": 160,
      "relevance_score": 0.89
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "model_used": "gpt-4o"
}
```

### `GET /health` - System Health Check

Checks if the system is healthy and ready.

**Response:**
```json
{
  "status": "healthy",
  "vector_db_status": "connected",
  "documents_indexed": 1247,
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### `GET /docs` - Interactive API Documentation

OpenAPI/Swagger UI at http://localhost:8000/docs

### `GET /openapi.json` - OpenAPI Schema

Raw OpenAPI specification.

## 🔄 Document Ingestion

### Running Ingestion

From the **project root**:

```bash
python backend/scripts/ingest.py
```

**What it does:**
1. Loads DSM-5.pdf from project root
2. Extracts text and structure
3. Stage 1: Extracts metadata (disorders, criteria, ICD codes)
4. Stage 2: Applies semantic chunking
5. Generates embeddings via OpenAI API
6. Stores in ChromaDB with metadata

**Output example:**
```
============================================================
DSM-5 Document Ingestion Pipeline
============================================================
Found DSM-5.pdf at: /path/to/DSM-5.pdf

Stage 1: Loading and Processing DSM-5.pdf
============================================================
Processing Statistics:
  Total chunks: 1247
  Average chunk size: 1850 characters
  Min chunk size: 523 characters
  Max chunk size: 1999 characters
  Total characters: 2,306,150

Stage 2: Adding Documents to Vector Database
============================================================
Generating embeddings and storing in ChromaDB...
  Batch 1/25 complete (50/1247 documents)
  Batch 2/25 complete (100/1247 documents)
  ...
  Batch 25/25 complete (1247/1247 documents)

Stage 3: Verification
============================================================
  Documents in database: 1247
  Database status: connected

✓ Ingestion completed successfully!
✓ 1247 documents indexed
```

### Re-ingesting Documents

To reset and re-ingest:

```bash
python backend/scripts/ingest.py
# When prompted: "Reset and re-ingest? (yes/no): " → yes
```

## 🔍 How It Works

### 1. Hybrid Document Processing

**Stage 1: Metadata Extraction**
- Parses DSM-5 structure
- Identifies: disorders, categories, diagnostic criteria
- Extracts: ICD codes, severity levels, specifiers
- Preserves diagnostic relationships

**Stage 2: Semantic Chunking**
- Uses embeddings to find natural breakpoints
- Maintains context within chunks
- Respects min/max size constraints
- Creates overlap for context

### 2. RAG Pipeline

```
User Query
    ↓
Generate Embedding
    ↓
Similarity Search (ChromaDB)
    ↓
Filter by Threshold
    ↓
Rerank Results
    ↓
Build Prompt
    ↓
Call GPT-4o
    ↓
Format Response
    ↓
Return with Sources
```

**Retrieval Phase:**
1. Convert user query to embedding
2. Search ChromaDB for similar documents
3. Filter by similarity threshold
4. Optional: rerank by relevance

**Generation Phase:**
1. Build prompt with retrieved context
2. Add system instructions (safety guardrails)
3. Include user symptoms and duration
4. Send to GPT-4o
5. Return analysis with source attribution

## 🧬 Module Overview

### `config.py`
Pydantic Settings-based configuration management. Loads environment variables, validates types, provides getter methods.

### `models.py`
Request/response Pydantic models:
- `AnalysisRequest` - /analyze endpoint input
- `AnalysisResponse` - /analyze endpoint output
- `HealthResponse` - /health endpoint output
- `SourceDocument` - Retrieved DSM-5 chunks with metadata
- `ChunkMetadata` - Metadata for each chunk

### `database.py`
ChromaDB vector database management:
- Collection initialization
- Document addition with embeddings
- Similarity search
- Collection statistics
- Health checks

### `rag_pipeline.py`
RAG implementation with LangChain:
- Prompt construction
- LLM calls with safety guardrails
- Result formatting
- Source attribution

### `chunking/metadata_extractor.py`
Stage 1: Metadata extraction from DSM-5
- Identifies disorder headers
- Extracts diagnostic criteria
- Captures ICD codes
- Preserves section structure

### `chunking/semantic_splitter.py`
Stage 2: Semantic chunking
- Embedding-based breakpoints
- Size validation
- Overlap management

### `chunking/hybrid_processor.py`
Orchestrates both processing stages
- Calls metadata extractor
- Calls semantic splitter
- Combines results
- Generates processing statistics

## 📊 Logging

Logs are written to `logs/app.log` with structured format:

```
2024-01-15 10:30:45 | INFO    | Document ingestion started
2024-01-15 10:31:12 | DEBUG   | Extracted 1247 chunks
2024-01-15 10:45:22 | INFO    | Embeddings generated and stored
2024-01-15 10:45:23 | SUCCESS | Ingestion completed!
```

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🐛 Troubleshooting

### "Missing credentials" Error
```
ERROR - Error during startup: Missing credentials. Please pass an `api_key`...
```

**Solution:**
1. Check `.env` exists in `backend/` directory
2. Verify `OPENAI_API_KEY=sk-...` is set
3. Restart the application

### "OpenAI object has no attribute 'create'"
```
AttributeError: 'OpenAI' object has no attribute 'create'
```

**Solution:** This indicates a library version mismatch. The code has been fixed to work with the latest `langchain-openai` version. Update your code.

### "DSM-5.pdf not found"
```
ERROR - DSM-5.pdf not found in current directory
```

**Solution:** Place `DSM-5.pdf` in the **project root**, not in the `backend/` directory.

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
API_PORT=8001 python main.py
```

### Vector Database Errors
- Check `data/chroma_db/` directory exists
- Check disk space
- Try deleting and re-ingesting: `rm -rf data/chroma_db/`

### Slow Ingestion
- Ingestion typically takes 10-30 minutes for DSM-5
- Depends on document size and OpenAI API speed
- Each embedding call costs tokens
- Monitor: Watch the "Batch X/Y" progress output

## 🔒 Security Notes

- **API Keys**: Store in `.env`, never commit to git
- **User Data**: Not logged by default (see `LOG_USER_QUERIES` config)
- **Embeddings**: Sent to OpenAI (no local computation)
- **Vector DB**: Stored locally, not sent anywhere
- **HTTPS**: Use in production

## 📝 Development

### Running with Auto-reload
```bash
python main.py
# Auto-reloads on file changes (due to API_RELOAD=true)
```

### Running Tests
```bash
# Tests would go in tests/ directory
pytest tests/
```

### Type Checking
```bash
# mypy for static type checking
mypy backend/
```

## 🚢 Deployment

For production:
1. Set `API_RELOAD=false`
2. Set `LOG_LEVEL=WARNING`
3. Use proper HTTPS/reverse proxy
4. Implement authentication
5. Add rate limiting
6. Monitor logs and performance

Example with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

## 📚 Additional Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)

---

**Built with ❤️ for educational purposes**
