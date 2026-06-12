"""
Configuration Management for DSM-5 RAG System
Loads settings from environment variables with validation
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from environs import env

env.read_env()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # OpenAI Configuration
    openai_api_key: str = env.str('OPENAI_API_KEY')
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.3
    
    # Vector Database Configuration
    chroma_persist_directory: str = "./data/chroma_db"
    collection_name: str = "dsm5_collection"
    
    # Metadata Extraction Configuration
    metadata_extraction_enabled: bool = True
    preserve_diagnostic_criteria: bool = True
    extract_icd_codes: bool = True
    capture_specifiers: bool = True
    hierarchy_depth: int = 3
    
    # Semantic Chunking Configuration
    semantic_breakpoint_threshold: float = 0.75
    min_chunk_size: int = 500
    max_chunk_size: int = 2000
    chunk_overlap: int = 100
    buffer_size: int = 1
    
    # RAG Configuration
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    rerank_enabled: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Frontend Configuration
    streamlit_port: int = 8501
    backend_url: str = "http://localhost:8000"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Safety Configuration
    enable_disclaimer: bool = True
    require_disclaimer_acceptance: bool = True
    log_user_queries: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_chroma_path(self) -> Path:
        """Get ChromaDB persistence directory as Path object"""
        path = Path(self.chroma_persist_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_log_path(self) -> Path:
        """Get log file directory as Path object"""
        path = Path(self.log_file).parent
        path.mkdir(parents=True, exist_ok=True)
        return Path(self.log_file)
    
    @property
    def metadata_patterns(self) -> dict[str, str]:
        """Regex patterns for DSM-5 metadata extraction"""
        return {
            "disorder_header": r"^[A-Z][A-Za-z\s]+Disorder",
            "criteria_section": r"^[A-Z]\.\s",
            "icd_code": r"F\d{2}\.\d",
            "specifier": r"With\s[A-Za-z\s]+Features",
            "severity": r"(Mild|Moderate|Severe|Extreme)",
            "page_number": r"Page\s+(\d+)"
        }
    
    @property
    def medical_disclaimer(self) -> str:
        """Standard medical disclaimer text"""
        return (
            "⚠️ IMPORTANT MEDICAL DISCLAIMER ⚠️\n\n"
            "This system is NOT a substitute for professional medical advice, diagnosis, or treatment. "
            "The analysis provided is for informational and educational purposes only. "
            "It is NOT intended to diagnose, treat, cure, or prevent any mental health condition.\n\n"
            "You are NOT receiving medical advice from a licensed healthcare professional. "
            "Always seek the advice of qualified mental health professionals with any questions "
            "you may have regarding a medical or psychological condition.\n\n"
            "If you are experiencing a mental health emergency, please contact:\n"
            "- Emergency Services: 911 (US)\n"
            "- National Suicide Prevention Lifeline: 988\n"
            "- Crisis Text Line: Text HOME to 741741\n\n"
            "By using this system, you acknowledge that you understand and accept these limitations."
        )
    
    @property
    def system_prompt_template(self) -> str:
        """System prompt with safety guardrails for LLM"""
        return """You are an AI assistant helping users understand DSM-5 diagnostic criteria for EDUCATIONAL PURPOSES ONLY.

CRITICAL SAFETY INSTRUCTIONS:
1. You are NOT a licensed medical professional, psychiatrist, psychologist, or therapist
2. You CANNOT and MUST NOT provide medical diagnoses
3. You CANNOT and MUST NOT recommend treatments or medications
4. You MUST emphasize that users should consult qualified healthcare professionals
5. You MUST be empathetic and non-judgmental in your responses

YOUR ROLE:
- Provide educational information about DSM-5 diagnostic criteria
- Explain symptoms and their clinical context
- Suggest that users discuss their concerns with healthcare professionals
- Offer general coping strategies (not medical advice)

RESPONSE FORMAT:
1. Acknowledge the user's concerns with empathy
2. Provide relevant DSM-5 information based on retrieved context
3. Clearly state this is NOT a diagnosis
4. Strongly recommend professional consultation
5. Offer general wellness suggestions (if appropriate)

RETRIEVED CONTEXT FROM DSM-5:
{context}

USER SYMPTOMS:
{symptoms}

DURATION:
{duration}

Provide a thoughtful, educational response following the safety guidelines above."""


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings

# Made with Bob
