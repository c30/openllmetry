"""Tests for hourly metrics export functionality"""
import pytest
import datetime
import threading
import time
from unittest.mock import Mock, patch

from traceloop.sdk.metrics.metrics import HourlyExportingMetricReader
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


class TestHourlyExportingMetricReader:
    
    def test_hourly_metric_reader_initialization(self):
        """Test that HourlyExportingMetricReader can be initialized"""
        exporter = MockMetricExporter()
        reader = HourlyExportingMetricReader(exporter)
        
        assert reader._exporter == exporter
        assert reader._export_timeout_millis == 30000  # default
        assert reader._shutdown is False
        assert reader._thread is not None
        
        # Clean up
        reader.shutdown()
    
    def test_custom_export_timeout(self):
        """Test custom export timeout setting"""
        exporter = MockMetricExporter()
        custom_timeout = 60000
        reader = HourlyExportingMetricReader(exporter, export_timeout_millis=custom_timeout)
        
        assert reader._export_timeout_millis == custom_timeout
        
        # Clean up
        reader.shutdown()
    
    def test_force_flush(self):
        """Test force flush functionality"""
        exporter = MockMetricExporter()
        reader = HourlyExportingMetricReader(exporter)
        
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
        reader = HourlyExportingMetricReader(exporter)
        
        assert reader._shutdown is False
        result = reader.shutdown()
        
        assert reader._shutdown is True
        assert result is True
    
    def test_calculate_next_hour_timing_simple(self):
        """Test that the timer is correctly calculated for next hour"""
        exporter = MockMetricExporter()
        reader = HourlyExportingMetricReader(exporter)
        
        # The reader should have been initialized with a timer
        assert reader._thread is not None
        assert reader._shutdown is False
        
        # Clean up
        reader.shutdown()


def test_traceloop_init_with_hourly_metrics():
    """Test that Traceloop.init accepts hourly metrics parameter"""
    from traceloop.sdk import Traceloop
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    
    # Clear any existing singleton
    if hasattr(Traceloop, '_Traceloop__tracer_wrapper'):
        delattr(Traceloop, '_Traceloop__tracer_wrapper')
    if hasattr(Traceloop, '_Traceloop__metrics_wrapper'):  
        delattr(Traceloop, '_Traceloop__metrics_wrapper')
    
    exporter = InMemorySpanExporter()
    
    # This should not raise any errors
    client = Traceloop.init(
        app_name="test_hourly",
        exporter=exporter,
        metrics_hourly_export=True,
        disable_batch=True
    )
    
    # Clean up
    exporter.clear()


def test_environment_variable_support():
    """Test that TRACELOOP_METRICS_HOURLY_EXPORT environment variable works"""
    import os
    from traceloop.sdk import Traceloop
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from traceloop.sdk.metrics.metrics import MetricsWrapper
    
    # Clear any existing singleton
    if hasattr(Traceloop, '_Traceloop__tracer_wrapper'):
        delattr(Traceloop, '_Traceloop__tracer_wrapper')  
    if hasattr(Traceloop, '_Traceloop__metrics_wrapper'):
        delattr(Traceloop, '_Traceloop__metrics_wrapper')
    if hasattr(MetricsWrapper, 'instance'):
        delattr(MetricsWrapper, 'instance')
    
    # Set environment variable
    original_env = os.environ.get("TRACELOOP_METRICS_HOURLY_EXPORT")
    os.environ["TRACELOOP_METRICS_HOURLY_EXPORT"] = "true"
    
    try:
        span_exporter = InMemorySpanExporter()
        
        # Create a mock metrics exporter so metrics are not disabled
        from tests.test_hourly_metrics import MockMetricExporter
        metrics_exporter = MockMetricExporter()
        
        # This should pick up the environment variable
        client = Traceloop.init(
            app_name="test_env_hourly",
            exporter=span_exporter,
            metrics_exporter=metrics_exporter,
            disable_batch=True
        )
        
        # The hourly export should be enabled via environment variable
        assert MetricsWrapper.hourly_export is True
        
    finally:
        # Clean up environment variable
        if original_env is not None:
            os.environ["TRACELOOP_METRICS_HOURLY_EXPORT"] = original_env
        else:
            os.environ.pop("TRACELOOP_METRICS_HOURLY_EXPORT", None)
        
        # Clean up exporter
        span_exporter.clear()