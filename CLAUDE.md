# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an educational MCP (Model Context Protocol) tutorial demonstrating a todo management system with:
- An MCP server exposing todo operations as tools
- An MCP client providing a natural language interface via Claude API
- Documentation generation for API reference

## Running the Code

```bash
# Run the MCP server
uv run src/todo_server.py

# Run the MCP client (requires ANTHROPIC_API_KEY in .env.local)
uv run src/todo_client.py

# Test server with MCP Inspector
npx @modelcontextprotocol/inspector uv run src/todo_server.py
```

## Documentation Generation

```bash
# Generate HTML API documentation
python scripts/generate_docs.py

# Serve documentation locally (http://localhost:8080/src/)
python scripts/serve_docs.py
```

## Architecture

The codebase demonstrates the MCP Host pattern:

1. **todo_server.py**: FastMCP server exposing tools (create_todo, list_todos, update_todo, delete_todo)
2. **todo_client.py**: MCP host with two key classes:
   - `TodoMCPClient`: Handles MCP protocol communication over stdio
   - `TodoChatClient`: Orchestrates natural language interaction using Claude API

Communication flow: User → Client (interprets with AI) → Server (executes tools) → Client (formats response) → User

## Environment Setup

1. Copy `dist.env.local` to `.env.local`
2. Add your `ANTHROPIC_API_KEY`
3. Optionally set `HTTPS_PROXY` for corporate networks

## Purpose

This example showcases the importance of clear MCP tool descriptions and error responses. The current implementation demonstrates best practices with well-documented tools and consistent error handling.