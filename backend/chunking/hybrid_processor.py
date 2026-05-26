"""
Hybrid Document Processor
Orchestrates metadata extraction and semantic chunking
"""

import uuid
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from pypdf import PdfReader
from loguru import logger

from backend.config import get_settings
from backend.models import ChunkMetadata
from backend.chunking.metadata_extractor import MetadataExtractor, DSM5Section
from backend.chunking.semantic_splitter import SemanticSplitter


class HybridDocumentProcessor:
    """Processes documents using hybrid metadata + semantic approach"""
    
    def __init__(self):
        """Initialize hybrid processor"""
        self.settings = get_settings()
        self.metadata_extractor = MetadataExtractor()
        self.semantic_splitter = SemanticSplitter()
        logger.info("Hybrid document processor initialized")
    
    def load_pdf(self, pdf_path: str) -> Tuple[str, Dict[int, str]]:
        """
        Load PDF and extract text with page mapping
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (full_text, page_map)
        """
        try:
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Loading PDF: {pdf_path}")
            reader = PdfReader(str(pdf_path_obj))
            
            full_text = ""
            page_map = {}
            
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        page_map[page_num] = page_text
                        full_text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
            
            logger.info(f"Extracted text from {len(page_map)} pages")
            return full_text, page_map
            
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise
    
    def process_document(
        self,
        pdf_path: str
    ) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
        """
        Process document using hybrid approach
        
        Args:
            pdf_path: Path to DSM-5 PDF file
            
        Returns:
            Tuple of (texts, metadatas, ids)
        """
        logger.info("Starting hybrid document processing")
        
        # Stage 1: Load PDF
        full_text, page_map = self.load_pdf(pdf_path)
        
        # Stage 2: Extract metadata and split by disorders
        if self.settings.metadata_extraction_enabled:
            sections = self.metadata_extractor.split_by_disorders(full_text, page_map)
            logger.info(f"Extracted {len(sections)} disorder sections")
        else:
            # Fallback: treat entire document as one section
            sections = [DSM5Section(
                content=full_text,
                start_page=1,
                end_page=len(page_map),
                section_type="general"
            )]
        
        # Stage 3: Apply semantic chunking to each section
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        for section in sections:
            # Skip empty sections
            if not section.content or len(section.content.strip()) < 100:
                continue
            
            # Add context prefix for better chunk understanding
            context_prefix = self._create_context_prefix(section)
            
            # Semantic chunking
            chunks = self.semantic_splitter.split_text(section.content)
            
            logger.debug(f"Section '{section.disorder_name or 'Unknown'}' split into {len(chunks)} chunks")
            
            # Create metadata for each chunk
            for chunk_idx, chunk in enumerate(chunks):
                # Estimate page number for this chunk
                page_num = self._estimate_page_number(chunk, page_map)
                
                # Create metadata
                metadata = self.metadata_extractor.create_chunk_metadata(
                    text=chunk,
                    section=section,
                    page_number=page_num
                )
                
                # Add chunk ID
                chunk_id = str(uuid.uuid4())
                metadata.chunk_id = chunk_id
                
                # Convert to dict for ChromaDB
                metadata_dict = self._metadata_to_dict(metadata)
                
                # Add context if available
                if context_prefix and self.settings.preserve_diagnostic_criteria:
                    chunk_with_context = f"{context_prefix}\n\n{chunk}"
                else:
                    chunk_with_context = chunk
                
                all_texts.append(chunk_with_context)
                all_metadatas.append(metadata_dict)
                all_ids.append(chunk_id)
        
        logger.info(f"Hybrid processing complete: {len(all_texts)} chunks created")
        
        return all_texts, all_metadatas, all_ids
    
    def _create_context_prefix(self, section: DSM5Section) -> str:
        """Create context prefix for chunks"""
        parts = []
        
        if section.disorder_category:
            parts.append(f"Category: {section.disorder_category}")
        
        if section.disorder_name:
            parts.append(f"Disorder: {section.disorder_name}")
        
        if section.icd_code:
            parts.append(f"ICD Code: {section.icd_code}")
        
        return " | ".join(parts) if parts else ""
    
    def _estimate_page_number(
        self,
        chunk: str,
        page_map: Dict[int, str]
    ) -> Optional[int]:
        """Estimate page number for a chunk by finding best match"""
        # Try to extract page number from chunk text
        page_num = self.metadata_extractor.extract_page_number(chunk)
        if page_num:
            return page_num
        
        # Fallback: find page with most overlap
        max_overlap = 0
        best_page = None
        
        chunk_words = set(chunk.lower().split()[:50])  # Use first 50 words
        
        for page_num, page_text in page_map.items():
            page_words = set(page_text.lower().split()[:100])
            overlap = len(chunk_words & page_words)
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_page = page_num
        
        return best_page
    
    def _metadata_to_dict(self, metadata: ChunkMetadata) -> Dict[str, Any]:
        """Convert ChunkMetadata to dictionary for ChromaDB"""
        return {
            "disorder_name": metadata.disorder_name or "",
            "disorder_category": metadata.disorder_category or "",
            "section_type": metadata.section_type or "",
            "criteria_label": metadata.criteria_label or "",
            "page_number": metadata.page_number or 0,
            "icd_code": metadata.icd_code or "",
            "parent_section": metadata.parent_section or "",
            "has_specifiers": metadata.has_specifiers,
            "severity_levels": ",".join(metadata.severity_levels) if metadata.severity_levels else "",
            "chunk_id": metadata.chunk_id or ""
        }
    
    def get_processing_stats(self, texts: List[str]) -> Dict[str, Any]:
        """Get statistics about processed documents"""
        if not texts:
            return {
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }
        
        chunk_sizes = [len(text) for text in texts]
        
        return {
            "total_chunks": len(texts),
            "avg_chunk_size": sum(chunk_sizes) // len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }

# Made with Bob
