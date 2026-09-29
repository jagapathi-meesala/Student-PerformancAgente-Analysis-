from typing import Dict
from contracts.adapter import AdapterContract

class AdapterRegistry:
    """Registry for managing multiple framework adapters if needed."""
    
    def __init__(self):
        self._adapters: Dict[str, AdapterContract] = {}

    def register(self, name: str, adapter: AdapterContract) -> None:
        if not isinstance(adapter, AdapterContract):
            raise TypeError("Adapter must implement AdapterContract")
        self._adapters[name] = adapter
        
    def get(self, name: str) -> AdapterContract:
        if name not in self._adapters:
            raise KeyError(f"Adapter '{name}' not found.")
        return self._adapters[name]
