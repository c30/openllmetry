from collections.abc import Sequence
from typing import Dict, Optional
import datetime

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
)
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.sdk.resources import Resource

from opentelemetry import metrics


class AlignedPeriodicMetricReader(PeriodicExportingMetricReader):
    """
    A MetricReader that exports metrics at aligned intervals within each minute.
    Specifically exports at 00, 20, and 40 seconds of each minute.
    This ensures that metrics are reported at consistent clock times rather than at
    intervals from application start time.

    Inherits from PeriodicExportingMetricReader to leverage OpenTelemetry SDK's
    robust thread management, export locking, and shutdown handling.
    """

    def __init__(
        self,
        exporter: MetricExporter,
        export_timeout_millis: Optional[float] = None,
    ):
        # Initialize with a dummy interval - we'll override the _ticker method anyway
        # Use 20 seconds (20000ms) as it matches our aligned interval
        super().__init__(
            exporter=exporter,
            export_interval_millis=20000,  # This will be ignored by our custom _ticker
            export_timeout_millis=export_timeout_millis or 30000,
        )

    def _ticker(self) -> None:
        """
        Override the periodic ticker to use aligned timing instead of fixed intervals.
        Exports at 00, 20, and 40 seconds of each minute.
        """
        while not self._shutdown:
            try:
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

                # Wait until the next aligned export time or until shutdown
                if self._shutdown_event.wait(seconds_until_next_export):
                    break  # Shutdown was requested

                # Perform the metric collection and export
                try:
                    self.collect(timeout_millis=self._export_timeout_millis)
                except Exception as e:
                    # Use the same error handling pattern as the parent class
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.warning(
                        "Exception during aligned metric collection: %s. Will try again at next aligned interval.",
                        e,
                        exc_info=True,
                    )

            except Exception as e:
                # Handle any unexpected errors in the timing calculation
                import logging
                _logger = logging.getLogger(__name__)
                _logger.exception("Unexpected error in aligned metric ticker: %s", e)
                # Fall back to 20-second wait to avoid tight loop
                if self._shutdown_event.wait(20):
                    break

        # Final collection before shutdown (same as parent class)
        try:
            self.collect(timeout_millis=self._export_timeout_millis)
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning("Final metric collection failed during shutdown: %s", e, exc_info=True)


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
