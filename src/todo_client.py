#!/usr/bin/env python3
"""
Todo MCP Host Application - Natural Language Interface for Todo Management

This application demonstrates how to build an MCP Host that uses AI to provide
natural language interfaces to external systems through the Model Context Protocol.

Key Concepts for Mid-Level Developers:

1. MCP Host Pattern: This application acts as an MCP Host, similar to Claude Desktop
   or IDEs, that connects to MCP servers to access data and functionality.

2. AI-Powered Orchestration: We use Claude API to interpret user intent and 
   determine which MCP tools to call, but the host application orchestrates
   the entire flow.

3. Natural Language as UI: Instead of building complex UIs, the host uses AI to
   interpret user intent and translate it to MCP tool calls.

4. Structured Communication: The host provides the AI with available MCP tools
   and handles the execution based on AI recommendations.

This pattern represents the future of applications - where MCP hosts can leverage
AI to provide intuitive interfaces while maintaining standardized connections
to various data sources and services.
"""
import asyncio
import os
import sys
import json
import argparse
from typing import Dict, Any, cast, Optional
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic
from anthropic.types import TextBlock, ToolUseBlock
from dotenv import load_dotenv


class TodoMCPClient:
    """MCP client for communicating with the todo server.
    
    This class handles the low-level MCP protocol communication.
    It demonstrates how to:
    - Connect to an MCP server via stdio (standard input/output)
    - Discover available tools from the server
    - Execute tool calls and handle responses
    
    For developers: This abstraction layer allows you to interact with
    MCP servers without dealing with protocol details.
    """
    
    def __init__(self, server_path: Optional[str] = None):
        """Initialize the MCP client.
        
        Args:
            server_path: Path to the MCP server script. If not provided,
                        assumes good_todo_server.py is in the same directory.
        """
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.available_tools = []
        if server_path:
            self.server_path = server_path
        else:
            self.server_path = str(Path(__file__).parent / "good_todo_server.py")
    
    async def connect(self):
        """Connect to the todo server via MCP.
        
        This method demonstrates the MCP connection flow:
        1. Launch the server as a subprocess
        2. Establish stdio communication channels
        3. Initialize the MCP session
        4. Discover available tools
        
        This pattern allows any application to become MCP-enabled
        without modifying its core code.
        """
        # Configure how to launch the MCP server
        server_params = StdioServerParameters(
            command="uv",  # Using uv to run the Python script
            args=["run", self.server_path],
            env=None
        )
        
        # Create stdio transport - MCP communicates over stdin/stdout
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        
        # Create MCP session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        
        # Initialize the connection
        await self.session.initialize()
        
        # Discover available tools - this is key for AI to know what it can do
        response = await self.session.list_tools()
        self.available_tools = response.tools
        print(f"Connected to Todo Server. Available tools: {[tool.name for tool in self.available_tools]}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call (e.g., 'create_todo')
            arguments: Dictionary of arguments to pass to the tool
            
        Returns:
            The tool's response, typically containing result data
            
        This method shows how MCP standardizes tool execution across
        different services, making it easy for AI to interact with
        any MCP-enabled system.
        """
        if self.session is None:
            raise RuntimeError("MCP session not initialized. Call connect() first.")
        result = await self.session.call_tool(tool_name, arguments)
        return result
    
    async def close(self):
        """Close the MCP client connection"""
        await self.exit_stack.aclose()
    
    def get_tools_description(self) -> str:
        """Get a formatted description of available tools.
        
        This method formats tool information for the LLM, helping it
        understand what actions are available. This is crucial for
        effective AI tool selection.
        
        Returns:
            Formatted string describing all available tools and their parameters
        """
        tools_desc = "Available todo management tools:\n"
        for tool in self.available_tools:
            tools_desc += f"- {tool.name}: {tool.description}\n"
            # Include parameter information to help AI understand usage
            if tool.inputSchema and 'properties' in tool.inputSchema:
                tools_desc += f"  Parameters: {list(tool.inputSchema['properties'].keys())}\n"
        return tools_desc


class TodoChatClient:
    """MCP Host application with AI-powered natural language interface.
    
    This class implements the MCP Host pattern:
    1. User speaks in natural language to the host application
    2. Host sends request to AI (Claude API) along with available MCP tools
    3. AI analyzes intent and recommends which MCP tool to use
    4. Host executes the MCP tool call via its MCP client
    5. Host formats and presents results back to the user
    
    This pattern is transformative for software development:
    - Standardizes AI integration through MCP
    - Reduces UI development complexity
    - Makes applications more accessible
    - Enables rapid prototyping of user interactions
    - Allows non-technical users to interact with complex systems
    
    For mid-level developers: This shows how to build MCP hosts that leverage
    AI for natural language interfaces while maintaining proper separation
    between AI services and application logic.
    """
    
    def __init__(self, anthropic_api_key: str, server_path: Optional[str] = None, debug: bool = False):
        """Initialize the chat client.
        
        Args:
            anthropic_api_key: API key for Claude
            server_path: Optional path to the MCP server
            debug: Enable debug logging for tool calls and API requests
        """
        self.mcp_client = TodoMCPClient(server_path=server_path)
        
        # Configure Anthropic client with proxy support if needed
        client_kwargs = {"api_key": anthropic_api_key}
        proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        
        if proxy_url:
            import httpx
            client_kwargs["http_client"] = httpx.Client(
                proxy=proxy_url,
                verify=False  # Disable SSL verification for corporate proxies
            )
        
        self.anthropic_client = anthropic.Anthropic(**client_kwargs)
        self.conversation_history = []
        self.debug = debug
        
        # Determine server type for emoji display
        if server_path and "bad_todo_server" in server_path:
            self.server_emoji = "😈"
        else:
            # Default case or good server
            self.server_emoji = "🤗"
    
    async def start(self):
        """Start the chat client"""
        print("Todo Chat Client - Powered by Claude")
        print("=" * 50)
        print("Connecting to Todo Server...")
        
        await self.mcp_client.connect()
        
        print("\nWelcome! I can help you manage your todos.")
        print("Examples of what you can say:")
        print("- 'Add a todo to buy groceries'")
        print("- 'Show me all my todos'")
        print("- 'Mark todo 1 as complete'")
        print("- 'Delete the shopping todo'")
        print("\nType 'quit' to exit.\n")
        
        await self.chat_loop()
    
    async def chat_loop(self):
        """Main chat interaction loop"""
        while True:
            try:
                user_input = input(f"{self.server_emoji} You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print(f"{self.server_emoji} Claude: Goodbye! Your todos are saved.")
                    break
                
                if not user_input:
                    continue
                
                # Process the user input with Claude
                response = await self.process_with_llm(user_input)
                print(f"{self.server_emoji} Claude: {response}")
                
            except KeyboardInterrupt:
                print(f"\n{self.server_emoji} Claude: Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def process_with_llm(self, user_input: str) -> str:
        """Process user input using Claude with multi-pass tool execution.
        
        This implements a multi-pass pattern where:
        1. Claude understands the user's request
        2. Claude can make multiple tool calls to gather information
        3. Claude analyzes tool results to make decisions
        4. Claude continues until it has a complete answer
        
        Args:
            user_input: Natural language message from the user
            
        Returns:
            Natural language response with complete results
        """
        # System prompt that enables multi-pass reasoning
        system_prompt = """You are a helpful assistant that manages todos using MCP tools.

You can use these tools to help users manage their todo lists. You may need to:
- Call multiple tools to complete a request
- Analyze results from one tool before calling another
- Ask clarifying questions if a request is ambiguous
- Provide thoughtful summaries of data

Approach each request step by step:
1. Understand what the user wants
2. Determine which tools you need to use
3. Execute tools and analyze their results
4. Continue until you have a complete answer
5. Provide a clear, helpful response to the user

Be conversational and helpful in your responses."""
        
        # Convert MCP tools to Anthropic tool format
        tools = self.convert_to_anthropic_tools()
        
        # Initialize conversation with user input
        messages = [{"role": "user", "content": user_input}]
        
        # Multi-pass loop - continue until Claude provides final answer
        max_iterations = 10  # Prevent infinite loops
        
        for iteration in range(max_iterations):
            try:
                # Debug logging for LLM API calls
                if self.debug:
                    print(f"🤖 LLM API Call #{iteration + 1}: claude-3-5-sonnet-20241022")
                    print(f"🤖 Messages count: {len(messages)}")
                    print(f"🤖 Tools available: {len(tools)}")
                
                # Get Claude's response with tools
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0,
                    system=system_prompt,
                    messages=messages,
                    tools=tools
                )
                
                # Debug logging for LLM responses
                if self.debug:
                    tool_calls = [block for block in response.content if block.type == "tool_use"]
                    text_blocks = [block for block in response.content if block.type == "text"]
                    print(f"🤖 LLM Response: {len(tool_calls)} tool calls, {len(text_blocks)} text blocks")
                    if text_blocks and not tool_calls:
                        print(f"🤖 Final Response: {text_blocks[0].text[:100]}{'...' if len(text_blocks[0].text) > 100 else ''}")
                
                # Add assistant message to conversation
                messages.append({"role": "assistant", "content": response.content})
                
                # Check if Claude made any tool calls
                tool_calls = [block for block in response.content if block.type == "tool_use"]
                
                if not tool_calls:
                    # No tool calls means Claude has final answer
                    # Extract text from response
                    text_blocks = [block for block in response.content if block.type == "text"]
                    if text_blocks:
                        return text_blocks[0].text
                    else:
                        return "I completed the task."
                
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call.name
                    tool_args = tool_call.input
                    tool_id = tool_call.id
                    
                    try:
                        # Debug logging for tool calls
                        if self.debug:
                            print(f"🔧 MCP Tool Call: {tool_name}({json.dumps(tool_args, indent=2)})")
                        
                        # Execute the MCP tool
                        result = await self.mcp_client.call_tool(tool_name, tool_args)
                        
                        # Parse the result
                        if hasattr(result, 'content'):
                            result_data = json.loads(result.content[0].text) if result.content else {}
                        else:
                            result_data = {}
                        
                        # Debug logging for tool results
                        if self.debug:
                            print(f"🔧 MCP Tool Result: {json.dumps(result_data, indent=2)}")
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": json.dumps(result_data)
                            }]
                        })
                        
                    except Exception as e:
                        # Add error to conversation so Claude can handle it
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            }]
                        })
                
            except anthropic.APIConnectionError as e:
                # Check for SSL certificate errors
                error_msg = str(e).lower()
                if "certificate" in error_msg or "ssl" in error_msg:
                    return (
                        "🔒 SSL Certificate Error: Unable to connect to Claude API.\n"
                        "\n"
                        "This could be caused by:\n"
                        "1. Missing Python certificates (common on macOS)\n"
                        "2. Corporate proxy/firewall (e.g., ZScaler) intercepting SSL\n"
                        "\n"
                        "Possible solutions:\n"
                        "• Run: pip install --upgrade certifi\n"
                        "• Check with your IT team about proxy certificates\n"
                        "• Set proxy environment variables if behind a corporate firewall"
                    )
                else:
                    return (
                        "🌐 Connection Error: Unable to reach Claude API.\n"
                        "Please check:\n"
                        "1. Your internet connection\n"
                        "2. Your ANTHROPIC_API_KEY is valid\n"
                        "3. If behind a corporate proxy, set HTTPS_PROXY in your .env.local file"
                    )
            except anthropic.AuthenticationError as e:
                return (
                    "🔑 Authentication Error: Invalid API key.\n"
                    "Please check that your ANTHROPIC_API_KEY in .env.local is correct."
                )
            except Exception as e:
                return f"Error: {str(e)}"
        
        return "I need more time to complete this request. Please try breaking it into smaller steps."
    
    def convert_to_anthropic_tools(self) -> list:
        """Convert MCP tools to Anthropic's tool format."""
        anthropic_tools = []
        
        for tool in self.mcp_client.available_tools:
            # Parse parameter schema from the tool object
            params = tool.inputSchema if hasattr(tool, 'inputSchema') else {}
            
            anthropic_tool = {
                "name": tool.name,
                "description": tool.description if hasattr(tool, 'description') else '',
                "input_schema": {
                    "type": "object",
                    "properties": params.get('properties', {}) if isinstance(params, dict) else {},
                    "required": params.get('required', []) if isinstance(params, dict) else []
                }
            }
            anthropic_tools.append(anthropic_tool)
        
        return anthropic_tools
    
    async def cleanup(self):
        """Clean up resources"""
        await self.mcp_client.close()


async def main():
    """Main entry point for the Todo MCP Client.
    
    This function demonstrates several important patterns:
    1. Environment-based configuration (API keys)
    2. Command-line argument handling for flexibility
    3. Proper async resource management with cleanup
    
    For mid-level developers: This structure shows how to build
    production-ready AI applications with proper configuration
    and error handling.
    """
    # Load environment variables from .env.local
    # This keeps sensitive data like API keys out of code
    env_path = Path(__file__).parent.parent / ".env.local"
    load_dotenv(env_path)
    
    # Parse command line arguments
    # This allows flexibility in deployment and testing
    parser = argparse.ArgumentParser(description="Todo Client - Natural language interface for todo management")
    parser.add_argument(
        "--server-path", 
        type=str, 
        help="Path to the todo server script (default: auto-selected based on --good/--bad flags)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging for MCP tool calls and LLM API calls"
    )
    
    # Add mutually exclusive group for server selection
    server_group = parser.add_mutually_exclusive_group()
    server_group.add_argument(
        "--good",
        action="store_true",
        help="Use the good_todo_server.py (well-documented, clear errors)"
    )
    server_group.add_argument(
        "--bad", 
        action="store_true",
        help="Use the bad_todo_server.py (poor descriptions, unclear errors)"
    )
    
    args = parser.parse_args()
    
    # Determine which server to use
    if args.server_path:
        server_path = args.server_path
    elif args.good:
        server_path = str(Path(__file__).parent / "good_todo_server.py")
        print("Using good_todo_server.py (well-documented with clear error messages)")
    elif args.bad:
        server_path = str(Path(__file__).parent / "bad_todo_server.py") 
        print("Using bad_todo_server.py (poor descriptions and unclear errors)")
    else:
        # Default to good server
        server_path = str(Path(__file__).parent / "good_todo_server.py")
        print("No server specified, defaulting to good_todo_server.py")
        print("Use --good or --bad to explicitly choose a server implementation")
    
    # Check for API key
    # Critical for AI applications - no key means no AI capabilities
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found")
        print("Please ensure your .env.local file contains: ANTHROPIC_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # Create and run the client with proper cleanup
    client = TodoChatClient(api_key, server_path=server_path, debug=args.debug)
    try:
        await client.start()
    finally:
        # Always clean up resources, even if errors occur
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
