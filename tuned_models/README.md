# Tuned Models Directory

This directory contains all tuned model versions organized by model type and version.

## Directory Structure

```
tuned_models/
├── README.md                          # This file
├── llama_1b/                          # Laptop configuration (1B parameter model)
│   ├── model_registry.json            # Version metadata and registry
│   ├── v1.0/                          # Version 1.0
│   │   ├── README.md                  # Version-specific documentation
│   │   ├── model_info.json            # Training metadata
│   │   ├── pytorch_model.bin          # Model weights (actual training)
│   │   ├── config.json                # Model configuration (actual training)
│   │   └── tokenizer.json             # Tokenizer config (actual training)
│   └── v1.1/                          # Version 1.1
│       ├── README.md
│       ├── model_info.json
│       └── [model files...]
└── llama_8b/                          # PC configuration (8B parameter model)
    ├── model_registry.json            # Version metadata and registry
    └── v1.0/                          # Version 1.0
        ├── README.md
        ├── model_info.json
        └── [model files...]
```

## Model Registry

Each model type has a `model_registry.json` file that tracks:
- All versions and their metadata
- Training parameters (epochs, batch size, learning rate)
- Training metrics (time, loss, model size)
- Active version status
- Notes and descriptions

## Version Management

Use the model manager CLI to interact with versions:

```bash
# List all versions
python -m tuning.model_manager list

# Set active version
python -m tuning.model_manager set-active v1.1

# Show version details
python -m tuning.model_manager info v1.0

# Show active version
python -m tuning.model_manager active
```

## Hardware Configurations

- **llama_1b/**: Optimized for laptop/CPU training
  - Model: llama3.2:1b (1B parameters)
  - Batch size: 1
  - Epochs: 1 (quick training)
  - Device: CPU

- **llama_8b/**: Optimized for PC/GPU training
  - Model: qwen3:8b (8B parameters)
  - Batch size: 8
  - Epochs: 3 (full training)
  - Device: CUDA

## Adding New Versions

When you run training, new versions are automatically created:
1. Version number auto-increments (v1.0 → v1.1 → v1.2)
2. New directory created with version name
3. Model files saved to version directory
4. Metadata added to registry
5. Version can be set as active

## File Descriptions

- **model_registry.json**: Central registry of all versions
- **model_info.json**: Training metadata for specific version
- **README.md**: Human-readable documentation for each version
- **pytorch_model.bin**: Actual model weights (created during training)
- **config.json**: Model configuration (created during training)
- **tokenizer.json**: Tokenizer configuration (created during training)
