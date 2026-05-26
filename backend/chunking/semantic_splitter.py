"""
Semantic Splitter for DSM-5 Documents
Stage 2: Apply semantic chunking within metadata sections
"""

from typing import List, Optional
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

from backend.config import get_settings


class SemanticSplitter:
    """Performs semantic-aware text splitting"""
    
    def __init__(self):
        """Initialize semantic splitter with embeddings"""
        self.settings = get_settings()
        
        # Initialize embeddings for semantic chunking
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            openai_api_key=self.settings.openai_api_key
        )
        
        # Initialize semantic chunker
        self.semantic_chunker = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=self.settings.semantic_breakpoint_threshold
        )
        
        # Fallback to recursive splitter for very large sections
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.max_chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info("Semantic splitter initialized")
    
    def split_text(
        self,
        text: str,
        use_semantic: bool = True
    ) -> List[str]:
        """
        Split text into chunks using semantic or recursive splitting
        
        Args:
            text: Text to split
            use_semantic: Whether to use semantic chunking (default: True)
            
        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []
        
        try:
            # Use semantic chunking for better context preservation
            if use_semantic and len(text) <= self.settings.max_chunk_size * 3:
                chunks = self.semantic_chunker.split_text(text)
                logger.debug(f"Semantic chunking produced {len(chunks)} chunks")
            else:
                # Fallback to recursive for very large texts
                chunks = self.recursive_splitter.split_text(text)
                logger.debug(f"Recursive chunking produced {len(chunks)} chunks")
            
            # Validate and filter chunks
            validated_chunks = self._validate_chunks(chunks)
            
            return validated_chunks
            
        except Exception as e:
            logger.warning(f"Semantic chunking failed, falling back to recursive: {e}")
            chunks = self.recursive_splitter.split_text(text)
            return self._validate_chunks(chunks)
    
    def _validate_chunks(self, chunks: List[str]) -> List[str]:
        """
        Validate and filter chunks based on size constraints
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Filtered list of valid chunks
        """
        validated = []
        
        for chunk in chunks:
            chunk = chunk.strip()
            
            # Skip empty chunks
            if not chunk:
                continue
            
            # Check minimum size
            if len(chunk) < self.settings.min_chunk_size:
                # Try to merge with previous chunk if possible
                if validated and len(validated[-1]) + len(chunk) <= self.settings.max_chunk_size:
                    validated[-1] = f"{validated[-1]}\n\n{chunk}"
                    logger.debug(f"Merged small chunk ({len(chunk)} chars) with previous")
                else:
                    # Keep it if it's the only chunk or has meaningful content
                    if len(chunk) > 100 or not validated:
                        validated.append(chunk)
                continue
            
            # Check maximum size
            if len(chunk) > self.settings.max_chunk_size:
                # Split large chunk using recursive splitter
                sub_chunks = self.recursive_splitter.split_text(chunk)
                validated.extend([c.strip() for c in sub_chunks if c.strip()])
                logger.debug(f"Split oversized chunk ({len(chunk)} chars) into {len(sub_chunks)} sub-chunks")
            else:
                validated.append(chunk)
        
        logger.debug(f"Validated {len(validated)} chunks from {len(chunks)} original chunks")
        return validated
    
    def split_with_context(
        self,
        text: str,
        context_prefix: Optional[str] = None
    ) -> List[str]:
        """
        Split text and add context prefix to each chunk
        
        Args:
            text: Text to split
            context_prefix: Optional context to prepend to each chunk
            
        Returns:
            List of chunks with context
        """
        chunks = self.split_text(text)
        
        if context_prefix:
            chunks = [f"{context_prefix}\n\n{chunk}" for chunk in chunks]
        
        return chunks
    
    def estimate_chunks(self, text: str) -> int:
        """
        Estimate number of chunks without actually splitting
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated number of chunks
        """
        if not text:
            return 0
        
        # Rough estimation based on average chunk size
        avg_chunk_size = (self.settings.min_chunk_size + self.settings.max_chunk_size) // 2
        estimated = max(1, len(text) // avg_chunk_size)
        
        return estimated

# Made with Bob
