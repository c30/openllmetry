"""
Simple LangChain MCP Example with OpenTelemetry

A minimal example showing the core concepts of using langchain-mcp
with OpenTelemetry instrumentation.

Usage:
    export OPENAI_API_KEY='your-key'
    python sample_app/langchain_mcp_simple_example.py "Your query here"
"""

import asyncio
import os
import sys
from contextlib import AsyncExitStack

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_mcp import MCPToolkit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from traceloop.sdk import Traceloop

# Initialize OpenTelemetry instrumentation
# Traceloop SDK automatically detects and instruments MCP, LangChain, and OpenAI
# when the instrumentation packages are installed (opentelemetry-instrumentation-mcp, etc.)
Traceloop.init(app_name="langchain_mcp_simple")


async def run_query(query: str):
    """Run a query using LangChain agent with MCP tools."""
    exit_stack = AsyncExitStack()

    try:
        # 1. Connect to MCP filesystem server
        print("🔌 Connecting to MCP server...")
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()]
        )

        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport

        session = await exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()
        print("✅ Connected")

        # 2. Create MCPToolkit and get tools
        print("🔧 Loading MCP tools...")
        toolkit = MCPToolkit(session=session)
        await toolkit.initialize()
        tools = toolkit.get_tools()
        print(f"✅ Loaded {len(tools)} tools")

        # 3. Create LangChain agent
        print("🤖 Creating LangChain agent...")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to MCP tools. "
             "Use them to answer questions."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        print("✅ Agent ready")

        # 4. Run the query - this will be traced by OpenTelemetry
        print(f"\n💬 Query: {query}\n")
        print("=" * 80)
        result = await agent_executor.ainvoke({"input": query})
        print("=" * 80)

        print(f"\n✨ Answer: {result['output']}\n")

    finally:
        await exit_stack.aclose()


def main():
    """Main entry point."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable required")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python langchain_mcp_simple_example.py 'Your query here'")
        print("\nExample queries:")
        print("  'List files in this directory'")
        print("  'What is in the README file?'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    asyncio.run(run_query(query))

    print("\n📊 Traces exported to your OpenTelemetry backend")


if __name__ == "__main__":
    main()
