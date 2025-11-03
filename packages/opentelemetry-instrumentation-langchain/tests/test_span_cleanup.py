"""Tests for span cleanup functionality."""
import time
from uuid import uuid4

import pytest
from opentelemetry.instrumentation.langchain.callback_handler import (
    TraceloopCallbackHandler,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.semconv_ai import Meters


@pytest.fixture
def tracer():
    """Create a tracer for testing."""
    provider = TracerProvider()
    return provider.get_tracer(__name__)


@pytest.fixture
def meter():
    """Create a meter for testing."""
    provider = MeterProvider()
    return provider.get_meter(__name__)


@pytest.fixture
def callback_handler(tracer, meter):
    """Create a callback handler with a short cleanup threshold for testing."""
    duration_histogram = meter.create_histogram(
        name=Meters.LLM_OPERATION_DURATION,
        unit="s",
        description="GenAI operation duration",
    )
    token_histogram = meter.create_histogram(
        name=Meters.LLM_TOKEN_USAGE,
        unit="token",
        description="Token usage",
    )
    # Use a 2-second threshold for testing
    return TraceloopCallbackHandler(
        tracer, duration_histogram, token_histogram,
        span_cleanup_threshold_seconds=2
    )


def test_cleanup_stale_spans(callback_handler):
    """Test that stale spans are cleaned up after threshold."""
    # Create some spans
    run_id_1 = uuid4()

    # Create first span
    callback_handler.on_chain_start(
        serialized={"name": "test_chain_1"},
        inputs={"test": "input1"},
        run_id=run_id_1,
        parent_run_id=None,
    )

    # Verify span was created
    assert run_id_1 in callback_handler.spans
    assert len(callback_handler.spans) == 1

    # Wait for span to become stale (threshold is 2 seconds)
    time.sleep(2.5)

    # Create a second span, which should trigger cleanup after CLEANUP_CHECK_INTERVAL
    # We need to create enough spans to trigger the cleanup check
    for i in range(callback_handler.CLEANUP_CHECK_INTERVAL):
        temp_run_id = uuid4()
        callback_handler.on_chain_start(
            serialized={"name": f"test_chain_{i}"},
            inputs={"test": f"input{i}"},
            run_id=temp_run_id,
            parent_run_id=None,
        )
        # Clean up these test spans immediately to avoid clutter
        if temp_run_id in callback_handler.spans:
            callback_handler.on_chain_end(
                outputs={"test": "output"},
                run_id=temp_run_id,
            )

    # The first stale span should have been cleaned up
    assert run_id_1 not in callback_handler.spans


def test_cleanup_preserves_active_spans(callback_handler):
    """Test that active (non-stale) spans are not cleaned up."""
    run_id = uuid4()

    # Create a span
    callback_handler.on_chain_start(
        serialized={"name": "test_chain"},
        inputs={"test": "input"},
        run_id=run_id,
        parent_run_id=None,
    )

    # Verify span exists
    assert run_id in callback_handler.spans

    # Trigger cleanup immediately (span is fresh, should not be removed)
    callback_handler._cleanup_stale_spans()

    # Span should still exist
    assert run_id in callback_handler.spans

    # Clean up
    callback_handler.on_chain_end(
        outputs={"test": "output"},
        run_id=run_id,
    )

    # Now it should be gone through normal cleanup
    assert run_id not in callback_handler.spans


def test_cleanup_with_no_spans(callback_handler):
    """Test that cleanup works safely when there are no spans."""
    # Should not raise any errors
    callback_handler._cleanup_stale_spans()
    assert len(callback_handler.spans) == 0


def test_default_cleanup_threshold():
    """Test that default cleanup threshold is set correctly."""
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    meter_provider = MeterProvider()
    meter = meter_provider.get_meter(__name__)

    duration_histogram = meter.create_histogram(
        name=Meters.LLM_OPERATION_DURATION,
        unit="s",
        description="GenAI operation duration",
    )
    token_histogram = meter.create_histogram(
        name=Meters.LLM_TOKEN_USAGE,
        unit="token",
        description="Token usage",
    )

    handler = TraceloopCallbackHandler(tracer, duration_histogram, token_histogram)

    # Verify default threshold is 1 hour
    assert handler.span_cleanup_threshold == 3600


def test_custom_cleanup_threshold():
    """Test that custom cleanup threshold can be set."""
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    meter_provider = MeterProvider()
    meter = meter_provider.get_meter(__name__)

    duration_histogram = meter.create_histogram(
        name=Meters.LLM_OPERATION_DURATION,
        unit="s",
        description="GenAI operation duration",
    )
    token_histogram = meter.create_histogram(
        name=Meters.LLM_TOKEN_USAGE,
        unit="token",
        description="Token usage",
    )

    custom_threshold = 1800  # 30 minutes
    handler = TraceloopCallbackHandler(
        tracer, duration_histogram, token_histogram,
        span_cleanup_threshold_seconds=custom_threshold
    )

    # Verify custom threshold is set
    assert handler.span_cleanup_threshold == custom_threshold


def test_periodic_cleanup_trigger(callback_handler):
    """Test that cleanup is triggered periodically during span creation."""
    # Create a stale span
    stale_run_id = uuid4()
    callback_handler.on_chain_start(
        serialized={"name": "stale_chain"},
        inputs={"test": "input"},
        run_id=stale_run_id,
        parent_run_id=None,
    )

    # Wait for it to become stale
    time.sleep(2.5)

    # Create new spans until cleanup is triggered
    initial_count = callback_handler._span_creation_count
    interval = callback_handler.CLEANUP_CHECK_INTERVAL

    # Create spans just before the cleanup interval
    for i in range(interval - (initial_count % interval) - 1):
        temp_run_id = uuid4()
        callback_handler.on_chain_start(
            serialized={"name": f"chain_{i}"},
            inputs={"test": f"input{i}"},
            run_id=temp_run_id,
            parent_run_id=None,
        )
        # End them immediately
        if temp_run_id in callback_handler.spans:
            callback_handler.on_chain_end(
                outputs={"test": "output"},
                run_id=temp_run_id,
            )

    # Stale span should still exist (cleanup not triggered yet)
    assert stale_run_id in callback_handler.spans

    # Create one more span to trigger cleanup
    trigger_run_id = uuid4()
    callback_handler.on_chain_start(
        serialized={"name": "trigger_chain"},
        inputs={"test": "input"},
        run_id=trigger_run_id,
        parent_run_id=None,
    )

    # Now the stale span should be cleaned up
    assert stale_run_id not in callback_handler.spans

    # Clean up the trigger span
    if trigger_run_id in callback_handler.spans:
        callback_handler.on_chain_end(
            outputs={"test": "output"},
            run_id=trigger_run_id,
        )
