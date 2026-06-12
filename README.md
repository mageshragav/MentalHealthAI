# 🧠 DSM-5 Psychological Analysis System

A sophisticated **Retrieval-Augmented Generation (RAG)** system that analyzes psychological symptoms against DSM-5 diagnostic criteria using OpenAI GPT-4o and ChromaDB vector database.

## ⚠️ Important Disclaimer

**THIS IS NOT A MEDICAL DIAGNOSTIC TOOL.** This system is for educational and informational purposes only. It does NOT replace professional medical advice, diagnosis, or treatment. Always consult qualified mental health professionals for proper evaluation and care.

## 🌟 Features

- **Hybrid Document Processing**: Combines metadata extraction with semantic chunking for optimal context preservation
- **Advanced RAG Pipeline**: Uses LangChain with OpenAI GPT-4o for intelligent symptom analysis
- **Vector Database**: ChromaDB for efficient similarity search with persistent storage
- **Safety-First Design**: Built-in medical disclaimers and safety guardrails
- **Modern Stack**: FastAPI backend + Streamlit frontend
- **Rich Metadata**: Extracts disorder categories, ICD codes, diagnostic criteria labels
- **Source Attribution**: Shows which DSM-5 sections were used in analysis

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   FastAPI       │
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ RAG    │ │ ChromaDB │
│Pipeline│ │ Vector   │
└───┬────┘ │ Database │
    │      └──────────┘
    ▼
┌──────────────┐
│ OpenAI GPT-4o│
│ + Embeddings │
└──────────────┘
```

## 📋 Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- DSM-5.pdf file (place in project root)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install dependencies using uv
uv sync

# Or install manually
uv pip install -r pyproject.toml
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

**Required environment variables:**
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

To get your OpenAI API key:
1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy it and paste in `.env`

### 3. Prepare DSM-5 Document

Place your `DSM-5.pdf` file in the **project root** directory:

```
Rag_DeviPriya/
├── DSM-5.pdf          ← Place here
├── backend/
│   ├── .env           ← Your API key goes here
│   ├── main.py
│   ├── scripts/
│   └── ...
├── frontend/
└── README.md
```

### 4. Ingest DSM-5 Document

From the **project root**, run the ingestion script:

```bash
# Disable ChromaDB telemetry (optional but recommended)
export CHROMA_TELEMETRY_DISABLED=true

# Run ingestion
python backend/scripts/ingest.py
```

This will:
- Extract text from DSM-5.pdf
- Apply hybrid chunking (metadata + semantic)
- Generate embeddings via OpenAI
- Store in ChromaDB vector database

**⏱️ Duration**: 10-30 minutes depending on document size (first run only)

**Expected output:**
```
============ DSM-5 Document Ingestion Pipeline ============
Found DSM-5.pdf at: /path/to/DSM-5.pdf
Initializing components...
Database is empty. Creating new collection...

Stage 1: Loading and Processing DSM-5.pdf
============================================================
Processing Statistics:
  Total chunks: 1247
  Average chunk size: 1850 characters
  ...

Stage 2: Adding Documents to Vector Database
============================================================
Generating embeddings and storing in ChromaDB...
(This may take several minutes depending on document size)
  Batch 1/25 complete (50/1247 documents)
  ...
