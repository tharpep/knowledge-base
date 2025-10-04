# Leveraging RAG in GenAI

## Overview

This guide walks through the process of setting up and utilizing a GenAI stack with Retrieval-Augmented Generation (RAG) systems and graph databases. Learn how to integrate graph databases like Neo4j with AI models for more accurate, contextually-aware responses.

## What is RAG?

### Retrieval-Augmented Generation
RAG is a technique that combines the power of large language models with external knowledge retrieval. It enhances AI responses by:

- **Retrieving** relevant information from external sources
- **Augmenting** the input with retrieved context
- **Generating** responses based on both the query and retrieved information

### Benefits of RAG
- **Accuracy**: Reduces hallucinations by grounding responses in factual data
- **Relevance**: Provides up-to-date information beyond training data
- **Transparency**: Shows sources for generated responses
- **Customization**: Can be tailored to specific domains or datasets

## RAG Architecture

### Core Components

#### 1. Document Store
- **Purpose**: Stores source documents and metadata
- **Options**: PostgreSQL, MongoDB, Elasticsearch
- **Features**: Full-text search, metadata filtering

#### 2. Vector Database
- **Purpose**: Stores document embeddings for semantic search
- **Options**: Qdrant, Pinecone, Weaviate, Chroma
- **Features**: Similarity search, filtering, clustering

#### 3. Embedding Model
- **Purpose**: Converts text to vector representations
- **Options**: OpenAI Embeddings, Sentence Transformers, Cohere
- **Features**: Semantic understanding, multilingual support

#### 4. LLM
- **Purpose**: Generates responses based on context
- **Options**: GPT-4, Claude, Llama, local models
- **Features**: Context understanding, response generation

### Data Flow
```
Query → Embedding → Vector Search → Document Retrieval → Context Augmentation → LLM → Response
```

## Graph Database Integration

### Why Graph Databases?

#### 1. Relationship Modeling
- **Entities**: People, organizations, concepts
- **Relationships**: Connections between entities
- **Properties**: Attributes of entities and relationships

#### 2. Complex Queries
- **Traversal**: Navigate through connected data
- **Pattern Matching**: Find specific relationship patterns
- **Aggregation**: Analyze network structures

### Neo4j Integration

#### 1. Graph Schema Design
```cypher
// Create nodes
CREATE (p:Person {name: "John Doe", expertise: "Machine Learning"})
CREATE (c:Concept {name: "Neural Networks", category: "AI"})
CREATE (d:Document {title: "Deep Learning Guide", content: "..."})

// Create relationships
CREATE (p)-[:EXPERT_IN]->(c)
CREATE (d)-[:ABOUT]->(c)
CREATE (p)-[:AUTHORED]->(d)
```

#### 2. Graph-Enhanced Retrieval
```python
class GraphRAG:
    def __init__(self, neo4j_client, vector_store, llm):
        self.neo4j = neo4j_client
        self.vector_store = vector_store
        self.llm = llm
    
    def retrieve_context(self, query: str):
        # Vector search for initial documents
        vector_results = self.vector_store.search(query, top_k=5)
        
        # Extract entities from query
        entities = self.extract_entities(query)
        
        # Graph traversal for related concepts
        graph_results = self.neo4j.query("""
            MATCH (e:Entity)-[r]-(related)
            WHERE e.name IN $entities
            RETURN related, r
        """, entities=entities)
        
        return vector_results, graph_results
```

## Implementation Guide

### 1. Setup Environment

#### Docker Compose Configuration
```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.0
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
  
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
  
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - neo4j
      - qdrant
```

### 2. Document Processing Pipeline

#### Text Chunking
```python
class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, text: str) -> List[str]:
        """Split document into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap
        
        return chunks
```

#### Entity Extraction
```python
import spacy

class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
```

### 3. Graph Database Operations

#### Node Creation
```python
class GraphManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_document_node(self, doc_id: str, title: str, content: str):
        """Create document node in graph"""
        with self.driver.session() as session:
            session.run("""
                CREATE (d:Document {
                    id: $doc_id,
                    title: $title,
                    content: $content,
                    created_at: datetime()
                })
            """, doc_id=doc_id, title=title, content=content)
```

#### Relationship Creation
```python
    def link_entities_to_document(self, doc_id: str, entities: List[Dict]):
        """Link extracted entities to document"""
        with self.driver.session() as session:
            for entity in entities:
                # Create entity node if not exists
                session.run("""
                    MERGE (e:Entity {name: $name, type: $type})
                    MERGE (d:Document {id: $doc_id})
                    MERGE (d)-[:MENTIONS]->(e)
                """, name=entity["text"], type=entity["label"], doc_id=doc_id)
```

### 4. Enhanced Retrieval

#### Hybrid Search
```python
class HybridRetriever:
    def __init__(self, vector_store, graph_manager):
        self.vector_store = vector_store
        self.graph = graph_manager
    
    def retrieve(self, query: str, top_k: int = 5):
        # Vector similarity search
        vector_results = self.vector_store.similarity_search(query, k=top_k)
        
        # Extract entities for graph search
        entities = self.extract_entities(query)
        
        # Graph-based expansion
        graph_results = self.graph.expand_entities(entities)
        
        # Combine and rank results
        combined_results = self.combine_results(vector_results, graph_results)
        
        return combined_results[:top_k]
```

