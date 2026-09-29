from abc import ABC, abstractmethod
from typing import Any, Dict

class ToolContract(ABC):
    """Base contract for all deterministic tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The tool's unique name (kebab-case)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass
        
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema defining the expected input."""
        pass

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the tool deterministically based on input_data."""
        pass
