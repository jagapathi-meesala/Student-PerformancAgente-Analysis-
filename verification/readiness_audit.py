import os
import sys

REQUIRED_FILES = [
    "agent.yaml",
    "SOUL.md",
    "RULES.md",
    "DUTIES.md",
    "AGENTS.md",
    "README.md",
    "EXPLAINABILITY.md",
    "config/__init__.py",
    "config/settings.py",
    "contracts/__init__.py",
    "contracts/agent_contract.py",
    "contracts/tool_contract.py",
    "contracts/adapter.py",
    "adapters/__init__.py",
    "adapters/registry.py",
    "adapters/portable_adapter.py",
    "core/__init__.py",
    "core/agent.py",
    "core/registry.py",
    "tools/__init__.py",
    "tools/analyze-student-performance.py",
    "tools/analyze-subject-performance.py",
    "tools/analyze-attendance.py",
    "tools/detect-performance-risk.py",
    "tools/calculate-grade-summary.py",
    "tools/analyze-performance-trend.py",
    "tools/generate-improvement-plan.py",
    "tests/__init__.py",
    "tests/test_agent.py",
    "tests/test_registry.py",
    "tests/test_tools.py",
    "tests/test_security.py",
    "tests/test_documentation.py",
    "tests/test_adapters.py",
    "tests/test_open_gap_schema.py",
]

EXCLUDE_DIRS = {
    ".venv", "venv", "env", "__pycache__", ".pytest_cache", 
    ".git", "node_modules", "dist", "build", "tests"
}

def check_file_exists(filepath: str) -> bool:
    return os.path.isfile(filepath)

def check_file_for_secrets(filepath: str) -> bool:
    """Basic check to ensure no obvious secrets are hardcoded in files."""
    if not filepath.endswith((".py", ".yaml", ".md")):
        return False
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            if any(secret in content for secret in ['sk-ant', 'sk-proj', "api_key =", "password =", "secret =", "token ="]):
                return True
    except Exception:
        pass
    return False

def audit():
    print("Starting Readiness Audit...")
    failed = False
    
    # Check required files
    for file in REQUIRED_FILES:
        if not check_file_exists(file):
            print(f"FAILED: Required file missing - {file}")
            failed = True
            
    # Check .env
    if check_file_exists(".env"):
        print("FAILED: .env file is tracked or present! Should be ignored.")
        failed = True
        
    # Check secrets
    # Use os.path.abspath to safely exclude this specific file from its own scan
    current_script_path = os.path.abspath(__file__)
    
    for root, dirs, files in os.walk("."):
        # Modify dirs in place to robustly exclude specified directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            path = os.path.normpath(os.path.join(root, file))
            
            # Skip this audit script itself since it contains the secret patterns
            if os.path.abspath(path) == current_script_path:
                continue
                
            if check_file_for_secrets(path):
                print(f"FAILED: Potential hardcoded secret found in {path}")
                failed = True

    if failed:
        print("\nReadiness Audit: FAILED")
        sys.exit(1)
    else:
        print("\nReadiness Audit: PASSED")
        sys.exit(0)

if __name__ == "__main__":
    audit()
