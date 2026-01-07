"""Logging configuration for the codebase."""

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
    """Setup logging for the application."""
    
    if enable_file_logging:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s | %(message)s'
    )
    
    if enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    if enable_file_logging:
        rag_log_file = os.path.join(log_dir, "rag", "rag_results.log")
        Path(os.path.dirname(rag_log_file)).mkdir(parents=True, exist_ok=True)
        rag_handler = logging.handlers.RotatingFileHandler(
            rag_log_file, maxBytes=1024*1024, backupCount=3
        )
        rag_handler.setLevel(logging.INFO)
        rag_handler.setFormatter(detailed_formatter)
        
        rag_logger = logging.getLogger("rag_demo")
        rag_logger.addHandler(rag_handler)
        rag_logger.setLevel(logging.INFO)
        rag_logger.propagate = False
        
        tuning_log_file = os.path.join(log_dir, "tuning", "tuning_results.log")
        Path(os.path.dirname(tuning_log_file)).mkdir(parents=True, exist_ok=True)
        tuning_handler = logging.handlers.RotatingFileHandler(
            tuning_log_file, maxBytes=1024*1024, backupCount=3
        )
        tuning_handler.setLevel(logging.INFO)
        tuning_handler.setFormatter(detailed_formatter)
        
        tuning_logger = logging.getLogger("tuning_demo")
        tuning_logger.addHandler(tuning_handler)
        tuning_logger.setLevel(logging.INFO)
        tuning_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


def get_rag_logger() -> logging.Logger:
    """Get the RAG demo logger."""
    return logging.getLogger("rag_demo")


def get_tuning_logger() -> logging.Logger:
    """Get the tuning demo logger."""
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
    """Log RAG demo results with retrieved context."""
    rag_logger = get_rag_logger()
    
    import textwrap
    wrapped_answer = textwrap.fill(answer, width=80, initial_indent="    ", subsequent_indent="    ")
    rag_logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {model_name} | {response_time:.2f}s | Q: {question[:100]}...")
    rag_logger.info(f"A: {wrapped_answer}")
    
    if context_docs and context_scores:
        rag_logger.info(f"CONTEXT: Retrieved {len(context_docs)} documents")
        for i, (doc, score) in enumerate(zip(context_docs, context_scores)):
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
    """Log tuning demo results in a structured format."""
    tuning_logger = get_tuning_logger()
    
    loss_str = f"{final_loss:.4f}" if final_loss else "N/A"
    tuning_logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {model_name} v{version} | {training_time:.1f}s | Loss: {loss_str} | {notes or 'No notes'}")




if __name__ != "__main__":
    setup_logging()
