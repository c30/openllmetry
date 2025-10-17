# Sample Applications for OpenLLMetry

This directory contains sample applications demonstrating various integrations with OpenLLMetry for LLM observability.

## Available Examples

### LangChain MCP Integration Demo

**Files:**
- `sample_app/langchain_mcp_example.py` - Comprehensive demo with multiple modes
- `sample_app/langchain_mcp_simple_example.py` - Minimal example for learning

A comprehensive demo showing how to integrate LangChain with Model Context Protocol (MCP) servers using OpenTelemetry instrumentation.

**Features:**
- LangChain agent integration with MCP tools
- Automatic tracing via `opentelemetry-instrumentation-mcp`
- Support for both demo and interactive modes
- End-to-end observability of MCP tool calls

**Usage:**

Full demo:
```bash
# Demo mode with predefined queries
poetry run python sample_app/langchain_mcp_example.py

# Interactive mode
poetry run python sample_app/langchain_mcp_example.py --interactive
```

Simple example:
```bash
# Run a single query
poetry run python sample_app/langchain_mcp_simple_example.py "List files in this directory"
```

**Requirements:**
- `OPENAI_API_KEY` environment variable
- Node.js/npx (for MCP servers)

See [langchain_mcp_example_README.md](sample_app/langchain_mcp_example_README.md) for detailed documentation.

### Other Examples

Additional sample applications demonstrating various LLM frameworks and integrations can be found in the `sample_app/` directory:
- Anthropic examples
- OpenAI examples
- LangChain applications
- LlamaIndex applications
- And more...

## Installation

```bash
poetry install
```

## Running Examples

All examples can be run using Poetry:

```bash
poetry run python sample_app/<example_name>.py
```

Make sure to set up required API keys as environment variables before running examples.
