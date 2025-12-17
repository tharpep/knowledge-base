"""
RAG Document Processing Workers
Async workers for document ingestion via arq
"""

import logging
from arq.connections import RedisSettings

logger = logging.getLogger(__name__)


async def process_document(ctx: dict, blob_id: str) -> dict:
    """
    Process a document from blob storage into Qdrant.
    
    This is the main worker function called by arq.
    Pipeline: Get Blob → Parse → Preprocess → Chunk → Embed → Store
    
    Args:
        ctx: arq context (contains redis connection)
        blob_id: The blob to process
        
    Returns:
        dict with processing results
    """
    from core.file_storage import get_blob_storage
    from rag.document_parser import get_document_parser
    from rag.document_ingester import DocumentIngester
    from rag.rag_setup import BasicRAG
    
    logger.info(f"[Worker] Starting processing for blob: {blob_id}")
    
    # Step 1: Get blob from storage
    storage = get_blob_storage()
    file_path = storage.get(blob_id)
    
    if file_path is None:
        logger.error(f"[Worker] Blob not found: {blob_id}")
        raise ValueError(f"Blob not found: {blob_id}")
    
    logger.info(f"[Worker] Found blob at: {file_path}")
    
    # Step 2: Parse document (extract text)
    parser = get_document_parser()
    parsed = parser.parse(file_path)
    
    if parsed is None:
        logger.error(f"[Worker] Failed to parse: {file_path}")
        raise ValueError(f"Failed to parse document: {file_path}")
    
    logger.info(f"[Worker] Parsed {parsed.file_type}: {parsed.original_filename} ({parsed.page_count} pages)")
    
    # Step 3: Initialize RAG and ingester
    rag = BasicRAG()
    ingester = DocumentIngester(rag)
    
    # Step 4: Preprocess text
    processed_text = ingester._preprocess_text(parsed.text)
    
    # Step 5: Chunk text
    chunks = ingester._chunk_text(processed_text, max_chunk_size=1000)
    logger.info(f"[Worker] Created {len(chunks)} chunks")
    
    # Step 6: Add to vector database
    count = rag.add_documents(chunks)
    
    logger.info(f"[Worker] Indexed {count} chunks from {blob_id}")
    
    return {
        "blob_id": blob_id,
        "chunks_indexed": count,
        "file_type": parsed.file_type,
        "original_filename": parsed.original_filename,
        "page_count": parsed.page_count
    }


# arq worker settings - used when running: arq rag.workers.WorkerSettings
class WorkerSettings:
    """arq worker configuration"""
    functions = [process_document]
    redis_settings = RedisSettings(host='localhost', port=6379)
    max_jobs = 10
    job_timeout = 300  # 5 minutes per job
