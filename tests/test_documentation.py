import os

def test_documentation_presence():
    """Verify all required documentation files exist."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    required_docs = [
        "README.md",
        "SOUL.md",
        "RULES.md",
        "DUTIES.md",
        "AGENTS.md",
        "EXPLAINABILITY.md"
    ]
    
    for doc in required_docs:
        path = os.path.join(project_root, doc)
        assert os.path.isfile(path), f"Missing documentation file: {doc}"

def test_manifest_presence():
    """Verify OpenGAP manifest exists."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(project_root, "agent.yaml")
    assert os.path.isfile(path), "Missing agent.yaml manifest"
