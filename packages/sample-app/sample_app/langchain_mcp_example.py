"""
LangChain MCP Integration Demo with OpenTelemetry Instrumentation

This demo shows how to use langchain-mcp with OpenTelemetry instrumentation
to trace and monitor MCP (Model Context Protocol) tool calls.

The demo uses:
- langchain-mcp: Integration between LangChain and MCP servers
- opentelemetry-instrumentation-mcp: Automatic tracing of MCP operations
- OpenAI as the LLM backend
- MCP filesystem server for tool demonstrations

To run this demo:
1. Install dependencies: poetry install
2. Set OPENAI_API_KEY environment variable
3. Run: python sample_app/langchain_mcp_example.py
"""

import asyncio
import os
import sys
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_mcp import MCPToolkit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

# Load environment variables
load_dotenv()

# Initialize Traceloop for OpenTelemetry tracing
# Traceloop SDK auto-detects and instruments MCP, LangChain, and OpenAI operations
# when their instrumentation packages are installed (opentelemetry-instrumentation-*)
Traceloop.init(app_name="langchain_mcp_demo")


class LangChainMCPDemo:
    """Demo class showing LangChain integration with MCP using OpenTelemetry tracing."""

    def __init__(self):
        """Initialize the demo with LLM and session management."""
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.exit_stack = AsyncExitStack()
        self.session = None
        self.agent_executor = None

    async def connect_to_mcp_server(self, server_command: str, server_args: list = None):
        """
        Connect to an MCP server using stdio transport.

        Args:
            server_command: Command to start the MCP server (e.g., "npx")
            server_args: Arguments for the server command
        """
        print(f"\n🔌 Connecting to MCP server: {server_command} {' '.join(server_args or [])}")

        # Set up server parameters
        server_params = StdioServerParameters(
            command=server_command,
            args=server_args or [],
            env=os.environ.copy()
        )

        # Connect to the MCP server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport

        # Create client session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        # Initialize the session
        await self.session.initialize()
        print("✅ Successfully connected to MCP server")

    async def setup_langchain_agent(self):
        """Set up LangChain agent with MCP tools."""
        if not self.session:
            raise RuntimeError("MCP session not initialized. Call connect_to_mcp_server first.")

        print("\n🔧 Setting up LangChain agent with MCP tools...")

        # Create MCPToolkit and initialize it
        toolkit = MCPToolkit(session=self.session)
        await toolkit.initialize()

        # Get tools from the MCP server
        tools = toolkit.get_tools()
        print(f"📦 Loaded {len(tools)} tools from MCP server:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        # Create agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant with access to MCP tools.
Use the available tools to help answer user questions.
Be concise and clear in your responses."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=10,
        )
        print("✅ LangChain agent configured successfully")

    @workflow(name="process_query_with_mcp")
    async def process_query(self, query: str) -> str:
        """
        Process a user query using the LangChain agent with MCP tools.
        This method is instrumented with @workflow decorator for better tracing.

        Args:
            query: User's question or request

        Returns:
            Agent's response as a string
        """
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call setup_langchain_agent first.")

        print(f"\n💬 Processing query: {query}")
        print("=" * 80)

        # Invoke the agent - this will be traced by OpenTelemetry
        result = await self.agent_executor.ainvoke({"input": query})

        print("=" * 80)
        return result["output"]

    async def run_demo_queries(self):
        """Run a series of demo queries to showcase MCP tool integration."""
        demo_queries = [
            "List all files in the current directory",
            "What is the content of README.md file?",
            "Tell me about the LICENSE file in this directory",
        ]

        print("\n" + "=" * 80)
        print("🚀 Starting LangChain MCP Demo")
        print("=" * 80)

        for i, query in enumerate(demo_queries, 1):
            print(f"\n{'=' * 80}")
            print(f"Demo Query #{i}")
            print(f"{'=' * 80}")

            try:
                response = await self.process_query(query)
                print(f"\n✨ Response: {response}\n")
            except Exception as e:
                print(f"\n❌ Error processing query: {str(e)}\n")
                import traceback
                traceback.print_exc()

    async def interactive_mode(self):
        """Run in interactive mode where user can enter queries."""
        print("\n" + "=" * 80)
        print("🤖 Interactive Mode - LangChain MCP Demo")
        print("=" * 80)
        print("Enter your queries (type 'quit' or 'exit' to stop)")
        print("=" * 80)

        while True:
            try:
                # Get user input
                query = input("\n🔮 Your query: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                if not query:
                    continue

                # Process the query
                response = await self.process_query(query)
                print(f"\n✨ Response: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 EOF received. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources and close connections."""
        print("\n🧹 Cleaning up resources...")
        await self.exit_stack.aclose()
        print("✅ Cleanup complete")


async def main():
    """Main entry point for the demo."""
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        return

    demo = LangChainMCPDemo()

    try:
        # Connect to MCP filesystem server
        # This uses the official MCP filesystem server from npm
        # It allows reading files from the current directory
        await demo.connect_to_mcp_server(
            server_command="npx",
            server_args=[
                "-y",  # Auto-confirm package installation
                "@modelcontextprotocol/server-filesystem",
                os.getcwd()  # Allow access to current working directory
            ]
        )

        # Set up the LangChain agent with MCP tools
        await demo.setup_langchain_agent()

        # Determine mode based on command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
            await demo.interactive_mode()
        else:
            # Run demo queries
            await demo.run_demo_queries()

        print("\n" + "=" * 80)
        print("✅ Demo completed successfully!")
        print("=" * 80)
        print("\n📊 Traces have been sent to your configured OpenTelemetry backend.")
        print("Check your tracing dashboard to see:")
        print("  - MCP server connections and tool calls")
        print("  - LangChain agent execution flow")
        print("  - OpenAI API calls")
        print("  - Complete end-to-end request traces")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   LangChain MCP with OpenTelemetry Demo                      ║
║                                                                              ║
║  This demo showcases:                                                        ║
║  • LangChain integration with Model Context Protocol (MCP)                  ║
║  • OpenTelemetry instrumentation for comprehensive tracing                  ║
║  • MCP tool usage with LangChain agents                                     ║
║  • Automatic trace and metric collection                                    ║
║                                                                              ║
║  Requirements:                                                               ║
║  • OPENAI_API_KEY environment variable                                      ║
║  • Node.js/npx installed (for MCP filesystem server)                        ║
║                                                                              ║
║  Usage:                                                                      ║
║  • Demo mode: python sample_app/langchain_mcp_example.py                    ║
║  • Interactive: python sample_app/langchain_mcp_example.py --interactive    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
