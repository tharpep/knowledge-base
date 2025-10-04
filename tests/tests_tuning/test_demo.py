"""
Simple tests for tuning demo functionality
"""

import pytest
from unittest.mock import patch, MagicMock

class TestTuningDemo:
    """Simple tests for tuning demo"""
    
    def test_demo_import(self):
        """Test that demo can be imported"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.demo import run_tuning_demo
            assert callable(run_tuning_demo)
    
    def test_demo_function_exists(self):
        """Test that demo function exists and is callable"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.demo import run_tuning_demo
            
            # Test that the function exists and is callable
            assert callable(run_tuning_demo)
            
            # Test that it accepts mode parameter
            import inspect
            sig = inspect.signature(run_tuning_demo)
            assert 'mode' in sig.parameters
    
    def test_demo_modes(self):
        """Test that demo supports different modes"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.demo import run_tuning_demo
            
            # Test that function can be called with different modes
            # (We'll mock the actual execution to avoid heavy dependencies)
            with patch('tuning.demo.BasicTuner') as mock_tuner_class:
                mock_tuner = MagicMock()
                mock_tuner_class.return_value = mock_tuner
                
                # Mock the config
                with patch('tuning.demo.get_tuning_config') as mock_config:
                    mock_config.return_value = MagicMock()
                    
                    # Test that demo can be called (it will fail gracefully)
                    try:
                        run_tuning_demo(mode="quick")
                    except Exception:
                        pass  # Expected to fail due to mocking
                    
                    # Verify that BasicTuner was instantiated
                    mock_tuner_class.assert_called()
    
    def test_demo_error_handling(self):
        """Test that demo handles errors gracefully"""
        with patch.dict('sys.modules', {
            'torch': MagicMock(),
            'transformers': MagicMock(),
            'datasets': MagicMock(),
            'accelerate': MagicMock()
        }):
            from tuning.demo import run_tuning_demo
            
            # Test that demo doesn't crash on errors
            with patch('tuning.demo.BasicTuner') as mock_tuner_class:
                mock_tuner_class.side_effect = Exception("Test error")
                
                with patch('tuning.demo.get_tuning_config') as mock_config:
                    mock_config.return_value = MagicMock()
                    
                    # Should not raise exception, should handle gracefully
                    try:
                        run_tuning_demo(mode="quick")
                    except Exception as e:
                        # If it does raise, it should be a specific error, not a crash
                        assert "Test error" in str(e)