"""Example demonstrating hourly metrics export functionality"""

import os
from traceloop.sdk import Traceloop

def main():
    """Example showing how to enable hourly metrics export"""
    
    print("Example 1: Enable hourly metrics export via parameter")
    Traceloop.init(
        app_name="hourly-metrics-example",
        api_endpoint="https://api.traceloop.com",
        api_key="your-api-key-here",
        metrics_hourly_export=True  # Enable hourly export
    )
    
    # Your application code here...
    print("Metrics will now be exported on the hour (1:00, 2:00, 3:00, etc.)")
    
    print("\nExample 2: Enable hourly metrics export via environment variable")
    # Set the environment variable before calling Traceloop.init()
    os.environ["TRACELOOP_METRICS_HOURLY_EXPORT"] = "true"
    
    Traceloop.init(
        app_name="hourly-metrics-env-example",
        api_endpoint="https://api.traceloop.com", 
        api_key="your-api-key-here"
    )
    
    # Your application code here...
    print("Metrics will now be exported on the hour via environment variable setting")

    print("""
    Environment Variable Options:
    - TRACELOOP_METRICS_HOURLY_EXPORT=true  (enables hourly export)
    - TRACELOOP_METRICS_HOURLY_EXPORT=1     (enables hourly export)
    - TRACELOOP_METRICS_HOURLY_EXPORT=yes   (enables hourly export)
    - TRACELOOP_METRICS_HOURLY_EXPORT=false (uses default periodic export)
    """)

if __name__ == "__main__":
    main()