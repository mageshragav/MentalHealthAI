"""
FastAPI Backend for DSM-5 Psychological Analysis System
Main application entry point
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from config import get_settings
from models import (
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    HealthCheckResponse,
    ErrorResponse
)
from rag_pipeline import get_rag_pipeline
from database import get_vector_db


# Configure logging
settings = get_settings()
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.get_log_path(),
    rotation="10 MB",
    retention="7 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting DSM-5 RAG System API")
    logger.info(f"Using model: {settings.llm_model}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    
    # Initialize components
    try:
        vector_db = get_vector_db()
        rag_pipeline = get_rag_pipeline()
        
        # Check if database is populated
        stats = vector_db.get_collection_stats()
        if stats["document_count"] == 0:
            logger.warning(
                "Vector database is empty! Please run the ingestion script: "
                "python scripts/ingest.py"
            )
        else:
            logger.info(f"Vector database loaded with {stats['document_count']} documents")
        
        logger.info("API startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DSM-5 RAG System API")


# Create FastAPI app
app = FastAPI(
    title="DSM-5 Psychological Analysis System",
    description="RAG-based system for analyzing psychological symptoms against DSM-5 criteria",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "DSM-5 Psychological Analysis System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint
    
    Returns system status and database statistics
    """
    try:
        vector_db = get_vector_db()
        rag_pipeline = get_rag_pipeline()
        
        # Get database stats
        stats = vector_db.get_collection_stats()
        
        # Check pipeline health
        pipeline_healthy = rag_pipeline.health_check()
        
        # Determine overall status
        if pipeline_healthy and stats["document_count"] > 0:
            overall_status = "healthy"
        elif stats["document_count"] == 0:
            overall_status = "warning - database empty"
        else:
            overall_status = "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            vector_db_status=stats["status"],
            documents_indexed=stats["document_count"]
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            vector_db_status="error",
            documents_indexed=0
        )


@app.post(
    "/analyze",
    response_model=SymptomAnalysisResponse,
    tags=["Analysis"],
    status_code=status.HTTP_200_OK
)
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze psychological symptoms using RAG pipeline
    
    This endpoint:
    1. Retrieves relevant DSM-5 diagnostic criteria from the vector database
    2. Uses GPT-4o to analyze symptoms in context of retrieved criteria
    3. Returns analysis with source citations and medical disclaimer
    
    **IMPORTANT**: This is NOT a medical diagnosis. Always consult qualified healthcare professionals.
    """
    try:
        logger.info(f"Received analysis request for symptoms: {request.symptoms[:100]}...")
        
        # Get RAG pipeline
        rag_pipeline = get_rag_pipeline()
        
        # Check if system is ready
        if not rag_pipeline.health_check():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System is not ready. Vector database may be empty. Please run ingestion script."
            )
        
        # Perform analysis
        response = rag_pipeline.analyze_symptoms(request)
        
        logger.info("Analysis completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            detail=str(exc)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message="An unexpected error occurred",
            detail=str(exc)
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )

# Made with Bob
