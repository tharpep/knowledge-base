"""Document Ingestion API routes - Ingest documents into RAG system"""

import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/ingest")
async def ingest_documents(folder_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Ingest documents into the RAG system.
    
    Args:
        folder_path: Path to folder containing documents to ingest. 
                     If not provided, uses config.rag_documents_folder (corpus or documents based on rag_use_documents_folder)
        
    Returns:
        Dictionary with ingestion results including:
        - success: Whether ingestion was successful
        - processed: Number of files processed
        - failed: Number of files that failed
        - files: List of file processing details
        - errors: List of any errors encountered
        - request_id: Request ID for tracing
    """
    from rag.rag_setup import BasicRAG
    from rag.document_ingester import DocumentIngester
    from core.config import get_config
    
    # Generate request ID for tracing
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    try:
        # Use config folder if not provided
        config = get_config()
        if folder_path is None:
            folder_path = config.rag_documents_folder
        
        # Validate folder path
        folder = Path(folder_path)
        if not folder.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "message": f"Folder not found: {folder_path}",
                        "type": "not_found_error",
                        "code": "folder_not_found"
                    },
                    "request_id": request_id
                }
            )
        
        if not folder.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "message": f"Path is not a directory: {folder_path}",
                        "type": "invalid_request_error",
                        "code": "not_a_directory"
                    },
                    "request_id": request_id
                }
            )
        
        # Initialize RAG system
        rag = BasicRAG()
        
        # Initialize ingester
        ingester = DocumentIngester(rag)
        
        # Ingest documents
        result = ingester.ingest_folder(folder_path)
        
        return {
            "success": result["success"],
            "processed": result["processed"],
            "failed": result["failed"],
            "files": result["files"],
            "errors": result.get("errors", []),
            "request_id": request_id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": f"Document ingestion failed: {str(e)}",
                    "type": "internal_error",
                    "code": "server_error"
                },
                "request_id": request_id
            }
        )
