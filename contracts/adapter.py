from abc import ABC, abstractmethod
from typing import Any, Dict
from contracts.agent_contract import AgentContract

class AdapterContract(ABC):
    """Adapter interface for framework interoperability."""
    
    def __init__(self, agent: AgentContract):
        self.agent = agent

    @abstractmethod
    def execute(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Translates a generic request into an AgentCore execution."""
        pass
