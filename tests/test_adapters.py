import pytest
from core.agent import AgentCore
from adapters.portable_adapter import PortableAdapter
from contracts.tool_contract import ToolContract

class DummyTool(ToolContract):
    @property
    def name(self): return "test-tool"
    @property
    def description(self): return "dummy"
    @property
    def input_schema(self): return {}
    def execute(self, input_data): return {"status": "success"}

def test_portable_adapter_execution():
    agent = AgentCore()
    agent.registry.register(DummyTool())
    
    adapter = PortableAdapter(agent)
    result = adapter.execute("test-tool", {})
    
    assert result["success"]
    assert result["tool"] == "test-tool"
    assert result["result"] == {"status": "success"}
