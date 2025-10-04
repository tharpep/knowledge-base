# Develop Your App

## Overview

Learn how to develop your generative RAG application locally. This guide covers setting up a development environment for building and testing RAG applications with AI models.

## Development Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Git
- Code editor (VS Code recommended)

### Local Development Environment

#### 1. Project Structure
```
rag-app/
├── src/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
├── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

#### 2. Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Development Dependencies
```txt
# requirements-dev.txt
pytest
black
flake8
mypy
pre-commit
```

## Core Components

### 1. Document Processing
```python
class DocumentProcessor:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def process_document(self, text: str) -> List[float]:
        """Convert document text to embeddings"""
        return self.embedder.encode(text).tolist()
```

### 2. Vector Store Integration
```python
class VectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        vectors = [doc.embedding for doc in documents]
        self.client.upsert(
            collection_name="documents",
            points=vectors
        )
```

### 3. RAG Pipeline
```python
class RAGPipeline:
    def __init__(self, vector_store: VectorStore, llm_client: LLMClient):
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    def query(self, question: str) -> str:
        """Process query through RAG pipeline"""
        # Retrieve relevant documents
        results = self.vector_store.search(question, top_k=5)
        
        # Generate context
        context = "\n".join([doc.text for doc in results])
        
        # Generate answer
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        return self.llm_client.generate(prompt)
```

## Development Workflow

### 1. Local Testing
```bash
# Run tests
pytest tests/

# Code formatting
black src/
flake8 src/

# Type checking
mypy src/
```

### 2. Docker Development
```bash
# Build development image
docker build -f Dockerfile.dev -t rag-app:dev .

# Run with hot reload
docker-compose -f docker-compose.dev.yml up
```

### 3. API Development
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
    result = rag_pipeline.query(request.question)
    return QueryResponse(
        answer=result.answer,
        sources=result.sources
    )
```

## Testing Strategy

### 1. Unit Tests
```python
def test_document_processor():
    processor = DocumentProcessor()
    text = "Sample document text"
    embedding = processor.process_document(text)
    assert len(embedding) == 384  # Dimension of embedding
```

### 2. Integration Tests
```python
def test_rag_pipeline():
    pipeline = RAGPipeline(vector_store, llm_client)
    result = pipeline.query("What is machine learning?")
    assert isinstance(result, str)
    assert len(result) > 0
```

### 3. End-to-End Tests
```python
def test_api_endpoint():
    response = client.post("/query", json={"question": "Test question"})
    assert response.status_code == 200
    assert "answer" in response.json()
```

## Configuration Management

### Environment Variables
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/ragdb
VECTOR_STORE_URL=http://localhost:6333
LLM_MODEL=llama2
API_KEY=your-api-key
```

### Configuration Class
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    vector_store_url: str
    llm_model: str
    api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Debugging and Monitoring

### 1. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_query(question: str):
    logger.info(f"Processing query: {question}")
    # ... processing logic
    logger.info("Query processed successfully")
```

### 2. Performance Monitoring
```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper
```

## Deployment Preparation

### 1. Production Configuration
```python
# config/production.py
class ProductionConfig:
    DEBUG = False
    DATABASE_URL = os.getenv("DATABASE_URL")
    VECTOR_STORE_URL = os.getenv("VECTOR_STORE_URL")
```

### 2. Health Checks
```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### 3. Docker Production Build
```dockerfile
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Best Practices

### Code Quality
- Follow PEP 8 style guide
- Use type hints
- Write comprehensive tests
- Document functions and classes

### Performance
- Optimize database queries
- Cache frequently accessed data
- Use async/await for I/O operations
- Monitor memory usage

### Security
- Validate input data
- Use environment variables for secrets
- Implement rate limiting
- Regular dependency updates
