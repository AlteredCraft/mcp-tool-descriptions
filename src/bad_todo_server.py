#!/usr/bin/env python3
"""
BAD MCP Todo Server - Anti-Example Demonstrating Poor Tool Descriptions

This server intentionally demonstrates POOR practices for MCP tool descriptions
and error handling. It serves as a contrast to good_todo_server.py to highlight
the importance of clear, accurate documentation in MCP implementations.

DO NOT USE THIS CODE IN PRODUCTION - IT'S INTENTIONALLY BAD!

Issues demonstrated:
- Cryptic field names that are unclear to the AI
- Missing tool descriptions
- Missing parameter descriptions
- Abbreviated function names
"""
from typing import Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP
from pydantic import Field

# In-memory storage for todos - in production, this would be a database
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
mcp = FastMCP("Todo Server")

@mcp.tool()
def create(
    # BAD: No field descriptions - AI has to guess what these parameters do
    title: Annotated[str, Field()],
    description: Annotated[str, Field(default="")],
    priority: Annotated[str, Field(default="medium", pattern="^(low|medium|high)$")]
) -> Dict[str, Any]:
    """Create."""
    # BAD: Minimal, unhelpful tool description
    todo_id = todo_store.get_next_id()

    # BAD: Cryptic field names - AI won't understand the response structure
    todo = {
        "id": todo_id,
        "t": title,           # title -> "t"
        "de": description,    # description -> "de"  
        "pr": priority,       # priority -> "pr"
        "co": False,          # completed -> "co"
        "ca": datetime.now().isoformat()  # created_at -> "ca"
    }

    todo_store.todos[todo_id] = todo

    return {"success": True, "todo": todo}

@mcp.tool()
def list(
    # BAD: No parameter description
    status: Annotated[str, Field(default="all", pattern="^(all|completed|pending)$")]
) -> Dict[str, Any]:
    """List."""
    # BAD: Minimal, unhelpful tool description
    filtered_todos = []

    for todo in todo_store.todos.values():
        if status == "all":
            filtered_todos.append(todo)
        elif status == "completed" and todo["co"]:  # Using cryptic "co" field
            filtered_todos.append(todo)
        elif status == "pending" and not todo["co"]:
            filtered_todos.append(todo)

    return {
        "todos": filtered_todos,
        "count": len(filtered_todos),
        "total": len(todo_store.todos)
    }

@mcp.tool()
def update(
    # BAD: No parameter descriptions at all
    todo_id: Annotated[int, Field()],
    title: Annotated[Optional[str], Field(default=None)],
    description: Annotated[Optional[str], Field(default=None)],
    priority: Annotated[Optional[str], Field(default=None, pattern="^(low|medium|high)$")],
    completed: Annotated[Optional[bool], Field(default=None)]
) -> Dict[str, Any]:
    """Update."""
    # BAD: Minimal, unhelpful tool description
    if todo_id not in todo_store.todos:
        return {"success": False, "error": f"Todo {todo_id} not found"}

    todo = todo_store.todos[todo_id]

    # BAD: Using cryptic field names throughout
    if title is not None:
        todo["t"] = title
    if description is not None:
        todo["de"] = description
    if priority is not None:
        todo["pr"] = priority
    if completed is not None:
        todo["co"] = completed

    todo["updated_at"] = datetime.now().isoformat()

    return {"success": True, "todo": todo}

@mcp.tool()
def delete(
    # BAD: No parameter description
    todo_id: Annotated[int, Field()]
) -> Dict[str, Any]:
    """Delete."""
    # BAD: Minimal, unhelpful tool description
    if todo_id not in todo_store.todos:
        return {"success": False, "error": f"Todo {todo_id} not found"}

    deleted_todo = todo_store.todos.pop(todo_id)
    return {"success": True, "deleted_todo": deleted_todo}


if __name__ == "__main__":
    mcp.run()