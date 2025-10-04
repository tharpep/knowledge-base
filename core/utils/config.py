"""
Simple Configuration Management
Basic settings for RAG system testing and operation
"""

import os
from dataclasses import dataclass


@dataclass
class RAGConfig:
    """Simple configuration for RAG system"""
    
    # Hardware settings
    use_laptop: bool = True  # True for laptop (llama3.2:1b), False for PC (qwen3:8b)
    
    # AI Provider settings
    use_ollama: bool = True  # True for Ollama (local), False for Purdue API
    
    # Vector store settings
    use_persistent: bool = True  # True for persistent storage, False for in-memory only
    collection_name: str = "simrag_docs"  # Name for Qdrant collection
    clear_on_ingest: bool = True  # Clear collection before ingesting new documents
    
    # Retrieval settings
    top_k: int = 5  # Number of documents to retrieve (1-20 recommended)
    similarity_threshold: float = 0.7  # Minimum similarity score (0.0-1.0)
    
    # Generation settings
    max_tokens: int = 200  # Maximum tokens in response (50-500 recommended)
    temperature: float = 0.7  # Creativity level (0.0-1.0, lower = more focused)
    
    @property
    def model_name(self) -> str:
        """Get model name based on hardware configuration"""
        return "llama3.2:1b" if self.use_laptop else "qwen3:8b"


@dataclass
class TuningConfig:
    """Simple configuration for model fine-tuning"""
    
    # Hardware settings
    use_laptop: bool = True  # True for laptop (llama3.2:1b), False for PC (qwen3:8b)
    
    # Model settings
    device: str = "auto"  # Options: "auto", "cpu", "cuda", "mps" (for Apple Silicon)
    max_length: int = 512  # Maximum sequence length (256-1024 recommended)
    
    # Training settings (will be optimized based on use_laptop)
    num_epochs: int = 3  # Number of training epochs (1-10 recommended)
    batch_size: int = 4  # Batch size (1-16, adjust based on GPU memory)
    learning_rate: float = 5e-5  # Learning rate (1e-5 to 1e-3 recommended)
    
    # Model versioning
    version: str = "v1.0"  # Model version (e.g., v1.0, v1.1, v2.0)
    create_version_dir: bool = True  # Whether to create versioned subdirectories
    
    @property
    def optimized_batch_size(self) -> int:
        """Get batch size optimized for hardware"""
        return 1 if self.use_laptop else 8  # CPU: 1, GPU: 8
    
    @property
    def optimized_num_epochs(self) -> int:
        """Get number of epochs optimized for hardware"""
        return 1 if self.use_laptop else 3  # CPU: 1 for speed, GPU: 3 for quality
    
    @property
    def model_name(self) -> str:
        """Get model name based on hardware configuration"""
        return "llama3.2:1b" if self.use_laptop else "qwen3:8b"
    
    @property
    def output_dir(self) -> str:
        """Get output directory based on hardware configuration"""
        model_suffix = "1b" if self.use_laptop else "8b"
        base_dir = f"./tuned_models/llama_{model_suffix}"
        
        if self.create_version_dir:
            return f"{base_dir}/{self.version}"
        return base_dir
    
    @property
    def model_registry_path(self) -> str:
        """Get path to model registry metadata file"""
        model_suffix = "1b" if self.use_laptop else "8b"
        return f"./tuned_models/llama_{model_suffix}/model_registry.json"


# Default configurations
DEFAULT_RAG_CONFIG = RAGConfig()
DEFAULT_TUNING_CONFIG = TuningConfig()


def get_rag_config() -> RAGConfig:
    """Get RAG configuration with environment variable overrides
    
    Environment variables that can be set:
        - USE_LAPTOP: "true" or "false" (laptop=llama3.2:1b, PC=qwen3:8b)
    - USE_OLLAMA: "true" or "false" (use Ollama vs Purdue API)
    - USE_PERSISTENT: "true" or "false" (persistent vs in-memory storage)
    - COLLECTION_NAME: name for Qdrant collection
    """
    config = RAGConfig()
    
    # Override with environment variables if set
    use_laptop_env = os.getenv("USE_LAPTOP")
    if use_laptop_env:
        config.use_laptop = use_laptop_env.lower() == "true"
    
    use_ollama_env = os.getenv("USE_OLLAMA")
    if use_ollama_env:
        config.use_ollama = use_ollama_env.lower() == "true"
    
    use_persistent_env = os.getenv("USE_PERSISTENT")
    if use_persistent_env:
        config.use_persistent = use_persistent_env.lower() == "true"
    
    collection_name_env = os.getenv("COLLECTION_NAME")
    if collection_name_env:
        config.collection_name = collection_name_env
    
    return config


def get_tuning_config() -> TuningConfig:
    """Get tuning configuration with environment variable overrides
    
    Environment variables that can be set:
        - USE_LAPTOP: "true" or "false" (laptop=llama3.2:1b, PC=qwen3:8b)
    - TUNING_BATCH_SIZE: batch size as integer (1-16)
    - TUNING_EPOCHS: number of epochs as integer (1-10)
    - TUNING_DEVICE: device like "auto", "cpu", "cuda", "mps"
    """
    config = TuningConfig()
    
    # Override with environment variables if set
    use_laptop_env = os.getenv("USE_LAPTOP")
    if use_laptop_env:
        config.use_laptop = use_laptop_env.lower() == "true"
    
    tuning_batch_size_env = os.getenv("TUNING_BATCH_SIZE")
    if tuning_batch_size_env:
        config.batch_size = int(tuning_batch_size_env)
    
    tuning_epochs_env = os.getenv("TUNING_EPOCHS")
    if tuning_epochs_env:
        config.num_epochs = int(tuning_epochs_env)
    
    tuning_device_env = os.getenv("TUNING_DEVICE")
    if tuning_device_env:
        config.device = tuning_device_env
    
    return config