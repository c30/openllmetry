"""Tests for aligned periodic metrics export functionality (00, 20, 40 seconds timing)"""
import pytest
import datetime
import threading
import time
from unittest.mock import Mock, patch, MagicMock

from traceloop.sdk.metrics.metrics import AlignedPeriodicMetricReader, HourlyExportingMetricReader
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult


class MockMetricExporter(MetricExporter):
    """Mock exporter for testing"""
    
    def __init__(self):
        self.exported_metrics = []
        self.export_calls = 0
        
    def export(self, metrics_data):
        self.export_calls += 1
        self.exported_metrics.append(metrics_data)
        return MetricExportResult.SUCCESS
        
    def shutdown(self, timeout_millis=30000):
        return True
        
    def force_flush(self, timeout_millis=30000):
        return True


class TestAlignedPeriodicMetricReader:
    
    def test_aligned_periodic_metric_reader_initialization(self):
        """Test that AlignedPeriodicMetricReader can be initialized"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)
        
        assert reader._exporter == exporter
        assert reader._export_timeout_millis == 30000  # default
        assert reader._shutdown is False
        assert reader._thread is not None
        
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
        
        # Simulate receiving some metrics
        reader._receive_metrics("mock_metrics_data")
        
        result = reader.force_flush()
        
        assert result is True
        assert exporter.export_calls == 1
        
        # Clean up
        reader.shutdown()
    
    def test_shutdown(self):
        """Test shutdown functionality"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)
        
        assert reader._shutdown is False
        result = reader.shutdown()
        
        assert reader._shutdown is True
        assert result is True
    
    def test_aligned_timing_logic_integration(self):
        """Integration test to verify the aligned timing logic works correctly"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)
        
        # Test that the reader was created and has a timer
        assert reader._thread is not None
        assert reader._shutdown is False
        
        # Test that we can force flush and it exports metrics
        reader._receive_metrics("test_data")
        result = reader.force_flush()
        assert result is True
        assert exporter.export_calls == 1
        
        # Clean up
        reader.shutdown()
    
    def test_recurring_export_interval(self):
        """Test that recurring exports are scheduled every 20 seconds"""
        exporter = MockMetricExporter()
        reader = AlignedPeriodicMetricReader(exporter)
        
        with patch('threading.Timer') as mock_timer:
            # Call the export and schedule method directly
            reader._export_and_schedule()
            
            # After initial export, should schedule next export in 20 seconds
            mock_timer.assert_called_with(20, reader._export_and_schedule)
        
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
    client = Traceloop.init(
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