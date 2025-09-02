#!/usr/bin/env python3
"""
Manual test to verify that the AlignedPeriodicMetricReader exports at the correct intervals:
- At 00, 20, and 40 seconds of each minute
- Every 20 seconds after the first aligned export

Run this script and observe the export timestamps to verify the timing.
"""

import time
import datetime
from traceloop.sdk.metrics.metrics import AlignedPeriodicMetricReader
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult


class TestMetricExporter(MetricExporter):
    """Test exporter that logs when exports happen"""
    
    def export(self, metrics_data):
        now = datetime.datetime.now()
        print(f"[EXPORT] {now.strftime('%H:%M:%S.%f')[:-3]} - Exported at second {now.second}")
        return MetricExportResult.SUCCESS
        
    def shutdown(self, timeout_millis=30000):
        return True
        
    def force_flush(self, timeout_millis=30000):
        return True


def main():
    print("Testing AlignedPeriodicMetricReader timing...")
    print("Expected exports at: 00, 20, 40 seconds of each minute")
    print("Press Ctrl+C to stop\n")
    
    exporter = TestMetricExporter()
    reader = AlignedPeriodicMetricReader(exporter)
    
    # Add some fake metrics data
    reader._receive_metrics("test_metrics_data_1")
    reader._receive_metrics("test_metrics_data_2")
    
    try:
        print("Waiting for exports... (will show timestamps)")
        # Let it run for a while to see the pattern
        time.sleep(120)  # Run for 2 minutes to see multiple cycles
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        reader.shutdown()
        print("Test completed.")


if __name__ == "__main__":
    main()