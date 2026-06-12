"""
ChromaDB Vector Database Management
Handles vector storage, retrieval, and collection management
"""

from typing import List, Dict, Any, Optional
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from loguru import logger

from config import get_settings
from models import ChunkMetadata, SourceDocument


class VectorDatabase:
    """Manages ChromaDB vector database operations"""

    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=self.settings.openai_api_key
        )
        
        # Initialize ChromaDB client with persistence
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.settings.get_chroma_path()),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # Initialize or get collection
        self.collection_name = self.settings.collection_name
        self.vectorstore: Optional[Chroma] = None
        
        logger.info(f"ChromaDB initialized at {self.settings.get_chroma_path()}")
    
    def initialize_collection(self) -> None:
        """Initialize or load existing collection"""
        try:
            # Try to get existing collection
            collection = self.chroma_client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
            
            # Initialize LangChain Chroma wrapper
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
        except Exception as e:
            logger.warning(f"Collection not found, will be created during ingestion: {e}")
            self.vectorstore = None
    
    def create_collection(self, reset: bool = False) -> None:
        """Create a new collection (optionally reset existing)"""
        try:
            if reset:
                try:
                    self.chroma_client.delete_collection(name=self.collection_name)
                    logger.info(f"Deleted existing collection: {self.collection_name}")
                except Exception:
                    pass
            
            # Create new collection through LangChain
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            logger.info(f"Created new collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector database
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        if not self.vectorstore:
            self.create_collection()
        
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]
            
            # Add documents to vectorstore
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to collection")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SourceDocument]:
        """
        Perform similarity search on the vector database
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of SourceDocument objects with relevance scores
        """
        if not self.vectorstore:
            self.initialize_collection()
            if not self.vectorstore:
                logger.error("Vector database not initialized")
                return []
        
        try:
            k = k or self.settings.top_k_results
            
            # Perform similarity search with scores
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=filter_dict
            )
            
            # Convert to SourceDocument objects
            source_docs = []
            for doc, score in results:
                # Only include results above similarity threshold
                if score >= self.settings.similarity_threshold:
                    source_doc = SourceDocument(
                        content=doc.page_content,
                        page_number=doc.metadata.get("page_number"),
                        disorder_name=doc.metadata.get("disorder_name"),
                        disorder_category=doc.metadata.get("disorder_category"),
                        section_type=doc.metadata.get("section_type"),
                        criteria_label=doc.metadata.get("criteria_label"),
                        icd_code=doc.metadata.get("icd_code"),
                        relevance_score=round(score, 4)
                    )
                    source_docs.append(source_doc)
            
            logger.info(f"Found {len(source_docs)} relevant documents for query")
            return source_docs
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            if not self.vectorstore:
                self.initialize_collection()
            
            if self.vectorstore:
                collection = self.chroma_client.get_collection(name=self.collection_name)
                count = collection.count()
                
                return {
                    "collection_name": self.collection_name,
                    "document_count": count,
                    "status": "connected"
                }
            else:
                return {
                    "collection_name": self.collection_name,
                    "document_count": 0,
                    "status": "not_initialized"
                }
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "status": "error"
            }
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self.vectorstore = None
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if database is healthy and accessible"""
        try:
            stats = self.get_collection_stats()
            return stats["status"] in ["connected", "not_initialized"]
        except Exception:
            return False


# Global database instance
_db_instance: Optional[VectorDatabase] = None


def get_vector_db() -> VectorDatabase:
    """Get or create global vector database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = VectorDatabase()
        _db_instance.initialize_collection()
    return _db_instance

# Made with Bob
