"""
Library Ingestion Script
Iterates through all blobs in data/library_blob and re-ingests them into the RAG system.
Useful for bulk ingestion or re-indexing after model changes.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from core.file_storage import get_blob_storage
from rag.document_parser import get_document_parser
from rag.document_ingester import DocumentIngester
from rag.rag_setup import get_rag
from core.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ingest_library")

async def ingest_blob(blob_id: str, rag, ingester, parser, storage):
    """Ingest a single blob."""
    try:
        # Get blob info and file
        blob_info = storage.get_info(blob_id)
        file_path = storage.get(blob_id)
        
        if not file_path or not blob_info:
            logger.error(f"Blob not found: {blob_id}")
            return False
            
        logger.info(f"Processing: {blob_info.original_filename} ({blob_id})")
        
        # Parse
        parsed = parser.parse(file_path)
        if not parsed:
            logger.error(f"Failed to parse: {blob_info.original_filename}")
            return False
            
        # Preprocess
        processed_text = ingester._preprocess_text(parsed.text)
        
        # Clear existing chunks for this blob to prevent duplicates
        rag.delete_by_blob_id(blob_id)
        
        # Chunk
        config = get_config()
        chunks = ingester._chunk_text(
            processed_text, 
            max_chunk_size=config.library_chunk_size,
            overlap=config.library_chunk_overlap
        )
        
        # Store
        metadata = {
            "blob_id": blob_id,
            "original_filename": blob_info.original_filename
        }
        
        count = rag.add_documents(chunks, metadata=metadata)
        logger.info(f"Success: {blob_info.original_filename} -> {count} chunks")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {blob_id}: {e}")
        return False

async def main():
    logger.info("Starting Library Ingestion...")
    
    # Initialize components
    storage = get_blob_storage()
    rag = get_rag()
    ingester = DocumentIngester(rag)
    parser = get_document_parser()
    
    # Get all blobs
    blobs = storage.list()
    total = len(blobs)
    logger.info(f"Found {total} blobs in library")
    
    if total == 0:
        logger.info("No blobs to ingest.")
        return
    
    # Process all
    success_count = 0
    failed_count = 0
    
    for i, blob in enumerate(blobs):
        logger.info(f"[{i+1}/{total}] Ingesting {blob.blob_id}...")
        success = await ingest_blob(blob.blob_id, rag, ingester, parser, storage)
        if success:
            success_count += 1
        else:
            failed_count += 1
            
    logger.info("="*40)
    logger.info("Ingestion Complete")
    logger.info(f"Total: {total}")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {failed_count}")
    logger.info("="*40)

if __name__ == "__main__":
    asyncio.run(main())
