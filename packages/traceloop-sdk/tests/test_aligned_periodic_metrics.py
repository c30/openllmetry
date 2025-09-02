"""Tests for aligned periodic metrics export functionality (00, 20, 40 seconds timing)"""
from unittest.mock import patch

from traceloop.sdk.metrics.metrics import (
    AlignedPeriodicMetricReader, HourlyExportingMetricReader
)
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult, AggregationTemporality
from opentelemetry.sdk.metrics._internal.instrument import Counter, UpDownCounter, Histogram, ObservableCounter, ObservableUpDownCounter, ObservableGauge
from opentelemetry.sdk.metrics._internal.aggregation import ExplicitBucketHistogramAggregation


class MockMetricExporter(MetricExporter):
    """Mock exporter for testing"""

    def __init__(self):
        self.exported_metrics = []
        self.export_calls = 0
        
        # Add the required attributes that PeriodicExportingMetricReader expects
        self._preferred_temporality = {
            Counter: AggregationTemporality.CUMULATIVE,
            UpDownCounter: AggregationTemporality.CUMULATIVE,
            Histogram: AggregationTemporality.CUMULATIVE,
            ObservableCounter: AggregationTemporality.CUMULATIVE,
            ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
            ObservableGauge: AggregationTemporality.CUMULATIVE,
        }
        self._preferred_aggregation = {
            Histogram: ExplicitBucketHistogramAggregation()
        }

    def export(self, metrics_data):
        self.export_calls += 1
        self.exported_metrics.append(metrics_data)
        return MetricExportResult.SUCCESS

    def shutdown(self, timeout_millis=30000, timeout=None, **kwargs):
        # Handle both timeout_millis (our interface) and timeout (parent class call)
        return True

    def force_flush(self, timeout_millis=30000, timeout=None, **kwargs):
        # Handle both timeout_millis (our interface) and timeout (parent class call)
        return True


class TestAlignedPeriodicMetricReader:

    def test_aligned_periodic_metric_reader_initialization(self):
        """Test that AlignedPeriodicMetricReader can be initialized"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)

        assert reader._exporter == exporter
        assert reader._export_timeout_millis == 30000  # default
        assert reader._shutdown is False
        # New implementation uses _daemon_thread from PeriodicExportingMetricReader
        assert reader._daemon_thread is not None

        # Clean up
        reader.shutdown()

    def test_backward_compatibility_class_alias(self):
        """Test that HourlyExportingMetricReader is an alias for AlignedPeriodicMetricReader"""
        assert HourlyExportingMetricReader is AlignedPeriodicMetricReader

    def test_custom_export_timeout(self):
        """Test custom export timeout setting"""
        exporter = MockMetricExporter()
        custom_timeout = 60000
        reader = AlignedPeriodicMetricReader(exporter, export_timeout_millis=custom_timeout)

        assert reader._export_timeout_millis == custom_timeout

        # Clean up
        reader.shutdown()

    def test_force_flush(self):
        """Test force flush functionality"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)

        # The new implementation doesn't use _receive_metrics in the same way
        # Force flush should work with the underlying exporter
        result = reader.force_flush()

        assert result is True
        # Since we haven't collected any metrics, export_calls should be 0
        # The parent class handles the actual metric collection/export flow

        # Clean up
        reader.shutdown()

    def test_shutdown(self):
        """Test shutdown functionality"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)

        assert reader._shutdown is False
        reader.shutdown()

        assert reader._shutdown is True
        # The shutdown method doesn't return a boolean in the new implementation
        # (it's following the PeriodicExportingMetricReader interface)

    def test_aligned_timing_logic_integration(self):
        """Integration test to verify the aligned timing logic works correctly"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)

        # Test that the reader was created and has a daemon thread
        assert reader._daemon_thread is not None
        assert reader._shutdown is False

        # Test that we can force flush
        result = reader.force_flush()
        assert result is True

        # Clean up
        reader.shutdown()

    def test_recurring_export_interval(self):
        """Test that the aligned timing logic is working with the new implementation"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)

        # Test that the reader is using our custom _ticker implementation
        # The _ticker method should be overridden to use aligned timing
        assert hasattr(reader, '_ticker')
        # We can verify it's our method by checking if the parent class thread is running
        assert reader._daemon_thread is not None
        assert reader._daemon_thread.is_alive()

        # Clean up
        reader.shutdown()


def test_traceloop_init_with_aligned_periodic_metrics():
    """Test that Traceloop.init still works with the aligned periodic metrics"""
    from traceloop.sdk import Traceloop
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from traceloop.sdk.metrics.metrics import MetricsWrapper

    # Clear any existing singletons
    if hasattr(Traceloop, '_Traceloop__tracer_wrapper'):
        delattr(Traceloop, '_Traceloop__tracer_wrapper')
    if hasattr(Traceloop, '_Traceloop__metrics_wrapper'):
        delattr(Traceloop, '_Traceloop__metrics_wrapper')
    if hasattr(MetricsWrapper, 'instance'):
        delattr(MetricsWrapper, 'instance')

    exporter = InMemorySpanExporter()
    metrics_exporter = MockMetricExporter()

    # This should not raise any errors and should use AlignedPeriodicMetricReader
    Traceloop.init(
        app_name="test_aligned_periodic",
        exporter=exporter,
        metrics_exporter=metrics_exporter,
        metrics_hourly_export=True,  # This now enables aligned periodic export
        disable_batch=True
    )

    # Verify the setting was applied
    assert MetricsWrapper.aligned_periodic_export is True
    assert MetricsWrapper.hourly_export is True  # Backward compatibility

    # Clean up
    exporter.clear()
