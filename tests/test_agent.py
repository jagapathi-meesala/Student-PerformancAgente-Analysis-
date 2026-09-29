import pytest
from core.agent import AgentCore
from core.registry import DynamicToolRegistry

def test_agent_initialization():
    agent = AgentCore()
    assert agent.metadata["name"] == "student-performance-analysis"
    assert isinstance(agent.registry, DynamicToolRegistry)

def test_agent_load_tools(tmp_path):
    agent = AgentCore()
    # Assuming tools are loaded successfully if tools directory exists
    import os
    tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools"))
    agent.load_tools_from_directory(tools_dir)
    tools = agent.list_tools()
    assert len(tools) == 7
    assert "analyze-student-performance" in tools
    assert "detect-performance-risk" in tools
