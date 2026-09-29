from typing import Dict, Any
from contracts.adapter import AdapterContract
from contracts.agent_contract import AgentContract

class PortableAdapter(AdapterContract):
    """A portable adapter implementation providing framework-neutral interface."""
    
    def __init__(self, agent: AgentContract):
        super().__init__(agent)
        
    def execute(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Translates a generic dictionary payload to AgentCore execution."""
        return self.agent.execute_tool(tool_name, payload)
