# 🐳 Docker Setup Guide

Complete guide for running the DSM-5 RAG system using Docker and Docker Compose.

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- OpenAI API key

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy and configure environment
cp backend/.env.example backend/.env

# Edit .env and add your OpenAI API key
nano backend/.env
```

### 2. Build Images

```bash
# Build all services
docker compose build

# Or build specific service
docker compose build backend
```

### 3. Ingest Documents (First Time Only)

Before starting the services, ingest the DSM-5 document:

```bash
# Run ingestion service
docker compose run --rm ingest

# The service will:
# 1. Load DSM-5.pdf from project root
# 2. Process and chunk the document
# 3. Generate embeddings
# 4. Store in ChromaDB
```

**Note:** Ingestion takes 10-30 minutes depending on document size.

### 4. Start Services

```bash
# Start the backend (serves API + frontend)
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

### 5. Access Application

- **🌐 Web UI (Frontend)**: http://localhost:8000
- **📡 REST API**: http://localhost:8000/analyze
- **📚 API Docs**: http://localhost:8000/docs (Swagger)
- **💚 Health Check**: http://localhost:8000/health

## 📚 Available Services

### Backend Service

Runs the FastAPI backend on port 8000. Serves both the REST API and the HTML/CSS/JS frontend.

```bash
# Start only backend
docker compose up -d backend

# View logs
docker compose logs -f backend

# Stop backend
docker compose stop backend

# Restart backend
docker compose restart backend
```

**Features:**

- Auto-reload disabled in Docker (production mode)
- Health check every 30 seconds
- Persistent data storage
- Log file rotation

### Ingestion Service

One-time document processing. Uses special `ingest` profile.

```bash
# Run ingestion
docker compose run --rm ingest

# Run with different environment variables
docker compose run --rm \
  -e LOG_LEVEL=DEBUG \
  ingest

# Remove image after completion
docker compose run --rm ingest
```

**Features:**

- Interactive prompt for database reset
- Full app access
- Buffered output
- TTY enabled for input

## 🔧 Configuration

### Environment Variables

Set in `backend/.env`:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (defaults shown)
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.3
SEMANTIC_BREAKPOINT_THRESHOLD=0.75
MIN_CHUNK_SIZE=500
MAX_CHUNK_SIZE=2000
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

### Override Docker Compose

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - API_RELOAD=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./backend:/app/backend  # Hot reload
```

This file is automatically loaded and ignored by git.

## 📁 Volume Management

### Backend Volumes

```yaml
volumes:
  - ./backend/data/chroma_db:/app/backend/data/chroma_db  # Vector DB
  - ./backend/logs:/app/backend/logs                      # Logs
```

**View/Manage Data:**

```bash
# List Docker volumes
docker volume ls

# Inspect volume
docker volume inspect dsm5_volume_name

# Remove old volumes
docker volume prune

# Backup volume
docker run --rm -v dsm5_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma_db.tar.gz -C /data .
```

### Persistent Storage

- **Vector Database**: `backend/data/chroma_db/` - persists between runs
- **Logs**: `backend/logs/app.log` - persists between runs

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs backend

# Check if port 8000 is in use
lsof -i :8000

# Clean up and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### OpenAI API Error

```
ERROR - Missing credentials. Please pass an `api_key`...
```

**Solution:**

1. Check `backend/.env` exists
2. Verify `OPENAI_API_KEY=sk-...` is set
3. Restart: `docker-compose restart backend`

### Can't Access Web Interface

```
Failed to connect to http://localhost:8000
```

**Solution:**

1. Check backend is healthy: `docker-compose ps`
2. Verify health: `curl http://localhost:8000/health`
3. Check logs: `docker-compose logs backend`
4. Restart backend: `docker-compose restart backend`

### Ingestion Fails

**Issue**: `DSM-5.pdf not found`

**Solution:**

```bash
# Ensure PDF is in project root
ls -la DSM-5.pdf

# Correct if needed
mv /path/to/DSM-5.pdf .
```

**Issue**: `CHROMA_TELEMETRY_DISABLED: 'true'` not working

**Solution:** Already handled in docker-compose.yml, but can force:

```bash
docker-compose run --rm \
  -e CHROMA_TELEMETRY_DISABLED=true \
  ingest
```