## Advanced Features

### 1. Multi-hop Reasoning
```python
def multi_hop_query(self, query: str):
    """Perform multi-hop reasoning through graph"""
    # Start with query entities
    start_entities = self.extract_entities(query)
    
    # Find connected concepts
    connected = self.graph.find_connected_concepts(start_entities, hops=2)
    
    # Retrieve documents about connected concepts
    context_docs = []
    for concept in connected:
        docs = self.vector_store.search(concept, top_k=3)
        context_docs.extend(docs)
    
    return context_docs
```

### 2. Temporal Reasoning
```python
def temporal_query(self, query: str, time_range: Tuple[datetime, datetime]):
    """Query with temporal constraints"""
    # Find entities in query
    entities = self.extract_entities(query)
    
    # Graph query with time filter
    results = self.graph.query("""
        MATCH (e:Entity)-[r]-(d:Document)
        WHERE e.name IN $entities
        AND d.created_at >= $start_date
        AND d.created_at <= $end_date
        RETURN d
        ORDER BY d.created_at DESC
    """, entities=entities, start_date=time_range[0], end_date=time_range[1])
    
    return results
```

### 3. Contextual Ranking
```python
def rank_by_context(self, query: str, candidates: List[Document]):
    """Rank documents by contextual relevance"""
    query_embedding = self.embedder.encode(query)
    
    scores = []
    for doc in candidates:
        # Semantic similarity
        doc_embedding = self.embedder.encode(doc.content)
        semantic_score = cosine_similarity([query_embedding], [doc_embedding])[0][0]
        
        # Graph connectivity score
        graph_score = self.calculate_graph_relevance(query, doc)
        
        # Combined score
        combined_score = 0.7 * semantic_score + 0.3 * graph_score
        scores.append(combined_score)
    
    # Sort by combined score
    ranked_docs = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked_docs]
```

## Performance Optimization

### 1. Caching Strategies
```python
from functools import lru_cache

class CachedRetriever:
    def __init__(self, retriever):
        self.retriever = retriever
    
    @lru_cache(maxsize=1000)
    def cached_retrieve(self, query: str, top_k: int):
        """Cache retrieval results"""
        return self.retriever.retrieve(query, top_k)
```

### 2. Batch Processing
```python
def batch_embed_documents(self, documents: List[str], batch_size: int = 32):
    """Process documents in batches for efficiency"""
    embeddings = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_embeddings = self.embedder.encode(batch)
        embeddings.extend(batch_embeddings)
    
    return embeddings
```

### 3. Index Optimization
```python
def optimize_vector_index(self):
    """Optimize vector database index"""
    # Create HNSW index for faster search
    self.vector_store.create_index(
        field_name="embedding",
        index_type="hnsw",
        metric="cosine",
        ef_construction=200,
        m=16
    )
```

## Monitoring and Evaluation

### 1. Retrieval Metrics
```python
def evaluate_retrieval(self, test_queries: List[str], ground_truth: List[List[str]]):
    """Evaluate retrieval performance"""
    metrics = {
        "precision": [],
        "recall": [],
        "f1": []
    }
    
    for query, gt_docs in zip(test_queries, ground_truth):
        retrieved = self.retrieve(query, top_k=10)
        retrieved_ids = [doc.id for doc in retrieved]
        
        # Calculate metrics
        precision = len(set(retrieved_ids) & set(gt_docs)) / len(retrieved_ids)
        recall = len(set(retrieved_ids) & set(gt_docs)) / len(gt_docs)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics["precision"].append(precision)
        metrics["recall"].append(recall)
        metrics["f1"].append(f1)
    
    return {k: np.mean(v) for k, v in metrics.items()}
```

### 2. Response Quality
```python
def evaluate_response_quality(self, query: str, response: str, context: List[str]):
    """Evaluate response quality metrics"""
    metrics = {}
    
    # Factual accuracy (requires ground truth)
    metrics["factual_accuracy"] = self.check_factual_accuracy(response, context)
    
    # Relevance to query
    metrics["relevance"] = self.calculate_relevance(query, response)
    
    # Completeness
    metrics["completeness"] = self.assess_completeness(query, response)
    
    return metrics
```

## Best Practices

### 1. Data Quality
- Clean and preprocess documents
- Validate entity extractions
- Maintain consistent metadata

### 2. System Design
- Use appropriate chunk sizes
- Implement proper error handling
- Monitor system performance

### 3. Security
- Secure database connections
- Validate user inputs
- Implement access controls

### 4. Scalability
- Use distributed systems for large datasets
- Implement caching strategies
- Optimize database queries

## Conclusion

RAG with graph databases provides a powerful approach to building contextually-aware AI systems. By combining semantic search with relationship modeling, you can create more accurate and comprehensive responses that leverage both content similarity and structural knowledge.

The key to success is:
- **Proper data modeling** in the graph database
- **Effective retrieval strategies** that combine vector and graph search
- **Continuous evaluation** and optimization of the system
- **Scalable architecture** that can handle growing datasets
