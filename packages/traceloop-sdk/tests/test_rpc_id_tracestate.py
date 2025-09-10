"""Test rpc_id extraction from tracestate."""

from opentelemetry.trace import TraceState, SpanContext, TraceFlags
from traceloop.sdk.tracing.tracing import default_span_processor_on_start


def test_rpc_id_extraction_from_tracestate(exporter):
    """Test that rpc_id is extracted from tracestate and set as span attribute."""
    # Create a TraceState with rpc_id
    trace_state = TraceState([("rpc_id", "test-rpc-id-123"), ("other_key", "other_value")])

    # Create a span context with the tracestate
    span_context = SpanContext(
        trace_id=0x12345678901234567890123456789012,
        span_id=0x1234567890123456,
        is_remote=False,
        trace_flags=TraceFlags(0x01),
        trace_state=trace_state
    )

    # Mock span with the custom span context
    class MockSpan:
        def __init__(self, span_context):
            self._span_context = span_context
            self.attributes = {}

        def get_span_context(self):
            return self._span_context

        def set_attribute(self, key, value):
            self.attributes[key] = value

    mock_span = MockSpan(span_context)

    # Call the default span processor
    default_span_processor_on_start(mock_span)

    # Verify that rpc_id was extracted and set as attribute
    assert "rpc_id" in mock_span.attributes
    assert mock_span.attributes["rpc_id"] == "test-rpc-id-123"


def test_no_rpc_id_in_tracestate(exporter):
    """Test that no rpc_id attribute is set when rpc_id is not in tracestate."""
    # Create a TraceState without rpc_id
    trace_state = TraceState([("other_key", "other_value")])

    # Create a span context with the tracestate
    span_context = SpanContext(
        trace_id=0x12345678901234567890123456789012,
        span_id=0x1234567890123456,
        is_remote=False,
        trace_flags=TraceFlags(0x01),
        trace_state=trace_state
    )

    # Mock span with the custom span context
    class MockSpan:
        def __init__(self, span_context):
            self._span_context = span_context
            self.attributes = {}

        def get_span_context(self):
            return self._span_context

        def set_attribute(self, key, value):
            self.attributes[key] = value

    mock_span = MockSpan(span_context)

    # Call the default span processor
    default_span_processor_on_start(mock_span)

    # Verify that rpc_id was not set as attribute
    assert "rpc_id" not in mock_span.attributes


def test_empty_tracestate(exporter):
    """Test that no rpc_id attribute is set when tracestate is empty."""
    # Create a span context with empty tracestate
    span_context = SpanContext(
        trace_id=0x12345678901234567890123456789012,
        span_id=0x1234567890123456,
        is_remote=False,
        trace_flags=TraceFlags(0x01),
        trace_state=None  # No tracestate
    )

    # Mock span with the custom span context
    class MockSpan:
        def __init__(self, span_context):
            self._span_context = span_context
            self.attributes = {}

        def get_span_context(self):
            return self._span_context

        def set_attribute(self, key, value):
            self.attributes[key] = value

    mock_span = MockSpan(span_context)

    # Call the default span processor
    default_span_processor_on_start(mock_span)

    # Verify that rpc_id was not set as attribute
    assert "rpc_id" not in mock_span.attributes


def test_rpc_id_with_existing_attributes(exporter):
    """Test that rpc_id is set alongside other existing attributes."""
    from opentelemetry.context import attach, set_value

    # Create a TraceState with rpc_id
    trace_state = TraceState([("rpc_id", "custom-rpc-123")])

    # Create a span context with the tracestate
    span_context = SpanContext(
        trace_id=0x12345678901234567890123456789012,
        span_id=0x1234567890123456,
        is_remote=False,
        trace_flags=TraceFlags(0x01),
        trace_state=trace_state
    )

    # Mock span with the custom span context
    class MockSpan:
        def __init__(self, span_context):
            self._span_context = span_context
            self.attributes = {}

        def get_span_context(self):
            return self._span_context

        def set_attribute(self, key, value):
            self.attributes[key] = value

    mock_span = MockSpan(span_context)

    # Set a workflow name in context to test that other attributes still work
    attach(set_value("workflow_name", "test_workflow"))

    # Call the default span processor
    default_span_processor_on_start(mock_span)

    # Verify that both rpc_id and workflow_name were set
    assert "rpc_id" in mock_span.attributes
    assert mock_span.attributes["rpc_id"] == "custom-rpc-123"
    # The workflow name should also be set (this tests our existing functionality still works)
    from opentelemetry.semconv_ai import SpanAttributes
    assert SpanAttributes.TRACELOOP_WORKFLOW_NAME in mock_span.attributes
    assert mock_span.attributes[SpanAttributes.TRACELOOP_WORKFLOW_NAME] == "test_workflow"
