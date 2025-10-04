"""
Test AI Gateway functionality
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from llm.gateway import AIGateway


class TestAIGateway:
    """Test cases for AIGateway"""
    
    def test_init_with_config(self):
        """Test gateway initialization with config"""
        config = {
            "purdue": {"api_key": "test-key"},
            "ollama": {"base_url": "http://localhost:11434", "default_model": "test-model"}
        }
        
        with patch('llm.gateway.PurdueGenAI') as mock_purdue, \
             patch('llm.gateway.OllamaClient') as mock_ollama:
            
            gateway = AIGateway(config)
            
            # Should initialize both providers
            mock_purdue.assert_called_once_with("test-key")
            mock_ollama.assert_called_once()
    
    def test_init_from_env_vars(self):
        """Test gateway initialization from environment variables"""
        with patch.dict(os.environ, {'PURDUE_API_KEY': 'test-key'}), \
             patch('llm.gateway.PurdueGenAI') as mock_purdue:
            
            gateway = AIGateway()
            mock_purdue.assert_called_once()
    
    def test_init_with_ollama_env(self):
        """Test gateway initialization with Ollama environment variable"""
        with patch.dict(os.environ, {'USE_OLLAMA': 'true', 'USE_LAPTOP': 'true'}), \
             patch('llm.gateway.OllamaClient') as mock_ollama:
            
            gateway = AIGateway()
            mock_ollama.assert_called_once()
    
    def test_get_available_providers(self):
        """Test getting available providers"""
        config = {"purdue": {"api_key": "test-key"}}
        
        with patch('llm.gateway.PurdueGenAI'):
            gateway = AIGateway(config)
            providers = gateway.get_available_providers()
            assert "purdue" in providers
    
    def test_chat_with_provider_selection(self):
        """Test chat with automatic provider selection"""
        config = {"purdue": {"api_key": "test-key"}}
        
        with patch('llm.gateway.PurdueGenAI') as mock_purdue, \
             patch('llm.gateway.get_rag_config') as mock_config:
            # Mock config to prefer Purdue over Ollama
            mock_config.return_value.use_ollama = False
            mock_config.return_value.model_name = "llama3.1:latest"
            
            mock_client = MagicMock()
            mock_client.chat.return_value = "Test response"
            mock_purdue.return_value = mock_client
            
            gateway = AIGateway(config)
            response = gateway.chat("Hello")
            
            assert response == "Test response"
            mock_client.chat.assert_called_once_with("Hello", "llama3.1:latest")
    
    def test_chat_with_specific_provider(self):
        """Test chat with specific provider"""
        config = {"purdue": {"api_key": "test-key"}}
        
        with patch('llm.gateway.PurdueGenAI') as mock_purdue:
            mock_client = MagicMock()
            mock_client.chat.return_value = "Test response"
            mock_purdue.return_value = mock_client
            
            gateway = AIGateway(config)
            response = gateway.chat("Hello", provider="purdue", model="test-model")
            
            assert response == "Test response"
            mock_client.chat.assert_called_once_with("Hello", "test-model")
    
    def test_chat_no_providers_available(self):
        """Test chat when no providers are available"""
        with patch('llm.gateway.get_rag_config') as mock_config, \
             patch('llm.gateway.OllamaClient') as mock_ollama:
            # Mock config to prefer Ollama but no Ollama available
            mock_config.return_value.use_ollama = False  # Don't use Ollama
            mock_config.return_value.model_name = "llama3.2:1b"
            
            # Don't create any providers
            gateway = AIGateway({})
            
            with pytest.raises(Exception, match="No providers available"):
                gateway.chat("Hello")
    
    def test_chat_invalid_provider(self):
        """Test chat with invalid provider"""
        config = {"purdue": {"api_key": "test-key"}}
        
        with patch('llm.gateway.PurdueGenAI'):
            gateway = AIGateway(config)
            
            with pytest.raises(Exception, match="Provider 'invalid' not available"):
                gateway.chat("Hello", provider="invalid")
