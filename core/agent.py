import os
import importlib.util
from typing import Any, Dict
from contracts.agent_contract import AgentContract
from contracts.tool_contract import ToolContract
from core.registry import DynamicToolRegistry

class AgentCore(AgentContract):
    """Core Agent implementation handling registration and execution."""
    
    def __init__(self):
        self.metadata = {
            "name": "student-performance-analysis",
            "version": "1.0.0",
            "description": "Deterministic analysis agent for structured student academic performance data"
        }
        self.registry = DynamicToolRegistry()
        
    def load_tools_from_directory(self, tools_dir: str) -> None:
        """Dynamically load tools from the specified directory."""
        if not os.path.isdir(tools_dir):
            return
            
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                tool_path = os.path.join(tools_dir, filename)
                module_name = filename[:-3]
                
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(module_name, tool_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Instantiate and register tool class
                    # Assuming each tool file defines a class named 'Tool'
                    if hasattr(module, 'Tool'):
                        tool_instance = module.Tool()
                        if isinstance(tool_instance, ToolContract):
                            self.registry.register(tool_instance)
    
    def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool through the registry."""
        return self.registry.execute(tool_name, input_data)

    def list_tools(self) -> list[str]:
        """List registered tools."""
        return self.registry.list_tools()
