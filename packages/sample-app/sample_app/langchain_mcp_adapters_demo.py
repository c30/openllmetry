"""
Demo of langchain-mcp-adapters with OpenTelemetry instrumentation.

This example shows how to use LangChain with MCP (Model Context Protocol) servers
using the langchain-mcp-adapters package, with full OpenTelemetry tracing support.

The demo connects to an MCP server and uses LangChain's agent framework to
interact with it, while automatically capturing telemetry data through both
langchain and MCP instrumentation.

Requirements:
- OpenAI API key (set OPENAI_API_KEY environment variable)
- Node.js and npx (for running MCP server)

Usage:
    python langchain_mcp_adapters_demo.py
"""

import asyncio
import os
from langchain_mcp_adapters import MCPToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from traceloop.sdk import Traceloop

# Load environment variables
load_dotenv()

# Initialize Traceloop for OpenTelemetry instrumentation
# This automatically instruments both LangChain and MCP
Traceloop.init(app_name="langchain_mcp_adapters_demo")


async def run_agent_query(agent_executor, query):
    """Execute a single query with the agent."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        result = await agent_executor.ainvoke({"input": query})
        print(f"\nResult: {result['output']}")
        return result
    except Exception as e:
        print(f"\nError processing query: {str(e)}")
        return None


async def main():
    """
    Main function demonstrating langchain-mcp-adapters usage with OpenTelemetry.
    
    This demo:
    1. Connects to an MCP server (Google Maps in this example)
    2. Creates a LangChain toolkit from the MCP server tools
    3. Sets up a LangChain agent with the MCP tools
    4. Executes queries using the agent
    
    All interactions are automatically traced with OpenTelemetry via:
    - opentelemetry-instrumentation-langchain (for LangChain calls)
    - opentelemetry-instrumentation-mcp (for MCP protocol calls)
    """
    print("Initializing langchain-mcp-adapters demo...")
    print("Connecting to MCP server...")
    
    # Initialize the MCP toolkit with a server
    # This connects to the Google Maps MCP server as an example
    # The server_params define how to start the MCP server
    toolkit = MCPToolkit(
        server_package_name="@modelcontextprotocol/server-google-maps",
        server_params={
            "command": "npx",
            "args": ["@modelcontextprotocol/server-google-maps"],
            "env": dict(os.environ),
        }
    )
    
    try:
        # Initialize the toolkit (connects to the MCP server)
        await toolkit.initialize()
        
        # Get the tools from the MCP server
        tools = toolkit.get_tools()
        print(f"\nAvailable tools from MCP server: {[tool.name for tool in tools]}")
        
        # Set up the LangChain agent with OpenAI
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Create a prompt template for the agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to various tools. "
                       "Use them to answer user questions accurately."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create the agent with the MCP tools
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Example queries to demonstrate the integration
        queries = [
            "What's the distance between New York and Los Angeles?",
            "Find directions from San Francisco to Seattle",
        ]
        
        for query in queries:
            await run_agent_query(agent_executor, query)
        
    finally:
        # Clean up resources
        print("\nCleaning up...")
        await toolkit.cleanup()
        print("Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
