"""
Metadata Extractor for DSM-5 Documents
Stage 1: Extract structural metadata from DSM-5 PDF
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from backend.config import get_settings
from backend.models import ChunkMetadata


@dataclass
class DSM5Section:
    """Represents a section in DSM-5 document"""
    content: str
    start_page: int
    end_page: int
    disorder_name: Optional[str] = None
    disorder_category: Optional[str] = None
    section_type: Optional[str] = None
    icd_code: Optional[str] = None
    parent_section: Optional[str] = None


class MetadataExtractor:
    """Extracts metadata from DSM-5 document structure"""
    
    def __init__(self):
        """Initialize metadata extractor with patterns"""
        self.settings = get_settings()
        self.patterns = self.settings.metadata_patterns
        
        # DSM-5 disorder categories (major sections)
        self.disorder_categories = [
            "Neurodevelopmental Disorders",
            "Schizophrenia Spectrum and Other Psychotic Disorders",
            "Bipolar and Related Disorders",
            "Depressive Disorders",
            "Anxiety Disorders",
            "Obsessive-Compulsive and Related Disorders",
            "Trauma- and Stressor-Related Disorders",
            "Dissociative Disorders",
            "Somatic Symptom and Related Disorders",
            "Feeding and Eating Disorders",
            "Elimination Disorders",
            "Sleep-Wake Disorders",
            "Sexual Dysfunctions",
            "Gender Dysphoria",
            "Disruptive, Impulse-Control, and Conduct Disorders",
            "Substance-Related and Addictive Disorders",
            "Neurocognitive Disorders",
            "Personality Disorders",
            "Paraphilic Disorders"
        ]
    
    def extract_disorder_name(self, text: str) -> Optional[str]:
        """Extract disorder name from text"""
        # Look for disorder headers (capitalized, ends with "Disorder")
        pattern = self.patterns["disorder_header"]
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(0).strip()
        return None
    
    def extract_icd_code(self, text: str) -> Optional[str]:
        """Extract ICD diagnostic code"""
        pattern = self.patterns["icd_code"]
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return None
    
    def extract_criteria_label(self, text: str) -> Optional[str]:
        """Extract diagnostic criteria label (A, B, C, etc.)"""
        pattern = self.patterns["criteria_section"]
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return f"Criterion {match.group(0).strip()[0]}"
        return None
    
    def extract_severity_levels(self, text: str) -> List[str]:
        """Extract severity level indicators"""
        pattern = self.patterns["severity"]
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.lower() for m in set(matches)]
    
    def has_specifiers(self, text: str) -> bool:
        """Check if text contains specifiers"""
        pattern = self.patterns["specifier"]
        return bool(re.search(pattern, text))
    
    def identify_section_type(self, text: str) -> str:
        """Identify the type of section"""
        text_lower = text.lower()
        
        if re.search(r"^[A-Z]\.\s", text, re.MULTILINE):
            return "diagnostic_criteria"
        elif "specifier" in text_lower or "subtype" in text_lower:
            return "specifiers"
        elif "prevalence" in text_lower:
            return "prevalence"
        elif "development and course" in text_lower:
            return "development_course"
        elif "risk and prognostic factors" in text_lower:
            return "risk_factors"
        elif "diagnostic features" in text_lower:
            return "diagnostic_features"
        elif "differential diagnosis" in text_lower:
            return "differential_diagnosis"
        elif "comorbidity" in text_lower:
            return "comorbidity"
        else:
            return "general"
    
    def find_disorder_category(self, text: str, context: str = "") -> Optional[str]:
        """Find which disorder category this text belongs to"""
        combined_text = f"{context} {text}".lower()
        
        for category in self.disorder_categories:
            if category.lower() in combined_text:
                return category
        
        return None
    
    def extract_page_number(self, text: str) -> Optional[int]:
        """Extract page number from text"""
        pattern = self.patterns["page_number"]
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        return None
    
    def split_by_disorders(
        self,
        full_text: str,
        page_map: Dict[int, str]
    ) -> List[DSM5Section]:
        """
        Split document into sections by disorder
        
        Args:
            full_text: Complete document text
            page_map: Mapping of page numbers to text
            
        Returns:
            List of DSM5Section objects
        """
        sections = []
        current_category = None
        current_disorder = None
        section_start = 0
        
        lines = full_text.split('\n')
        
        for i, line in enumerate(lines):
            # Check for disorder category
            category = self.find_disorder_category(line)
            if category:
                current_category = category
                logger.debug(f"Found category: {category}")
            
            # Check for disorder name
            disorder = self.extract_disorder_name(line)
            if disorder:
                # Save previous section if exists
                if current_disorder and section_start < i:
                    section_text = '\n'.join(lines[section_start:i])
                    sections.append(DSM5Section(
                        content=section_text,
                        start_page=0,  # Will be calculated from page_map
                        end_page=0,
                        disorder_name=current_disorder,
                        disorder_category=current_category,
                        section_type=self.identify_section_type(section_text)
                    ))
                
                current_disorder = disorder
                section_start = i
                logger.debug(f"Found disorder: {disorder}")
        
        # Add final section
        if current_disorder and section_start < len(lines):
            section_text = '\n'.join(lines[section_start:])
            sections.append(DSM5Section(
                content=section_text,
                start_page=0,
                end_page=0,
                disorder_name=current_disorder,
                disorder_category=current_category,
                section_type=self.identify_section_type(section_text)
            ))
        
        logger.info(f"Extracted {len(sections)} disorder sections")
        return sections
    
    def create_chunk_metadata(
        self,
        text: str,
        section: Optional[DSM5Section] = None,
        page_number: Optional[int] = None
    ) -> ChunkMetadata:
        """
        Create metadata for a text chunk
        
        Args:
            text: Chunk text
            section: Parent DSM5Section if available
            page_number: Page number if known
            
        Returns:
            ChunkMetadata object
        """
        metadata = ChunkMetadata()
        
        # Extract from section if provided
        if section:
            metadata.disorder_name = section.disorder_name
            metadata.disorder_category = section.disorder_category
            metadata.section_type = section.section_type
            metadata.parent_section = section.parent_section
        
        # Extract from text
        metadata.icd_code = self.extract_icd_code(text)
        metadata.criteria_label = self.extract_criteria_label(text)
        metadata.severity_levels = self.extract_severity_levels(text)
        metadata.has_specifiers = self.has_specifiers(text)
        metadata.page_number = page_number or self.extract_page_number(text)
        
        # Override section type if we can determine it from text
        text_section_type = self.identify_section_type(text)
        if text_section_type != "general":
            metadata.section_type = text_section_type
        
        return metadata

# Made with Bob
