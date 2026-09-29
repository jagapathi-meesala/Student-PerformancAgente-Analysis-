from abc import ABC, abstractmethod
from typing import Any, Dict

class AgentContract(ABC):
    """Core agent interface."""

    @abstractmethod
    def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a registered tool by name."""
        pass

    @abstractmethod
    def list_tools(self) -> list[str]:
        """Returns a list of registered tool names."""
        pass
