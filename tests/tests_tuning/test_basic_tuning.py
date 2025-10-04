"""
Simple tests for BasicTuner - focus on basic functionality
"""

import pytest
from unittest.mock import patch, MagicMock

# Simple test that doesn't require complex mocking
class TestBasicTuner:
    """Simple tests for BasicTuner core functionality"""
    
    def test_init(self):
        """Test basic initialization"""
        # Mock the heavy dependencies at import time
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.basic_tuning import BasicTuner
            
            tuner = BasicTuner()
            assert tuner.model_name == "qwen3:1.7b"
            assert tuner.device in ["cpu", "cuda", "mps"]
            assert tuner.tokenizer is None
            assert tuner.model is None
            assert tuner.config is None
            assert tuner.registry is None
    
    def test_config_override(self):
        """Test configuration override"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.basic_tuning import BasicTuner
            
            tuner = BasicTuner(model_name="llama3.2:1b")
            assert tuner.model_name == "llama3.2:1b"
            # Device can be cpu, cuda, or mps depending on system
            assert tuner.device in ["cpu", "cuda", "mps"]
            assert tuner.config is None
            assert tuner.registry is None
    
    def test_model_name_mapping(self):
        """Test that model names are stored correctly"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.basic_tuning import BasicTuner
            
            # Test different model names
            tuner1 = BasicTuner(model_name="llama3.2:1b")
            assert tuner1.model_name == "llama3.2:1b"
            
            tuner2 = BasicTuner(model_name="qwen3:1.7b")
            assert tuner2.model_name == "qwen3:1.7b"
    
    def test_device_detection(self):
        """Test device detection logic"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.basic_tuning import BasicTuner
            
            tuner = BasicTuner()
            # Device should be one of the expected values
            assert tuner.device in ["cpu", "cuda", "mps"]
    
    def test_basic_properties(self):
        """Test basic properties are accessible"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.basic_tuning import BasicTuner
            
            tuner = BasicTuner()
            
            # Test that properties exist and are accessible
            assert hasattr(tuner, 'model_name')
            assert hasattr(tuner, 'device')
            assert hasattr(tuner, 'tokenizer')
            assert hasattr(tuner, 'model')
            assert hasattr(tuner, 'config')
            assert hasattr(tuner, 'registry')
            
            # Test that they have expected initial values
            assert tuner.tokenizer is None
            assert tuner.model is None
            assert tuner.config is None
            assert tuner.registry is None