import pytest
from core.registry import DynamicToolRegistry
from contracts.tool_contract import ToolContract

class DummyTool(ToolContract):
    @property
    def name(self): return "dummy-tool"
    @property
    def description(self): return "dummy"
    @property
    def input_schema(self): return {}
    def execute(self, input_data): return {"status": "ok"}

def test_registry_registration():
    registry = DynamicToolRegistry()
    tool = DummyTool()
    registry.register(tool)
    assert "dummy-tool" in registry.list_tools()

def test_registry_duplicate_registration():
    registry = DynamicToolRegistry()
    tool = DummyTool()
    registry.register(tool)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool)

def test_registry_missing_tool():
    registry = DynamicToolRegistry()
    result = registry.execute("nonexistent", {})
    assert not result["success"]
    assert result["error"]["type"] == "MissingToolError"

def test_registry_execution():
    registry = DynamicToolRegistry()
    registry.register(DummyTool())
    result = registry.execute("dummy-tool", {})
    assert result["success"]
    assert result["result"] == {"status": "ok"}
