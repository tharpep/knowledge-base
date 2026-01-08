"""Document Retriever with Hybrid Embedding Support"""

from qdrant_client.models import PointStruct
from typing import List, Tuple, Dict, Any, Optional
import uuid


class DocumentRetriever:
    """Handles document embedding and retrieval operations with hybrid support."""
    
    def __init__(self, model_name: str = 'BAAI/bge-m3', use_hybrid: bool = True):
        """Initialize document retriever."""
        self.model_name = model_name
        self.use_hybrid = use_hybrid
        self._retriever = None
        self._flag_model = None
        self._embedding_dim = None

    @property
    def retriever(self):
        """Get SentenceTransformer model (fallback for non-hybrid)."""
        if self._retriever is None:
            from sentence_transformers import SentenceTransformer
            self._retriever = SentenceTransformer(self.model_name)
        return self._retriever
    
    @property
    def flag_model(self):
        """Get FlagEmbedding model for hybrid embeddings."""
        if self._flag_model is None:
            from FlagEmbedding import BGEM3FlagModel
            import torch
            use_fp16 = torch.cuda.is_available()
            self._flag_model = BGEM3FlagModel(self.model_name, use_fp16=use_fp16)
        return self._flag_model

    @property
    def embedding_dim(self) -> int:
        if self._embedding_dim is None:
            if self.use_hybrid and self._flag_model is not None:
                self._embedding_dim = 1024  # BGE-M3 dense dim
            else:
                self._embedding_dim = self.retriever.get_sentence_embedding_dimension()
        return self._embedding_dim
    
    def encode_documents(self, documents: List[str]) -> List[List[float]]:
        """Encode documents into dense embeddings."""
        if self.use_hybrid:
            output = self.flag_model.encode(documents, return_dense=True, return_sparse=False)
            return [emb.tolist() for emb in output['dense_vecs']]
        else:
            embeddings = self.retriever.encode(documents)
            return [embedding.tolist() for embedding in embeddings]
    
    def encode_documents_hybrid(self, documents: List[str]) -> Tuple[List[List[float]], List[Dict[int, float]]]:
        """Encode documents into both dense and sparse embeddings."""
        output = self.flag_model.encode(documents, return_dense=True, return_sparse=True)
        dense = [emb.tolist() for emb in output['dense_vecs']]
        sparse = self._convert_sparse(output['lexical_weights'])
        return dense, sparse
    
    def _convert_sparse(self, lexical_weights: List[Dict]) -> List[Dict[int, float]]:
        """Convert FlagEmbedding sparse output to Qdrant format."""
        result = []
        for weights in lexical_weights:
            sparse_vec = {int(k): float(v) for k, v in weights.items()}
            result.append(sparse_vec)
        return result
    
    def encode_query(self, query: str) -> List[float]:
        """Encode a query into a dense embedding."""
        if self.use_hybrid:
            output = self.flag_model.encode([query], return_dense=True, return_sparse=False)
            return output['dense_vecs'][0].tolist()
        else:
            embedding = self.retriever.encode(query)
            return embedding.tolist()
    
    def encode_query_hybrid(self, query: str) -> Tuple[List[float], Dict[int, float]]:
        """Encode query into both dense and sparse embeddings."""
        output = self.flag_model.encode([query], return_dense=True, return_sparse=True)
        dense = output['dense_vecs'][0].tolist()
        sparse = self._convert_sparse(output['lexical_weights'])[0]
        return dense, sparse
    
    def create_points(self, documents: List[str], embeddings: List[List[float]], 
                     start_doc_id: int = 0, metadata: dict = None) -> List[PointStruct]:
        """Create Qdrant points from documents and embeddings (dense only)."""
        points = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            payload = {
                "text": doc, 
                "doc_id": start_doc_id + idx,
                "chunk_id": idx
            }
            if metadata:
                payload.update(metadata)
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=payload
            )
            points.append(point)
        return points
    
    def create_hybrid_points(self, documents: List[str], dense_embeddings: List[List[float]],
                            sparse_embeddings: List[Dict[int, float]], start_doc_id: int = 0,
                            metadata: dict = None) -> List[PointStruct]:
        """Create Qdrant points with both dense and sparse vectors."""
        from qdrant_client.models import SparseVector
        
        points = []
        for idx, (doc, dense, sparse) in enumerate(zip(documents, dense_embeddings, sparse_embeddings)):
            payload = {
                "text": doc, 
                "doc_id": start_doc_id + idx,
                "chunk_id": idx
            }
            if metadata:
                payload.update(metadata)
            
            indices = list(sparse.keys())
            values = list(sparse.values())
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": dense,
                    "sparse": SparseVector(indices=indices, values=values)
                },
                payload=payload
            )
            points.append(point)
        return points
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dim
    
    def get_model_info(self) -> dict:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "hybrid_enabled": self.use_hybrid
        }

