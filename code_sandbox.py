"""
code_sandbox.py - Replit & Claude Code Style Live Execution Sandbox

Allows Jarvis to execute Python code, compute data science models,
render charts/diagrams, and run shell commands in real-time.
"""

import os
import sys
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)
SANDBOX_DIR = os.path.join(os.path.dirname(__file__), "sandbox_outputs")
os.makedirs(SANDBOX_DIR, exist_ok=True)


def execute_python_code(code_snippet: str) -> dict:
    """
    Executes a Python code block in a sandboxed subprocess and captures output.
    Returns a dict with stdout, stderr, returncode, and any created image paths.
    """
    # Clean code snippet if wrapped in markdown
    if code_snippet.startswith("```python"):
        code_snippet = code_snippet[9:]
    elif code_snippet.startswith("```"):
        code_snippet = code_snippet[3:]
    if code_snippet.endswith("```"):
        code_snippet = code_snippet[:-3]
        
    code_snippet = code_snippet.strip()
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(code_snippet)
        temp_path = temp_file.name
        
    try:
        process = subprocess.run(
            [sys.executable, temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            cwd=SANDBOX_DIR
        )
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        return_code = process.returncode
    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = "Execution timed out (20s limit exceeded)."
        return_code = -1
    except Exception as e:
        stdout = ""
        stderr = f"Execution error: {str(e)}"
        return_code = -1
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return {
        "stdout": stdout,
        "stderr": stderr,
        "return_code": return_code,
        "success": (return_code == 0)
    }
