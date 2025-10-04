"""
Model Registry for tracking tuned model versions and metadata
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ModelVersion:
    """Metadata for a single model version"""
    version: str
    model_name: str
    base_model: str
    created_at: str
    training_epochs: int
    batch_size: int
    learning_rate: float
    device: str
    training_time_seconds: Optional[float] = None
    final_loss: Optional[float] = None
    model_size_mb: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool = True


class ModelRegistry:
    """Registry for managing tuned model versions"""
    
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._versions: Dict[str, ModelVersion] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load existing registry from file"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for version_str, version_data in data.items():
                        self._versions[version_str] = ModelVersion(**version_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load model registry: {e}")
                self._versions = {}
        else:
            self._versions = {}
    
    def _save_registry(self):
        """Save registry to file"""
        data = {version: asdict(model_version) for version, model_version in self._versions.items()}
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_version(self, model_version: ModelVersion) -> None:
        """Register a new model version"""
        self._versions[model_version.version] = model_version
        self._save_registry()
        print(f"✅ Registered model version {model_version.version}")
    
    def get_version(self, version: str) -> Optional[ModelVersion]:
        """Get a specific model version"""
        return self._versions.get(version)
    
    def get_all_versions(self) -> List[ModelVersion]:
        """Get all registered versions"""
        return list(self._versions.values())
    
    def get_latest_version(self) -> Optional[ModelVersion]:
        """Get the latest (most recent) version"""
        if not self._versions:
            return None
        
        # Sort by creation date
        versions = sorted(self._versions.values(), 
                         key=lambda v: v.created_at, 
                         reverse=True)
        return versions[0]
    
    def get_active_version(self) -> Optional[ModelVersion]:
        """Get the currently active version"""
        active_versions = [v for v in self._versions.values() if v.is_active]
        if not active_versions:
            return None
        
        # Return the most recent active version
        return sorted(active_versions, key=lambda v: v.created_at, reverse=True)[0]
    
    def set_active_version(self, version: str) -> bool:
        """Set a version as active (deactivates others)"""
        if version not in self._versions:
            print(f"❌ Version {version} not found")
            return False
        
        # Deactivate all versions
        for v in self._versions.values():
            v.is_active = False
        
        # Activate the specified version
        self._versions[version].is_active = True
        self._save_registry()
        print(f"✅ Set version {version} as active")
        return True
    
    def list_versions(self) -> None:
        """Print all registered versions"""
        if not self._versions:
            print("No model versions registered")
            return
        
        print("\n=== Model Versions ===")
        versions = sorted(self._versions.values(), 
                         key=lambda v: v.created_at, 
                         reverse=True)
        
        for version in versions:
            status = "🟢 ACTIVE" if version.is_active else "⚪"
            print(f"{status} {version.version}")
            print(f"   Model: {version.model_name}")
            print(f"   Created: {version.created_at}")
            print(f"   Training: {version.training_epochs} epochs, batch_size={version.batch_size}")
            if version.training_time_seconds:
                print(f"   Training time: {version.training_time_seconds:.1f}s")
            if version.final_loss:
                print(f"   Final loss: {version.final_loss:.4f}")
            if version.notes:
                print(f"   Notes: {version.notes}")
            print()
    
    def get_version_path(self, version: str) -> Optional[str]:
        """Get the file path for a specific version"""
        version_obj = self.get_version(version)
        if not version_obj:
            return None
        
        # Construct path based on version
        base_dir = self.registry_path.parent
        return str(base_dir / version)
    
    def create_new_version(self, 
                          model_name: str,
                          base_model: str,
                          training_epochs: int,
                          batch_size: int,
                          learning_rate: float,
                          device: str,
                          notes: Optional[str] = None) -> ModelVersion:
        """Create a new version with auto-incremented version number"""
        
        # Find the next version number
        existing_versions = [v for v in self._versions.keys() if v.startswith('v')]
        if not existing_versions:
            next_version = "v1.0"
        else:
            # Extract version numbers and increment
            version_numbers = []
            for v in existing_versions:
                try:
                    # Extract number from "v1.0", "v1.1", etc.
                    num = float(v[1:])
                    version_numbers.append(num)
                except ValueError:
                    continue
            
            if version_numbers:
                next_version = f"v{max(version_numbers) + 0.1:.1f}"
            else:
                next_version = "v1.0"
        
        # Create new version
        new_version = ModelVersion(
            version=next_version,
            model_name=model_name,
            base_model=base_model,
            created_at=datetime.now().isoformat(),
            training_epochs=training_epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            device=device,
            notes=notes
        )
        
        return new_version


def get_model_registry(config) -> ModelRegistry:
    """Get model registry instance for the given config"""
    return ModelRegistry(config.model_registry_path)