```

### 5. Start the Backend

From the **project root**, run:

```bash
# Start FastAPI backend
python backend/main.py
```

Backend will be available at:
- **API Base URL**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 6. Start the Frontend

In a **new terminal** from the **project root**:

```bash
# Start Streamlit frontend
streamlit run frontend/app.py
```

Frontend will be available at: **http://localhost:8501**

You should see the Streamlit app open automatically in your browser.

## 📁 Project Structure

```
Rag_DeviPriya/
├── DSM-5.pdf                   # ← Place your DSM-5 PDF here
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── database.py             # ChromaDB vector database manager
│   ├── rag_pipeline.py         # RAG implementation
│   ├── .env.example            # Environment variable template
│   ├── .env                    # ← Add your OpenAI API key here
│   ├── pyproject.toml          # Python dependencies (uv)
│   ├── uv.lock                 # Dependency lock file
│   ├── README.md               # Backend-specific documentation
│   ├── scripts/
│   │   └── ingest.py           # Document ingestion script
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── metadata_extractor.py    # Stage 1: Metadata extraction
│   │   ├── semantic_splitter.py     # Stage 2: Semantic chunking
│   │   └── hybrid_processor.py      # Orchestrator
│   ├── data/
│   │   └── chroma_db/          # Vector database (created after ingestion)
│   └── logs/                   # Application logs (created automatically)
├── frontend/
│   └── app.py                  # Streamlit web interface
├── .gitignore
├── .dockerignore
└── README.md                   # This file
```

## 🔧 Configuration

All configuration is managed through environment variables in `backend/.env`:

### Required Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |

### LLM & Embedding Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `EMBEDDING_MODEL` | Model for generating embeddings | text-embedding-3-small |
| `LLM_MODEL` | Language model for analysis | gpt-4o |
| `LLM_TEMPERATURE` | Model response creativity (0-1) | 0.3 |

### Chunking Settings (Document Processing)
| Variable | Description | Default |
|----------|-------------|---------|
| `SEMANTIC_BREAKPOINT_THRESHOLD` | Similarity threshold for semantic splits | 0.75 |
| `MIN_CHUNK_SIZE` | Minimum chunk size in characters | 500 |
| `MAX_CHUNK_SIZE` | Maximum chunk size in characters | 2000 |
| `CHUNK_OVERLAP` | Overlap between chunks in characters | 100 |

### RAG Settings (Retrieval & Search)
| Variable | Description | Default |
|----------|-------------|---------|
| `TOP_K_RESULTS` | Number of documents to retrieve | 5 |
| `SIMILARITY_THRESHOLD` | Minimum similarity score for results | 0.7 |
| `RERANK_ENABLED` | Enable result re-ranking | true |

### API Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API bind address | 0.0.0.0 |
| `API_PORT` | API port number | 8000 |
| `API_RELOAD` | Auto-reload on code changes (dev) | true |
| `STREAMLIT_PORT` | Streamlit frontend port | 8501 |
| `BACKEND_URL` | Backend URL for frontend | http://localhost:8000 |

### Safety & Features
| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_DISCLAIMER` | Show medical disclaimer | true |
| `REQUIRE_DISCLAIMER_ACCEPTANCE` | Require user to accept disclaimer | true |
| `LOG_USER_QUERIES` | Log user queries (privacy) | false |

**See `backend/.env.example` for all available options.**

## 🎯 Usage

### Web Interface

1. Open http://localhost:8501
2. Read and accept the medical disclaimer
3. Enter your symptom description
4. Optionally specify duration
5. Click "Analyze Symptoms"
6. Review the AI analysis and source evidence

### API Usage

You can also use the API directly:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "I have been feeling very sad and hopeless for the past month. I have no energy and cannot concentrate.",
    "duration": "1 month"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🔍 How It Works

### 1. Hybrid Document Processing

**Stage 1: Metadata Extraction**
- Identifies DSM-5 structure (disorders, categories, criteria)
- Extracts ICD codes, severity levels, specifiers
- Preserves diagnostic criteria relationships

**Stage 2: Semantic Chunking**
- Uses embeddings to find natural breakpoints
- Maintains context within chunks
- Validates chunk sizes and quality

### 2. RAG Pipeline

**Retrieval Phase:**
1. User submits symptom description
2. System generates query embedding
3. Performs similarity search in ChromaDB
4. Retrieves top-k relevant DSM-5 chunks
5. Filters by similarity threshold

**Generation Phase:**
1. Constructs prompt with:
   - System instructions (safety guardrails)
   - Retrieved DSM-5 context
   - User symptoms
   - Medical disclaimers
2. Sends to GPT-4o for analysis
3. Returns structured response with sources

### 3. Safety Measures

- Mandatory disclaimer acceptance
- Clear "not a diagnosis" messaging
- Emergency resource information
- No treatment recommendations
- Emphasis on professional consultation

## 📊 API Endpoints

### `POST /analyze`
Analyze symptoms against DSM-5 criteria

**Request:**
```json
{
  "symptoms": "string (required, min 10 chars)",
  "duration": "string (optional)"
}
```

