"""Cross-Encoder Reranker for two-stage retrieval."""

from typing import List, Tuple


class CrossEncoderReranker:
    """Reranks search results using a cross-encoder model."""
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        """Initialize the reranker."""
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy-load the cross-encoder model."""
        if self._model is None:
            from FlagEmbedding import FlagReranker
            import torch
            use_fp16 = torch.cuda.is_available()
            self._model = FlagReranker(self.model_name, use_fp16=use_fp16)
        return self._model
    
    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Rerank documents by relevance to query."""
        if not documents:
            return []
        
        pairs = [[query, doc] for doc in documents]
        scores = self.model.compute_score(pairs, normalize=True)
        
        if isinstance(scores, float):
            scores = [scores]
        
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return scored_docs[:top_k]
