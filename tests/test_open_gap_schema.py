import os
import pytest

def test_manifest_schema_basic():
    """Basic validation for agent.yaml fields without external network dependency."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed, skipping manifest test.")
        
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    manifest_path = os.path.join(project_root, "agent.yaml")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    assert "name" in data, "name field missing"
    assert "version" in data, "version field missing"
    assert "description" in data, "description field missing"
    assert data["name"] == "student-performance-analysis"
    
    # We do not strictly validate with jsonschema against the remote OpenGAP
    # URL because it requires internet and is prone to break in minimal test environments,
    # but the structure is verified to have required fields.
