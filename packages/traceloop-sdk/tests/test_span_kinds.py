"""Test span kinds and status functionality"""
import pytest
from opentelemetry.semconv_ai import SpanAttributes
from opentelemetry.trace.status import StatusCode
from traceloop.sdk.decorators import task, llm, mcp


def test_llm_span_kind(exporter):
    """Test that LLM span kind uses correct attribute key"""

    @llm(name="test_llm")
    def test_llm_function(prompt):
        return f"Response to: {prompt}"

    result = test_llm_function("Hello, how are you?")

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.name == "test_llm.llm"
    assert span.status.status_code == StatusCode.OK

    # Check if the correct attribute key was used for LLM
    # Should use GEN_AI_INPUT_MESSAGES if available,
    # otherwise fallback to TRACELOOP_ENTITY_INPUT
    has_gen_ai_input = hasattr(SpanAttributes, 'GEN_AI_INPUT_MESSAGES')
    expected_key = (
        SpanAttributes.GEN_AI_INPUT_MESSAGES if has_gen_ai_input
        else SpanAttributes.TRACELOOP_ENTITY_INPUT
    )

    assert expected_key in span.attributes
    assert result == "Response to: Hello, how are you?"


def test_mcp_span_kind(exporter):
    """Test that MCP span kind uses correct attribute key"""

    @mcp(name="test_mcp")
    def test_mcp_function(request):
        return f"MCP response to: {request}"

    result = test_mcp_function("mcp_request")

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.name == "test_mcp.mcp"
    assert span.status.status_code == StatusCode.OK

    # Check if the correct attribute key was used for MCP
    # Should use GEN_AI_MCP_REQUEST_ARGUMENT if available,
    # otherwise fallback to TRACELOOP_ENTITY_INPUT
    has_mcp_attr = hasattr(SpanAttributes, 'GEN_AI_MCP_REQUEST_ARGUMENT')
    expected_key = (
        SpanAttributes.GEN_AI_MCP_REQUEST_ARGUMENT if has_mcp_attr
        else SpanAttributes.TRACELOOP_ENTITY_INPUT
    )

    assert expected_key in span.attributes
    assert result == "MCP response to: mcp_request"


def test_default_span_kind(exporter):
    """Test that default (task) span kind uses default attribute key"""

    @task(name="test_task")
    def test_task_function(input_data):
        return f"Task result: {input_data}"

    result = test_task_function("some_input")

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.name == "test_task.task"
    assert span.status.status_code == StatusCode.OK

    # For existing span kinds (task, workflow, agent, tool),
    # should still use TRACELOOP_ENTITY_INPUT
    assert SpanAttributes.TRACELOOP_ENTITY_INPUT in span.attributes
    assert result == "Task result: some_input"


def test_span_status_on_success(exporter):
    """Test that spans are marked as OK on successful completion"""

    @task(name="success_task")
    def success_task():
        return "success"

    result = success_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.status.status_code == StatusCode.OK
    assert result == "success"


def test_span_status_on_error(exporter):
    """Test that spans are marked as ERROR on exception"""

    @task(name="error_task")
    def error_task():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        error_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.status.status_code == StatusCode.ERROR
    assert "Test error" in span.status.description


@pytest.mark.asyncio
async def test_async_span_status_on_success(exporter):
    """Test that async spans are marked as OK on successful completion"""

    @task(name="async_success_task")
    async def async_success_task():
        return "async_success"

    result = await async_success_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.status.status_code == StatusCode.OK
    assert result == "async_success"


@pytest.mark.asyncio
async def test_async_span_status_on_error(exporter):
    """Test that async spans are marked as ERROR on exception"""

    @task(name="async_error_task")
    async def async_error_task():
        raise ValueError("Async test error")

    with pytest.raises(ValueError, match="Async test error"):
        await async_error_task()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.status.status_code == StatusCode.ERROR
    assert "Async test error" in span.status.description
