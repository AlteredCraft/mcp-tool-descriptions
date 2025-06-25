#!/usr/bin/env python3
"""
Generate HTML documentation for the MCP Todo Tutorial project.

This script uses pdoc3 to automatically generate API documentation
from the docstrings in our Python code.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Generate HTML documentation using pdoc3."""
    
    # Get the project root directory (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs" / "api"
    
    # Create docs directory if it doesn't exist
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate documentation
    cmd = [
        sys.executable, "-m", "pdoc",
        "--html",
        "--output-dir", str(docs_dir),
        "--force",
        "--config", "show_source_code=True",
        "src.todo_server",
        "src.todo_client"
    ]
    
    print(f"Generating documentation in {docs_dir}...")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Documentation generated successfully!")
        print(f"📁 Open {docs_dir}/src/index.html to view the documentation")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating documentation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()