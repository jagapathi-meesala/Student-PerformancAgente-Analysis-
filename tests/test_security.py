import os
import tempfile

EXCLUDE_DIRS = {
    ".venv", "venv", "env", "__pycache__", ".pytest_cache", 
    ".git", "node_modules", "dist", "build", "tests"
}

def check_file_for_secrets(filepath):
    """Check for hardcoded secrets in files."""
    if not filepath.endswith((".py", ".yaml", ".md")):
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        if any(secret in content for secret in ['sk-ant', 'sk-proj', "api_key =", "password =", "secret =", "token ="]):
            return True
    return False

def test_no_unsafe_code():
    """Verify that eval and exec are not used in core or tools."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    unsafe_patterns = ['eval(', 'exec(', 'os.system(', 'subprocess.']
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                # Skip this test file to prevent false positives from pattern literals
                if os.path.abspath(path) == os.path.abspath(__file__):
                    continue
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in unsafe_patterns:
                        assert pattern not in content, f"Unsafe code '{pattern}' found in {path}"

def test_no_secrets():
    """Verify no hardcoded API keys are present."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # The actual readiness_audit.py has its own secret scanning implementation
    # that we need to ensure doesn't flag itself, but here we just test that
    # the rest of the project is clean.
    
    # We want to skip readiness_audit.py in our own test scan too, 
    # since it contains the secret literal patterns for its own tests.
    audit_script = os.path.normpath(os.path.join(project_root, "verification", "readiness_audit.py"))
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            path = os.path.normpath(os.path.join(root, file))
            # Skip this test file and the readiness audit script
            if os.path.abspath(path) == os.path.abspath(__file__) or os.path.abspath(path) == os.path.abspath(audit_script):
                continue
            
            has_secret = check_file_for_secrets(path)
            assert not has_secret, f"Hardcoded secret found in {path}"

def test_secret_detection_mechanism():
    """Prove that an actual hardcoded secret placed in a scanned source file would be detected."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("api_key = 'sk-ant-123456'\n")
        temp_path = f.name
        
    try:
        assert check_file_for_secrets(temp_path) is True
    finally:
        os.remove(temp_path)
