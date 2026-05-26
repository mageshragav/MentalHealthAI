#!/bin/bash

# Start Backend Script for DSM-5 RAG System

echo "=========================================="
echo "Starting DSM-5 RAG System Backend"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file from .env.example:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Install/update dependencies with uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Check if vector database is populated
if [ ! -d "data/chroma_db" ]; then
    echo ""
    echo "⚠️  WARNING: Vector database not found!"
    echo "Please run the ingestion script first:"
    echo "  python scripts/ingest.py"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start FastAPI backend
echo ""
echo "=========================================="
echo "Starting FastAPI Backend..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python backend/main.py

# Made with Bob
