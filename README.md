# MCP Tool Descriptions Tutorial

This repository demonstrates the critical importance of clear and accurate MCP (Model Context Protocol) tool descriptions through a practical todo management example. It accompanies the blog post "[BLOG_POST_TITLE]" ([BLOG_POST_URL]).

The project shows how poor documentation can significantly impact AI assistant performance by comparing two functionally identical MCP servers - one with excellent documentation and another with deliberately poor descriptions.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-tool-descriptions.git
cd mcp-tool-descriptions

# Install dependencies
uv sync

# Set up environment variables
cp dist.env.local .env.local
# Edit .env.local to add your ANTHROPIC_API_KEY
```

## Usage

### Running with Good Documentation

The good server demonstrates best practices with clear tool descriptions, helpful parameter documentation, and consistent error messages:

```bash
uv run src/todo_client.py --good
```

**Example conversation:**
```
You: add a task to buy groceries with high priority
Claude: [GOOD_EXAMPLE_RESPONSE_PLACEHOLDER]

You: show me all my tasks
Claude: [GOOD_EXAMPLE_RESPONSE_PLACEHOLDER]

You: mark task 1 as completed
Claude: [GOOD_EXAMPLE_RESPONSE_PLACEHOLDER]
```

### Running with Poor Documentation

The bad server demonstrates problematic practices with minimal descriptions, cryptic field names, and unclear error messages:

```bash
uv run src/todo_client.py --bad
```

**Example conversation:**
```
You: add a task to buy groceries with high priority
Claude: [BAD_EXAMPLE_RESPONSE_PLACEHOLDER]

You: show me all my tasks
Claude: [BAD_EXAMPLE_RESPONSE_PLACEHOLDER]

You: mark task 1 as completed
Claude: [BAD_EXAMPLE_RESPONSE_PLACEHOLDER]
```

### Testing Individual Servers

You can also test the MCP servers individually using the MCP Inspector:

```bash
# Test the good server
npx @modelcontextprotocol/inspector uv run src/good_todo_server.py

# Test the bad server
npx @modelcontextprotocol/inspector uv run src/bad_todo_server.py
```

Open http://localhost:5173 in your browser to interact with the tools directly.

### Documentation Generation

Generate API documentation for the servers:

```bash
# Generate HTML documentation
python scripts/generate_docs.py

# Serve documentation locally
python scripts/serve_docs.py
```

Visit http://localhost:8080/src/ to view the generated documentation.

## Key Differences

| Aspect | Good Server | Bad Server |
|--------|-------------|------------|
| **Tool Names** | `create_todo`, `list_todos`, `update_todo`, `delete_todo` | `create`, `list`, `update`, `delete` |
| **Descriptions** | Detailed, actionable descriptions | Single words: "Create.", "List.", etc. |
| **Parameters** | Fully documented with examples | No descriptions provided |
| **Response Fields** | Clear names: `title`, `description`, `priority`, `completed` | Cryptic abbreviations: `t`, `de`, `pr`, `co` |
| **Error Messages** | Specific, helpful context | Generic, unhelpful |

## Architecture

The project demonstrates the MCP Host pattern:

- **MCP Client** (`todo_client.py`): Acts as an MCP Host, connecting to servers and providing a natural language interface via Claude API
- **MCP Servers** (`good_todo_server.py`, `bad_todo_server.py`): Expose todo management functionality as MCP tools
- **Communication Flow**: User → Client (AI interpretation) → Server (tool execution) → Client (response formatting) → User


## Requirements

- Python 3.13+
- UV package manager
- Anthropic API key (for the client)

## License

This project is released under the MIT License. See LICENSE for details.