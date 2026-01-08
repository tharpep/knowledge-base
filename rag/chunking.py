"""Semantic text chunking utilities for RAG ingestion."""

from typing import List, Tuple


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    is_markdown: bool = False
) -> List[str]:
    """Split text into semantically meaningful chunks using LangChain."""
    if not text or not text.strip():
        return []
    
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=separators,
        length_function=len,
    )
    
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]


def chunk_markdown(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100
) -> List[Tuple[str, str]]:
    """Split markdown text, preserving header context. Returns (chunk, section_title) tuples."""
    if not text or not text.strip():
        return []
    
    from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
    
    headers_to_split = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split)
    md_docs = md_splitter.split_text(text)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
    )
    
    results = []
    for doc in md_docs:
        section_title = " > ".join(
            doc.metadata.get(h, "") 
            for h in ["h1", "h2", "h3"] 
            if doc.metadata.get(h)
        )
        
        if len(doc.page_content) <= chunk_size:
            results.append((doc.page_content.strip(), section_title))
        else:
            sub_chunks = text_splitter.split_text(doc.page_content)
            for chunk in sub_chunks:
                if chunk.strip():
                    results.append((chunk.strip(), section_title))
    
    return results


def chunk_conversation(
    text: str,
    chunk_size: int = 1500,
    overlap: int = 150
) -> List[str]:
    """Chunk conversation text, optimized for dialogue format."""
    return chunk_text(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
        is_markdown=False
    )
