"""
Pydantic Models for Request/Response Validation
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class SymptomAnalysisRequest(BaseModel):
    """Request model for symptom analysis"""
    
    symptoms: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Description of psychological symptoms",
        examples=["I've been feeling very sad and hopeless for the past 3 weeks. I have no energy and can't sleep well."]
    )
    
    duration: Optional[str] = Field(
        None,
        max_length=200,
        description="Duration of symptoms",
        examples=["3 weeks", "2 months", "6 months"]
    )
    
    @validator('symptoms')
    def validate_symptoms(cls, v: str) -> str:
        """Validate symptoms field"""
        if not v or v.isspace():
            raise ValueError("Symptoms description cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": "I've been feeling extremely sad and hopeless for the past month. I have no energy, can't concentrate on work, and have lost interest in activities I used to enjoy. My sleep is disrupted, and I often wake up early in the morning.",
                "duration": "1 month"
            }
        }


class SourceDocument(BaseModel):
    """Model for source document chunks"""
    
    content: str = Field(..., description="Content of the source chunk")
    page_number: Optional[int] = Field(None, description="Page number in DSM-5")
    disorder_name: Optional[str] = Field(None, description="Name of the disorder")
    disorder_category: Optional[str] = Field(None, description="Category of disorder")
    section_type: Optional[str] = Field(None, description="Type of section (e.g., diagnostic_criteria)")
    criteria_label: Optional[str] = Field(None, description="Criteria label (e.g., Criterion A)")
    icd_code: Optional[str] = Field(None, description="ICD diagnostic code")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "A. Five (or more) of the following symptoms have been present during the same 2-week period...",
                "page_number": 160,
                "disorder_name": "Major Depressive Disorder",
                "disorder_category": "Depressive Disorders",
                "section_type": "diagnostic_criteria",
                "criteria_label": "Criterion A",
                "icd_code": "F32.x",
                "relevance_score": 0.89
            }
        }


class SymptomAnalysisResponse(BaseModel):
    """Response model for symptom analysis"""
    
    analysis: str = Field(..., description="AI-generated analysis of symptoms")
    disclaimer: str = Field(..., description="Medical disclaimer text")
    sources: List[SourceDocument] = Field(
        default_factory=list,
        description="Source documents from DSM-5 used in analysis"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of analysis"
    )
    model_used: str = Field(default="gpt-4o", description="LLM model used for analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis": "Based on the symptoms you've described, there are several DSM-5 criteria that may be relevant...",
                "disclaimer": "⚠️ IMPORTANT: This is NOT a medical diagnosis...",
                "sources": [
                    {
                        "content": "A. Five (or more) of the following symptoms...",
                        "page_number": 160,
                        "disorder_name": "Major Depressive Disorder",
                        "relevance_score": 0.89
                    }
                ],
                "timestamp": "2024-01-15T10:30:00Z",
                "model_used": "gpt-4o"
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(..., description="Overall system status")
    vector_db_status: str = Field(..., description="Vector database connection status")
    documents_indexed: int = Field(..., ge=0, description="Number of documents in vector DB")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "vector_db_status": "connected",
                "documents_indexed": 1247,
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors"""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input provided",
                "detail": "Symptoms field must be at least 10 characters",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ChunkMetadata(BaseModel):
    """Metadata model for document chunks during ingestion"""
    
    disorder_name: Optional[str] = None
    disorder_category: Optional[str] = None
    section_type: Optional[str] = None
    criteria_label: Optional[str] = None
    page_number: Optional[int] = None
    icd_code: Optional[str] = None
    parent_section: Optional[str] = None
    has_specifiers: bool = False
    severity_levels: List[str] = Field(default_factory=list)
    chunk_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "disorder_name": "Major Depressive Disorder",
                "disorder_category": "Depressive Disorders",
                "section_type": "diagnostic_criteria",
                "criteria_label": "Criterion A",
                "page_number": 160,
                "icd_code": "F32.x",
                "parent_section": "Mood Disorders",
                "has_specifiers": True,
                "severity_levels": ["mild", "moderate", "severe"],
                "chunk_id": "uuid-string"
            }
        }

# Made with Bob