**Response:**
```json
{
  "analysis": "AI-generated analysis",
  "disclaimer": "Medical disclaimer text",
  "sources": [
    {
      "content": "DSM-5 text chunk",
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

### `GET /health`
Check system health

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

## 🛠️ Development

### Running Tests

```bash
# Install dev dependencies
uv pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest tests/
```

### Logging

Logs are stored in `logs/app.log` with rotation (10 MB, 7 days retention).

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Re-ingesting Documents

To re-process the DSM-5 document:

```bash
python scripts/ingest.py
# Choose 'yes' when prompted to reset database
```

## 🐛 Troubleshooting

### Missing OpenAI API Key Error
**Error**: `Missing credentials. Please pass an 'api_key'... or set the 'OPENAI_API_KEY' environment variable`

**Solution:**
1. Copy `.env.example` to `.env` in the `backend/` directory
2. Add your actual OpenAI API key: `OPENAI_API_KEY=sk-your-key-here`
3. Save and restart the application

### OpenAI Client API Error
**Error**: `'OpenAI' object has no attribute 'create'`

**Solution:** This is a dependency version mismatch. The fix has been applied to `database.py`. Just update your code to the latest version from the repository.

### ChromaDB Telemetry Warning
**Warning**: `Failed to send telemetry event ClientCreateCollectionEvent`

**Solution:** This is non-fatal but can be suppressed with:
```bash
export CHROMA_TELEMETRY_DISABLED=true
python backend/scripts/ingest.py
```

### Backend won't start
- Ensure `.env` file exists in `backend/` with valid `OPENAI_API_KEY`
- Check if port 8000 is already in use: `lsof -i :8000`
- Review logs: `tail -f backend/logs/app.log`
- Ensure all dependencies are installed: `cd backend && uv sync`

### Ingestion script fails
- Verify `DSM-5.pdf` is in the **project root** (not in `backend/`)
- Check internet connection (needed for OpenAI API calls)
- Ensure your OpenAI API key has sufficient credits
- Try with telemetry disabled: `export CHROMA_TELEMETRY_DISABLED=true`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check `BACKEND_URL` in `backend/.env` (default: `http://localhost:8000`)
- Ensure both are on the same machine or network

### Vector database is empty
- Run ingestion script: `python backend/scripts/ingest.py` (from project root)
- Ensure `DSM-5.pdf` is in project root
- Wait for all batches to complete (may take 10-30 minutes)
- Check for errors in console output

### Slow response times
- Reduce `TOP_K_RESULTS` in `backend/.env` (default: 5)
- Check OpenAI API rate limits at https://platform.openai.com/account/rate-limits
- Verify network connectivity is stable

## 📚 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | RESTful API server |
| **Frontend** | Streamlit | Web interface |
| **LLM** | OpenAI GPT-4o | Symptom analysis & generation |
| **Embeddings** | OpenAI text-embedding-3-small | Vector embeddings |
| **Vector DB** | ChromaDB | Semantic search storage |
| **Orchestration** | LangChain | RAG pipeline coordination |
| **PDF Processing** | pypdf | DSM-5 document parsing |
| **Logging** | Loguru | Structured logging |
| **Package Manager** | uv | Fast Python dependency management |
| **Config Management** | Pydantic Settings | Environment variable validation |

## 🔒 Security & Privacy

- API keys stored in `.env` (not committed to git)
- No user data logging by default
- Local vector database (no external data sharing)
- HTTPS recommended for production deployment

## 📄 License

This project is for educational purposes. Ensure you have proper rights to use the DSM-5 content.

## 🤝 Contributing

This is a prototype system. For production use:
- Add comprehensive testing
- Implement user authentication
- Add rate limiting
- Deploy with proper security measures
- Consult legal/medical professionals

## 📞 Support & Resources

### Mental Health Resources
- **SAMHSA National Helpline**: 1-800-662-4357
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **NAMI**: https://www.nami.org/
- **Mental Health America**: https://www.mhanational.org/

### Technical Support
- Check logs in `logs/app.log`
- Review API docs at http://localhost:8000/docs
- Ensure all dependencies are installed

## ⚖️ Legal Notice

This system is provided "as is" without warranty of any kind. The creators and contributors are not liable for any damages or consequences arising from its use. This is NOT a medical device and should NOT be used for clinical decision-making.

---

**Built with ❤️ for educational purposes**

**Remember**: Always consult qualified healthcare professionals for mental health concerns.