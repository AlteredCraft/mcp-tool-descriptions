#!/usr/bin/env python3
"""
MCP Todo Server - A Model Context Protocol Server Implementation

This server demonstrates how to build an MCP (Model Context Protocol) server
that exposes tools and resources for AI assistants to interact with. MCP enables
standardized communication between AI applications and external systems.

Key MCP Concepts Demonstrated:
1. Tools: Functions that AI can call to perform actions (create, read, update, delete todos)
2. Resources: Data endpoints that AI can query (todo list resource)
3. FastMCP: A Python framework that simplifies MCP server creation

The Model Context Protocol (MCP) provides:
- Standardized way for LLMs to discover and use external tools
- Type-safe parameter validation and error handling
- Automatic JSON schema generation for tool parameters
- Support for both synchronous and asynchronous operations

For developers learning AI integration:
- MCP servers expose your application's functionality as "tools" that AI can discover and use
- The protocol handles all communication details between AI clients and your server
- FastMCP makes it easy to turn Python functions into AI-accessible tools
- This pattern enables building AI-augmented applications without tight coupling

Architecture Overview:
- AI Assistant (Claude, ChatGPT, etc.) ← MCP Protocol → MCP Server (this code)
- The AI decides when and how to use tools based on user requests
- The server validates inputs and executes the requested operations
- Results are returned to the AI for interpretation and presentation

Testing with MCP Inspector:
- Run standalone: `uv run src/todo_server.py`
- With Inspector: `npx @modelcontextprotocol/inspector uv run src/todo_server.py`
- Open browser to http://localhost:5173 to interact with tools and resources
- The Inspector lets you manually test tools and see the MCP protocol messages
"""
from typing import Dict, Any, Optional, Annotated
from datetime import datetime
import json

from fastmcp import FastMCP
from pydantic import Field

# In-memory storage for todos - in production, this would be a database
# This demonstrates that MCP servers can work with any data storage backend
class TodoStore:
    def __init__(self):
        self.todos: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def get_next_id(self) -> int:
        current_id = self._next_id
        self._next_id += 1
        return current_id

todo_store = TodoStore()

# Initialize the MCP server with a descriptive name
# This name helps AI assistants understand what the server provides
mcp = FastMCP("Todo Server")

@mcp.tool()
def create_todo(
    title: Annotated[str, Field(description="Brief description of the task to be done")],
    description: Annotated[str, Field(default="", description="Additional details or context about the task")],
    priority: Annotated[str, Field(default="medium", description="Task importance: 'low', 'medium', or 'high'", pattern="^(low|medium|high)$")]
) -> Dict[str, Any]:
    """Add a new task to the todo list with specified details."""
    todo_id = todo_store.get_next_id()

    # Create the todo object with all necessary fields
    todo = {
        "id": todo_id,
        "title": title,
        "description": description,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }

    # Store in our in-memory database
    todo_store.todos[todo_id] = todo

    # Return a structured response that AI can interpret
    return {"success": True, "todo": todo}

@mcp.tool()
def list_todos(
    status: Annotated[str, Field(default="all", description="Filter tasks by: 'all', 'completed', or 'pending'", pattern="^(all|completed|pending)$")]
) -> Dict[str, Any]:
    """Retrieve todos filtered by completion status."""
    filtered_todos = []

    # Filter todos based on the requested status
    for todo in todo_store.todos.values():
        if status == "all":
            filtered_todos.append(todo)
        elif status == "completed" and todo["completed"]:
            filtered_todos.append(todo)
        elif status == "pending" and not todo["completed"]:
            filtered_todos.append(todo)

    # Return structured data that AI can process and present to users
    return {
        "todos": filtered_todos,
        "count": len(filtered_todos),
        "total": len(todo_store.todos)
    }

@mcp.tool()
def update_todo(
    todo_id: Annotated[int, Field(description="The ID number of the task to modify")],
    title: Annotated[Optional[str], Field(default=None, description="New title for the task")],
    description: Annotated[Optional[str], Field(default=None, description="New description or details")],
    priority: Annotated[Optional[str], Field(default=None, description="New priority: 'low', 'medium', or 'high'", pattern="^(low|medium|high)$")],
    completed: Annotated[Optional[bool], Field(default=None, description="Mark as done (true) or not done (false)")]
) -> Dict[str, Any]:
    """Modify an existing todo's properties or mark it complete."""
    # Validate the todo exists
    if todo_id not in todo_store.todos:
        return {"success": False, "error": f"Todo {todo_id} not found"}

    todo = todo_store.todos[todo_id]

    # Update only the fields that were provided
    if title is not None:
        todo["title"] = title
    if description is not None:
        todo["description"] = description
    if priority is not None:
        todo["priority"] = priority
    if completed is not None:
        todo["completed"] = completed

    # Track when the todo was last modified
    todo["updated_at"] = datetime.now().isoformat()

    return {"success": True, "todo": todo}

@mcp.tool()
def delete_todo(
    todo_id: Annotated[int, Field(description="The ID number of the task to remove")]
) -> Dict[str, Any]:
    """Remove a task from the list permanently."""
    # Validate before deletion
    if todo_id not in todo_store.todos:
        return {"success": False, "error": f"Todo {todo_id} not found"}

    # Remove from storage and return the deleted item
    deleted_todo = todo_store.todos.pop(todo_id)
    return {"success": True, "deleted_todo": deleted_todo}


if __name__ == "__main__":
    # Start the MCP server
    # This will handle the MCP protocol over stdin/stdout
    # allowing AI assistants to discover and use our tools
    mcp.run()