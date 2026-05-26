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

### 1. Clone and Setup

```bash
# Clone the repository (or extract the files)
cd dsm5-rag-system

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Prepare DSM-5 Document

Place your `DSM-5.pdf` file in the project root directory:
```
dsm5-rag-system/
├── DSM-5.pdf          ← Place here
├── backend/
├── frontend/
└── ...
```

### 4. Ingest DSM-5 Document

Run the ingestion script to process the PDF and populate the vector database:

```bash
python scripts/ingest.py
```

This will:
- Extract text from DSM-5.pdf
- Apply hybrid chunking (metadata + semantic)
- Generate embeddings
- Store in ChromaDB

**Note**: This process may take 10-30 minutes depending on document size.

### 5. Start the Backend

```bash
# Make script executable (Linux/Mac)
chmod +x scripts/start_backend.sh

# Start backend
./scripts/start_backend.sh

# Or run directly
python backend/main.py
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 6. Start the Frontend

In a new terminal:

```bash
# Make script executable (Linux/Mac)
chmod +x scripts/start_frontend.sh

# Start frontend
./scripts/start_frontend.sh

# Or run directly
streamlit run frontend/app.py
```

Frontend will be available at: http://localhost:8501

## 📁 Project Structure

```
dsm5-rag-system/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── database.py             # ChromaDB management
│   ├── rag_pipeline.py         # RAG implementation
│   └── chunking/
│       ├── __init__.py
│       ├── metadata_extractor.py    # Stage 1: Metadata extraction
│       ├── semantic_splitter.py     # Stage 2: Semantic chunking
│       └── hybrid_processor.py      # Orchestrator
├── frontend/
│   └── app.py                  # Streamlit UI
├── scripts/
│   ├── ingest.py               # Document ingestion
│   ├── start_backend.sh        # Backend startup
│   └── start_frontend.sh       # Frontend startup
├── data/
│   └── chroma_db/              # Vector database (created after ingestion)
├── logs/                       # Application logs (created automatically)
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata for uv
├── .env.example                # Environment template
├── .gitignore
└── README.md
```

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

### Core Settings
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)
- `LLM_MODEL`: Language model (default: gpt-4o)
- `LLM_TEMPERATURE`: Model temperature (default: 0.3)

### Chunking Settings
- `SEMANTIC_BREAKPOINT_THRESHOLD`: Similarity threshold for semantic splits (default: 0.75)
- `MIN_CHUNK_SIZE`: Minimum chunk size in characters (default: 500)
- `MAX_CHUNK_SIZE`: Maximum chunk size in characters (default: 2000)

### RAG Settings
- `TOP_K_RESULTS`: Number of documents to retrieve (default: 5)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.7)

See `.env.example` for all available options.

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

### Backend won't start
- Check if `.env` file exists with valid `OPENAI_API_KEY`
- Ensure port 8000 is not in use
- Check logs in `logs/app.log`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check `BACKEND_URL` in `.env` (default: http://localhost:8000)

### Vector database is empty
- Run ingestion script: `python scripts/ingest.py`
- Ensure `DSM-5.pdf` is in project root
- Check ingestion logs for errors

### Slow response times
- Reduce `TOP_K_RESULTS` in `.env`
- Use smaller embedding model
- Check OpenAI API rate limits

## 📚 Technology Stack

- **Backend**: FastAPI 0.109.0
- **Frontend**: Streamlit 1.30.0
- **LLM**: OpenAI GPT-4o
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: ChromaDB 0.4.22
- **Orchestration**: LangChain 0.1.4
- **PDF Processing**: pypdf 4.0.1
- **Logging**: Loguru 0.7.2

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