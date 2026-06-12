"""
RAG Pipeline Implementation
Retrieval-Augmented Generation for DSM-5 Analysis
"""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from loguru import logger

from config import get_settings
from database import get_vector_db
from models import (
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    SourceDocument
)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for symptom analysis"""
    
    def __init__(self):
        """Initialize RAG pipeline components"""
        self.settings = get_settings()
        self.vector_db = get_vector_db()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            openai_api_key=self.settings.openai_api_key
        )
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(
            self.settings.system_prompt_template
        )
        
        # Create output parser
        self.output_parser = StrOutputParser()
        
        logger.info(f"RAG pipeline initialized with model: {self.settings.llm_model}")
    
    def retrieve_context(
        self,
        query: str,
        k: Optional[int] = None
    ) -> tuple[List[SourceDocument], str]:
        """
        Retrieve relevant context from vector database
        
        Args:
            query: User's symptom description
            k: Number of documents to retrieve
            
        Returns:
            Tuple of (source_documents, formatted_context)
        """
        try:
            # Perform similarity search
            source_docs = self.vector_db.similarity_search(
                query=query,
                k=k or self.settings.top_k_results
            )
            
            if not source_docs:
                logger.warning("No relevant documents found in vector database")
                return [], "No relevant DSM-5 criteria found."
            
            # Format context for LLM
            context_parts = []
            for idx, doc in enumerate(source_docs, 1):
                context_part = f"[Source {idx}]"
                
                if doc.disorder_name:
                    context_part += f"\nDisorder: {doc.disorder_name}"
                
                if doc.disorder_category:
                    context_part += f"\nCategory: {doc.disorder_category}"
                
                if doc.criteria_label:
                    context_part += f"\nCriteria: {doc.criteria_label}"
                
                if doc.icd_code:
                    context_part += f"\nICD Code: {doc.icd_code}"
                
                context_part += f"\n\nContent:\n{doc.content}\n"
                context_part += f"\n(Relevance: {doc.relevance_score:.2%})\n"
                
                context_parts.append(context_part)
            
            formatted_context = "\n" + "="*80 + "\n".join(context_parts)
            
            logger.info(f"Retrieved {len(source_docs)} relevant documents")
            return source_docs, formatted_context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return [], "Error retrieving relevant information."
    
    def generate_analysis(
        self,
        symptoms: str,
        duration: Optional[str],
        context: str
    ) -> str:
        """
        Generate analysis using LLM with retrieved context
        
        Args:
            symptoms: User's symptom description
            duration: Duration of symptoms
            context: Retrieved DSM-5 context
            
        Returns:
            Generated analysis text
        """
        try:
            # Create the chain using LCEL (LangChain Expression Language)
            chain = (
                {
                    "context": lambda x: x["context"],
                    "symptoms": lambda x: x["symptoms"],
                    "duration": lambda x: x["duration"]
                }
                | self.prompt
                | self.llm
                | self.output_parser
            )
            
            # Invoke the chain
            analysis = chain.invoke({
                "context": context,
                "symptoms": symptoms,
                "duration": duration or "Not specified"
            })
            
            logger.info("Analysis generated successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return (
                "I apologize, but I encountered an error while analyzing your symptoms. "
                "Please try again or consult with a qualified healthcare professional."
            )
    
    def analyze_symptoms(
        self,
        request: SymptomAnalysisRequest
    ) -> SymptomAnalysisResponse:
        """
        Complete RAG pipeline: retrieve context and generate analysis
        
        Args:
            request: Symptom analysis request
            
        Returns:
            Symptom analysis response with sources
        """
        logger.info("Starting symptom analysis")
        
        try:
            # Step 1: Retrieve relevant context
            source_docs, formatted_context = self.retrieve_context(
                query=request.symptoms
            )
            
            # Step 2: Generate analysis
            analysis = self.generate_analysis(
                symptoms=request.symptoms,
                duration=request.duration,
                context=formatted_context
            )
            
            # Step 3: Create response
            response = SymptomAnalysisResponse(
                analysis=analysis,
                disclaimer=self.settings.medical_disclaimer,
                sources=source_docs,
                model_used=self.settings.llm_model
            )
            
            logger.info("Symptom analysis completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in symptom analysis pipeline: {e}")
            
            # Return error response with disclaimer
            return SymptomAnalysisResponse(
                analysis=(
                    "I apologize, but I encountered an error while processing your request. "
                    "This could be due to a temporary issue with the system. "
                    "Please try again later or consult with a qualified healthcare professional "
                    "for proper evaluation of your symptoms."
                ),
                disclaimer=self.settings.medical_disclaimer,
                sources=[],
                model_used=self.settings.llm_model
            )
    
    def health_check(self) -> bool:
        """Check if RAG pipeline is healthy"""
        try:
            # Check vector database
            if not self.vector_db.health_check():
                return False
            
            # Check if collection has documents
            stats = self.vector_db.get_collection_stats()
            if stats["document_count"] == 0:
                logger.warning("Vector database is empty")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global RAG pipeline instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create global RAG pipeline instance"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline

# Made with Bob
