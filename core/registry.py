from typing import Any, Dict
from contracts.tool_contract import ToolContract

class DynamicToolRegistry:
    """Registry to manage and execute dynamic tools safely."""
    
    def __init__(self):
        self._tools: Dict[str, ToolContract] = {}

    def register(self, tool: ToolContract) -> None:
        """Register a tool, preventing duplicates."""
        if not isinstance(tool, ToolContract):
            raise TypeError("Tool must implement ToolContract")
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> ToolContract:
        """Retrieve a registered tool."""
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not found.")
        return self._tools[tool_name]

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def execute(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool dynamically and return structured results."""
        try:
            tool = self.get(tool_name)
            # Input validation would be enforced here or within the tool.
            # Assuming tool handles validation appropriately based on requirements.
            result = tool.execute(input_data)
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
        except KeyError as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": {
                    "type": "MissingToolError",
                    "message": str(e)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            }
