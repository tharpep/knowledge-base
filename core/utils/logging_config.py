"""
Simple Logging Configuration
Centralized logging setup for the entire codebase
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> None:
    """
    Setup simple logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_file_logging: Whether to log to files
        enable_console_logging: Whether to log to console
    """
    
    # Create log directory
    if enable_file_logging:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s | %(message)s'
    )
    
    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file_logging:
        # RAG demo log (with simple rotation)
        rag_log_file = os.path.join(log_dir, "rag", "rag_results.log")
        Path(os.path.dirname(rag_log_file)).mkdir(parents=True, exist_ok=True)
        rag_handler = logging.handlers.RotatingFileHandler(
            rag_log_file, maxBytes=1024*1024, backupCount=3  # 1MB max, keep 3 backups
        )
        rag_handler.setLevel(logging.INFO)
        rag_handler.setFormatter(detailed_formatter)
        
        # Create RAG logger
        rag_logger = logging.getLogger("rag_demo")
        rag_logger.addHandler(rag_handler)
        rag_logger.setLevel(logging.INFO)
        rag_logger.propagate = False  # Don't propagate to root logger
        
        # Tuning demo log (with simple rotation)
        tuning_log_file = os.path.join(log_dir, "tuning", "tuning_results.log")
        Path(os.path.dirname(tuning_log_file)).mkdir(parents=True, exist_ok=True)
        tuning_handler = logging.handlers.RotatingFileHandler(
            tuning_log_file, maxBytes=1024*1024, backupCount=3  # 1MB max, keep 3 backups
        )
        tuning_handler.setLevel(logging.INFO)
        tuning_handler.setFormatter(detailed_formatter)
        
        # Create tuning logger
        tuning_logger = logging.getLogger("tuning_demo")
        tuning_logger.addHandler(tuning_handler)
        tuning_logger.setLevel(logging.INFO)
        tuning_logger.propagate = False  # Don't propagate to root logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_rag_logger() -> logging.Logger:
    """Get the RAG demo logger"""
    return logging.getLogger("rag_demo")


def get_tuning_logger() -> logging.Logger:
    """Get the tuning demo logger"""
    return logging.getLogger("tuning_demo")


def log_rag_result(
    question: str,
    answer: str,
    response_time: float,
    model_name: str,
    provider: str,
    context_docs: list = None,
    context_scores: list = None,
    retrieval_time: float = 0.0,
    generation_time: float = 0.0
) -> None:
    """
    Log RAG demo results with retrieved context
    
    Args:
        question: The question asked
        answer: The answer generated
        response_time: Total response time in seconds
        model_name: Model used for generation
        provider: Provider used (ollama, purdue, etc.)
        context_docs: List of retrieved document texts
        context_scores: List of relevance scores for retrieved documents
        retrieval_time: Time spent on retrieval
        generation_time: Time spent on generation
    """
    rag_logger = get_rag_logger()
    
    # Simple log format with wrapped answers
    import textwrap
    wrapped_answer = textwrap.fill(answer, width=80, initial_indent="    ", subsequent_indent="    ")
    rag_logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {model_name} | {response_time:.2f}s | Q: {question[:100]}...")
    rag_logger.info(f"A: {wrapped_answer}")
    
    # Log retrieved context details (show what was found, not full content)
    if context_docs and context_scores:
        rag_logger.info(f"CONTEXT: Retrieved {len(context_docs)} documents")
        for i, (doc, score) in enumerate(zip(context_docs, context_scores)):
            # Show first 100 chars to see what type of content was retrieved
            doc_preview = doc[:100] + "..." if len(doc) > 100 else doc
            rag_logger.info(f"  Doc {i+1} (score: {score:.3f}): {doc_preview}")
    elif context_docs:
        rag_logger.info(f"CONTEXT: Retrieved {len(context_docs)} documents (no scores)")
        for i, doc in enumerate(context_docs):
            doc_preview = doc[:100] + "..." if len(doc) > 100 else doc
            rag_logger.info(f"  Doc {i+1}: {doc_preview}")


def log_tuning_result(
    model_name: str,
    version: str,
    training_time: float,
    final_loss: Optional[float] = None,
    model_size_mb: Optional[float] = None,
    epochs: int = 0,
    batch_size: int = 0,
    learning_rate: float = 0.0,
    device: str = "unknown",
    notes: Optional[str] = None
) -> None:
    """
    Log tuning demo results in a structured format
    
    Args:
        model_name: Name of the model
        version: Version of the tuned model
        training_time: Training time in seconds
        final_loss: Final training loss
        model_size_mb: Model size in MB
        epochs: Number of training epochs
        batch_size: Batch size used
        learning_rate: Learning rate used
        device: Device used for training
        notes: Additional notes
    """
    tuning_logger = get_tuning_logger()
    
    # Simple log format
    loss_str = f"{final_loss:.4f}" if final_loss else "N/A"
    tuning_logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {model_name} v{version} | {training_time:.1f}s | Loss: {loss_str} | {notes or 'No notes'}")




# Initialize logging when module is imported
if __name__ != "__main__":
    # Only setup logging if not being run directly
    setup_logging()
