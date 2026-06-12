#!/bin/bash

# Start Frontend Script for DSM-5 RAG System

echo "=========================================="
echo "Starting DSM-5 RAG System Frontend"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file from .env.example:"
    echo "  cp .env.example .env"
    exit 1
fi

# Install/update dependencies with uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Check if backend is running
echo "Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is running"
else
    echo "⚠️  WARNING: Backend is not responding at http://localhost:8000"
    echo "Please start the backend first:"
    echo "  ./scripts/start_backend.sh"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Streamlit frontend
echo ""
echo "=========================================="
echo "Starting Streamlit Frontend..."
echo "UI will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

streamlit run frontend/app.py

# Made with Bob