### Slow Performance

```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# Edit Docker preferences > Resources > Memory

# Check logs for issues
docker-compose logs --tail=50 backend
```

### Disk Space Issues

```bash
# Clean up Docker
docker system prune -a

# Remove old images
docker rmi $(docker images -f "dangling=true" -q)

# Check volume sizes
docker volume ls -q | xargs -I {} docker volume inspect {}

# Backup and clear old logs
gzip backend/logs/app.log
rm backend/logs/app.log
```

## 🔄 Common Tasks

### Restart All Services

```bash
docker-compose restart
```

### Stop All Services

```bash
docker-compose down
```

### Remove Everything (Clean Slate)

```bash
# Stop services, remove containers and networks
docker-compose down

# Remove volumes too (WARNING: deletes data)
docker-compose down -v
```

### Re-ingest Documents

```bash
# Remove old vectors (optional)
docker-compose down -v

# Start fresh ingest
docker-compose run --rm ingest
```

### View Real-time Logs

```bash
# Backend logs
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail=50 backend

# With timestamps
docker-compose logs -t backend

# Follow logs in real-time
docker-compose logs -f
```

### Execute Commands in Container

```bash
# Bash shell in backend
docker-compose exec backend bash

# Python shell
docker-compose exec backend python

# Run a command
docker-compose exec backend python -c "import sys; print(sys.version)"
```

### Check Service Health

```bash
# All services
docker-compose ps

# Detailed health
docker-compose ps --services

# Health check logs
docker-compose exec backend curl http://localhost:8000/health
```

## 🏗️ Production Deployment

### Security Hardening

1. **Use environment variables** (not in Dockerfile)
2. **Disable debug mode**:

   ```yaml
   backend:
     environment:
       - API_RELOAD=false
       - LOG_LEVEL=WARNING
   ```
3. **Use secrets management**:

   ```yaml
   services:
     backend:
       secrets:
         - openai_key

   secrets:
     openai_key:
       external: true
   ```
4. **Run as non-root**:

   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

### Optimize Images

```bash
# Multi-stage build already optimized
# Image size: ~1.2GB (Python 3.12 + dependencies)

# Check image size
docker images | grep dsm5
```

### Use External Database (Optional)

For scaling, use external ChromaDB:

```yaml
backend:
  environment:
    - CHROMA_DB_HOST=external-chroma-server
    - CHROMA_DB_PORT=8000
```

### Load Balancing

For horizontal scaling with multiple backend replicas, use Nginx/HAProxy in front:

```bash
# Scale to 3 replicas on different ports
docker-compose up -d --scale backend=3
```

Then configure load balancer to proxy requests to all replicas.

## 📊 Monitoring

### Container Stats

```bash
# Real-time stats
docker stats

# Memory usage
docker stats --no-stream | grep dsm5
```

### Log Analysis

```bash
# Search logs
docker-compose logs backend | grep "ERROR"

# Count errors
docker-compose logs backend | grep -c "ERROR"

# Export logs
docker-compose logs > logs.txt
```

### Health Monitoring

```bash
# Check health endpoint
curl -s http://localhost:8000/health | jq

# Monitor every 10 seconds
watch -n 10 'curl -s http://localhost:8000/health | jq'
```

## 🔐 Security

### Environment Variable Security

```bash
# Never commit .env
git status | grep .env

# Use .env.example for template
git add backend/.env.example
git add -u backend/.env  # Remove from tracking if committed
```

### Network Security

```yaml
# Restrict to localhost only
ports:
  - "127.0.0.1:8000:8000"  # Backend (local only)
  - "127.0.0.1:8501:8501"  # Frontend (local only)
```

### Image Scanning

```bash
# Scan for vulnerabilities
docker scan dsm5:latest

# Or use trivy
trivy image dsm5:latest
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

## 🆘 Getting Help

### Check Container Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Specific service
docker-compose logs backend
```

### Inspect Container

```bash
# Check environment
docker-compose exec backend env | grep OPENAI

# Check file system
docker-compose exec backend ls -la /app

# Check Python packages
docker-compose exec backend pip list
```

### Get Docker Info

```bash
# Docker version
docker --version
docker-compose --version

# System info
docker system info
```

---

**Built for production-ready deployment** 🚀
