# Model Version v1.0

This directory contains the tuned model files for version v1.0.

## Files:
- `pytorch_model.bin` - The actual model weights (not included in this example)
- `config.json` - Model configuration (not included in this example)
- `tokenizer.json` - Tokenizer configuration (not included in this example)
- `model_info.json` - Training metadata and statistics

## Training Details:
- **Model**: qwen3:8b
- **Base Model**: Qwen/Qwen2.5-7B
- **Training Epochs**: 3
- **Batch Size**: 8
- **Learning Rate**: 5e-05
- **Device**: cuda
- **Training Time**: 180.5 seconds
- **Final Loss**: 1.8765
- **Model Size**: 14.2 MB

## Notes:
PC training with GPU acceleration
