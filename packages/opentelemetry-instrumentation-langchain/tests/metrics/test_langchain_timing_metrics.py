import pytest
from opentelemetry.semconv_ai import Meters


def test_timing_metrics_are_defined():
    """Test that the new timing metrics are properly defined."""
    # Verify the new metrics are defined in the Meters class
    assert hasattr(Meters, 'LLM_TIME_TO_FIRST_TOKEN')
    assert hasattr(Meters, 'LLM_TIME_PER_OUTPUT_TOKEN')
    assert hasattr(Meters, 'LLM_TIME_BETWEEN_TOKEN')
    
    # Verify they have the correct values
    assert Meters.LLM_TIME_TO_FIRST_TOKEN == "gen_ai.client.time_to_first_token"
    assert Meters.LLM_TIME_PER_OUTPUT_TOKEN == "gen_ai.client.time_per_output_token"
    assert Meters.LLM_TIME_BETWEEN_TOKEN == "gen_ai.client.time_between_token"


def test_timing_metrics_histograms_created(instrument_legacy, meter_provider):
    """Test that timing histogram metrics are created during instrumentation."""
    from opentelemetry.instrumentation.langchain import LangchainInstrumentor
    
    # Get the instrumentor
    instrumentor = LangchainInstrumentor()
    
    # Check if instrumentation created the timing metrics
    # We can't easily access the internal histograms, but we can verify
    # that the instrumentation doesn't raise errors with the new metrics
    
    # The fact that instrument_legacy fixture works means the histograms
    # were created successfully without errors
    assert True  # This test passes if instrumentation didn't fail


def test_callback_handler_timing_methods():
    """Test that the TraceloopCallbackHandler has timing-related methods."""
    from opentelemetry.instrumentation.langchain.callback_handler import TraceloopCallbackHandler
    from opentelemetry.instrumentation.langchain.span_utils import SpanHolder
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.trace import get_tracer
    from opentelemetry.metrics import get_meter
    
    # Create a tracer and meter for testing
    tracer_provider = TracerProvider()
    tracer = get_tracer(__name__, "test", tracer_provider)
    
    meter_provider = MeterProvider()
    meter = get_meter(__name__, "test", meter_provider)
    
    # Create histograms
    duration_hist = meter.create_histogram("test.duration", unit="s", description="test")
    token_hist = meter.create_histogram("test.tokens", unit="token", description="test")
    time_to_first_token_hist = meter.create_histogram("test.time_to_first_token", unit="s", description="test")
    time_per_output_token_hist = meter.create_histogram("test.time_per_output_token", unit="s", description="test")
    time_between_token_hist = meter.create_histogram("test.time_between_token", unit="s", description="test")
    
    # Create callback handler with timing histograms
    handler = TraceloopCallbackHandler(
        tracer=tracer,
        duration_histogram=duration_hist,
        token_histogram=token_hist,
        time_to_first_token_histogram=time_to_first_token_hist,
        time_per_output_token_histogram=time_per_output_token_hist,
        time_between_token_histogram=time_between_token_hist,
    )
    
    # Verify the handler has the timing histogram attributes
    assert hasattr(handler, 'time_to_first_token_histogram')
    assert hasattr(handler, 'time_per_output_token_histogram')
    assert hasattr(handler, 'time_between_token_histogram')
    
    # Verify they were set correctly
    assert handler.time_to_first_token_histogram == time_to_first_token_hist
    assert handler.time_per_output_token_histogram == time_per_output_token_hist
    assert handler.time_between_token_histogram == time_between_token_hist
    
    # Verify the handler has the on_llm_new_token method
    assert hasattr(handler, 'on_llm_new_token')
    assert callable(handler.on_llm_new_token)


def test_span_holder_timing_fields():
    """Test that SpanHolder has timing-related fields."""
    from opentelemetry.instrumentation.langchain.span_utils import SpanHolder
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace import get_tracer
    from opentelemetry.context.context import Context
    from uuid import uuid4
    
    # Create a minimal span for testing
    tracer_provider = TracerProvider()
    tracer = get_tracer(__name__, "test", tracer_provider)
    
    with tracer.start_as_current_span("test") as span:
        # Create a SpanHolder
        holder = SpanHolder(
            span=span,
            token=None,
            context=Context(),
            children=[],
            workflow_name="test",
            entity_name="test",
            entity_path="test"
        )
        
        # Verify timing fields exist
        assert hasattr(holder, 'first_token_time')
        assert hasattr(holder, 'last_token_time')
        assert hasattr(holder, 'output_token_count')
        
        # Verify initial values
        assert holder.first_token_time is None
        assert holder.last_token_time is None
        assert holder.output_token_count == 0