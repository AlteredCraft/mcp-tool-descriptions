#!/usr/bin/env python3
"""
Serve the generated HTML documentation locally for viewing.
"""

import http.server
import socketserver
import os
from pathlib import Path

def main():
    """Start a simple HTTP server to view the documentation."""
    
    # Get the docs directory (parent of scripts directory)
    docs_dir = Path(__file__).parent.parent / "docs" / "api"
    
    if not docs_dir.exists():
        print("❌ Documentation not found. Run generate_docs.py first!")
        return
    
    # Change to the docs directory
    os.chdir(docs_dir)
    
    # Start the server
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"📚 Serving documentation at http://localhost:{PORT}/src/")
    print("Press Ctrl+C to stop the server")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()