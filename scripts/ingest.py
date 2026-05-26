"""
Document Ingestion Script
Processes DSM-5.pdf and populates the vector database
"""

import sys
from pathlib import Path
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import get_settings
from backend.database import get_vector_db
from backend.chunking.hybrid_processor import HybridDocumentProcessor


def setup_logging():
    """Configure logging for ingestion"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )


def main():
    """Main ingestion function"""
    setup_logging()
    
    logger.info("=" * 80)
    logger.info("DSM-5 Document Ingestion Pipeline")
    logger.info("=" * 80)
    
    # Get settings
    settings = get_settings()
    
    # Check if DSM-5.pdf exists
    pdf_path = Path("DSM-5.pdf")
    if not pdf_path.exists():
        logger.error(f"DSM-5.pdf not found in current directory: {pdf_path.absolute()}")
        logger.error("Please place DSM-5.pdf in the project root directory")
        sys.exit(1)
    
    logger.info(f"Found DSM-5.pdf at: {pdf_path.absolute()}")
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        processor = HybridDocumentProcessor()
        vector_db = get_vector_db()
        
        # Ask user if they want to reset the database
        logger.info("\nCurrent database status:")
        stats = vector_db.get_collection_stats()
        logger.info(f"  Collection: {stats['collection_name']}")
        logger.info(f"  Documents: {stats['document_count']}")
        logger.info(f"  Status: {stats['status']}")
        
        if stats['document_count'] > 0:
            response = input("\nDatabase already contains documents. Reset and re-ingest? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                logger.info("Resetting database...")
                vector_db.create_collection(reset=True)
            else:
                logger.info("Keeping existing database. Exiting.")
                sys.exit(0)
        else:
            logger.info("Database is empty. Creating new collection...")
            vector_db.create_collection(reset=False)
        
        # Process document
        logger.info("\n" + "=" * 80)
        logger.info("Stage 1: Loading and Processing DSM-5.pdf")
        logger.info("=" * 80)
        
        texts, metadatas, ids = processor.process_document(str(pdf_path))
        
        # Display processing statistics
        stats = processor.get_processing_stats(texts)
        logger.info("\nProcessing Statistics:")
        logger.info(f"  Total chunks: {stats['total_chunks']}")
        logger.info(f"  Average chunk size: {stats['avg_chunk_size']} characters")
        logger.info(f"  Min chunk size: {stats['min_chunk_size']} characters")
        logger.info(f"  Max chunk size: {stats['max_chunk_size']} characters")
        logger.info(f"  Total characters: {stats['total_characters']:,}")
        
        # Add to vector database
        logger.info("\n" + "=" * 80)
        logger.info("Stage 2: Adding Documents to Vector Database")
        logger.info("=" * 80)
        
        logger.info("Generating embeddings and storing in ChromaDB...")
        logger.info("(This may take several minutes depending on document size)")
        
        # Add documents in batches to show progress
        batch_size = 50
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_num = (i // batch_size) + 1
            end_idx = min(i + batch_size, len(texts))
            
            batch_texts = texts[i:end_idx]
            batch_metadatas = metadatas[i:end_idx]
            batch_ids = ids[i:end_idx]
            
            vector_db.add_documents(
                texts=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            
            logger.info(f"  Batch {batch_num}/{total_batches} complete ({end_idx}/{len(texts)} documents)")
        
        # Verify ingestion
        logger.info("\n" + "=" * 80)
        logger.info("Stage 3: Verification")
        logger.info("=" * 80)
        
        final_stats = vector_db.get_collection_stats()
        logger.info(f"  Documents in database: {final_stats['document_count']}")
        logger.info(f"  Database status: {final_stats['status']}")
        
        if final_stats['document_count'] == len(texts):
            logger.success("\n✓ Ingestion completed successfully!")
            logger.info(f"✓ {final_stats['document_count']} documents indexed")
            logger.info(f"✓ Vector database ready at: {settings.get_chroma_path()}")
        else:
            logger.warning(f"\n⚠ Warning: Expected {len(texts)} documents but found {final_stats['document_count']}")
        
        logger.info("\n" + "=" * 80)
        logger.info("Next Steps:")
        logger.info("  1. Start the FastAPI backend: python backend/main.py")
        logger.info("  2. Start the Streamlit frontend: streamlit run frontend/app.py")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.warning("\n\nIngestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nError during ingestion: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
