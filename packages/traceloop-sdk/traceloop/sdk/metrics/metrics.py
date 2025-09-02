from collections.abc import Sequence
from typing import Dict, Optional
import datetime
import threading

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter as GRPCExporter,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter as HTTPExporter,
)
from opentelemetry.semconv_ai import Meters
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    MetricExporter,
    MetricReader,
    MetricExportResult,
)
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.sdk.resources import Resource

from opentelemetry import metrics


class AlignedPeriodicMetricReader(MetricReader):
    """
    A custom MetricReader that exports metrics at aligned intervals within each minute.
    Specifically exports at 00, 20, and 40 seconds of each minute.
    This ensures that metrics are reported at consistent clock times rather than at
    intervals from application start time.
    """

    def __init__(
        self,
        exporter: MetricExporter,
        export_timeout_millis: Optional[float] = None,
    ):
        super().__init__()
        self._exporter = exporter
        self._export_timeout_millis = export_timeout_millis or 30000  # 30 seconds default
        self._shutdown = False
        self._thread = None
        self._collected_metrics = []
        self._metrics_lock = threading.Lock()
        self._start_timer()

    def _receive_metrics(
        self,
        metrics_data,
        timeout_millis: float = 10000,
        **kwargs,
    ) -> None:
        """Called by MetricReader.collect when it receives a batch of metrics"""
        with self._metrics_lock:
            self._collected_metrics.append(metrics_data)

    def _start_timer(self):
        """Start the timer to schedule exports at aligned intervals (00, 20, 40 seconds)"""
        if self._shutdown:
            return

        # Calculate seconds until next aligned time (0, 20, or 40 seconds)
        now = datetime.datetime.now()
        current_second = now.second

        # Find the next export time (0, 20, or 40 seconds of current or next minute)
        if current_second < 20:
            # Next export at 20 seconds of current minute
            next_export = now.replace(second=20, microsecond=0)
        elif current_second < 40:
            # Next export at 40 seconds of current minute
            next_export = now.replace(second=40, microsecond=0)
        else:
            # Next export at 0 seconds of next minute
            next_export = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)

        seconds_until_next_export = (next_export - now).total_seconds()

        # Schedule the first export
        self._thread = threading.Timer(seconds_until_next_export, self._export_and_schedule)
        self._thread.start()

    def _export_and_schedule(self):
        """Export metrics and schedule the next export"""
        if self._shutdown:
            return

        # Export metrics
        try:
            with self._metrics_lock:
                if self._collected_metrics:
                    # Export collected metrics
                    for metrics_data in self._collected_metrics:
                        result = self._exporter.export([metrics_data])
                        if result != MetricExportResult.SUCCESS:
                            print(f"Failed to export metrics: {result}")
                    # Clear collected metrics after export
                    self._collected_metrics.clear()
        except Exception as e:
            print(f"Error during metric export: {e}")

        # Schedule next export in 20 seconds (next aligned interval)
        if not self._shutdown:
            self._thread = threading.Timer(20, self._export_and_schedule)
            self._thread.start()

    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush any pending metrics"""
        try:
            with self._metrics_lock:
                if self._collected_metrics:
                    for metrics_data in self._collected_metrics:
                        result = self._exporter.export([metrics_data])
                        if result != MetricExportResult.SUCCESS:
                            return False
                    self._collected_metrics.clear()
            return True
        except Exception:
            return False

    def shutdown(self, timeout_millis: float = 30000) -> bool:
        """Shutdown the metric reader"""
        self._shutdown = True
        if self._thread and self._thread.is_alive():
            self._thread.cancel()

        try:
            return self._exporter.shutdown(timeout_millis)
        except Exception:
            return False


# Maintain backward compatibility
HourlyExportingMetricReader = AlignedPeriodicMetricReader


class MetricsWrapper(object):
    resource_attributes: dict = {}
    endpoint: str = None
    # if it needs headers?
    headers: Dict[str, str] = {}
    aligned_periodic_export: bool = False
    # Backward compatibility alias
    hourly_export: bool = False
    __metrics_exporter: MetricExporter = None
    __metrics_provider: MeterProvider = None

    def __new__(cls, exporter: MetricExporter = None) -> "MetricsWrapper":
        if not hasattr(cls, "instance"):
            obj = cls.instance = super(MetricsWrapper, cls).__new__(cls)
            if not MetricsWrapper.endpoint:
                return obj

            obj.__metrics_exporter = (
                exporter
                if exporter
                else init_metrics_exporter(
                    MetricsWrapper.endpoint, MetricsWrapper.headers
                )
            )

            # Use either new or old parameter name for backward compatibility
            use_aligned_export = (MetricsWrapper.aligned_periodic_export or
                                  MetricsWrapper.hourly_export)

            obj.__metrics_provider = init_metrics_provider(
                obj.__metrics_exporter,
                MetricsWrapper.resource_attributes,
                use_aligned_export
            )

        return cls.instance

    @staticmethod
    def set_static_params(
        resource_attributes: dict,
        endpoint: str,
        headers: Dict[str, str],
        aligned_periodic_export: bool = False,
    ) -> None:
        MetricsWrapper.resource_attributes = resource_attributes
        MetricsWrapper.endpoint = endpoint
        MetricsWrapper.headers = headers
        MetricsWrapper.aligned_periodic_export = aligned_periodic_export
        # Also set the old parameter name for backward compatibility
        MetricsWrapper.hourly_export = aligned_periodic_export


def init_metrics_exporter(endpoint: str, headers: Dict[str, str]) -> MetricExporter:
    if "http" in endpoint.lower() or "https" in endpoint.lower():
        return HTTPExporter(endpoint=f"{endpoint}/v1/metrics", headers=headers)
    else:
        return GRPCExporter(endpoint=endpoint, headers=headers)


def init_metrics_provider(
    exporter: MetricExporter, resource_attributes: dict = None,
    aligned_periodic_export: bool = False
) -> MeterProvider:
    resource = (
        Resource.create(resource_attributes)
        if resource_attributes
        else Resource.create()
    )

    # Choose the appropriate reader based on aligned_periodic_export setting
    if aligned_periodic_export:
        reader = AlignedPeriodicMetricReader(exporter)
    else:
        reader = PeriodicExportingMetricReader(exporter)

    provider = MeterProvider(
        metric_readers=[reader],
        resource=resource,
        views=metric_views(),
    )

    metrics.set_meter_provider(provider)
    return provider


def metric_views() -> Sequence[View]:
    return [
        View(
            instrument_name=Meters.LLM_TOKEN_USAGE,
            aggregation=ExplicitBucketHistogramAggregation(
                [
                    1,
                    4,
                    16,
                    64,
                    256,
                    1024,
                    4096,
                    16384,
                    65536,
                    262144,
                    1048576,
                    4194304,
                    16777216,
                    67108864,
                ]
            ),
        ),
        View(
            instrument_name=Meters.PINECONE_DB_QUERY_DURATION,
            aggregation=ExplicitBucketHistogramAggregation(
                [
                    0.01,
                    0.02,
                    0.04,
                    0.08,
                    0.16,
                    0.32,
                    0.64,
                    1.28,
                    2.56,
                    5.12,
                    10.24,
                    20.48,
                    40.96,
                    81.92,
                ]
            ),
        ),
        View(
            instrument_name=Meters.PINECONE_DB_QUERY_SCORES,
            aggregation=ExplicitBucketHistogramAggregation(
                [
                    -1,
                    -0.875,
                    -0.75,
                    -0.625,
                    -0.5,
                    -0.375,
                    -0.25,
                    -0.125,
                    0,
                    0.125,
                    0.25,
                    0.375,
                    0.5,
                    0.625,
                    0.75,
                    0.875,
                    1,
                ]
            ),
        ),
    ]
