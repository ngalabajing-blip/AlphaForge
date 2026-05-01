"""
OpenTelemetry helpers — graceful no-ops when otel libs are not installed.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

try:
    from opentelemetry import trace  # type: ignore[import-not-found]
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,  # type: ignore[import-not-found]
    )
    from opentelemetry.sdk.resources import Resource  # type: ignore[import-not-found]
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore[import-not-found]
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore[import-not-found]

    _OTEL_AVAILABLE = True
except Exception:  # pragma: no cover
    _OTEL_AVAILABLE = False


def configure_tracing(service_name: str, otel_endpoint: str | None) -> None:
    """Configure an OTLP exporter if both otel libs and an endpoint are present."""
    if not _OTEL_AVAILABLE or not otel_endpoint:
        return
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


@contextmanager
def span(name: str, **attrs) -> Iterator[None]:
    """Open a span if otel is available, otherwise a no-op."""
    if not _OTEL_AVAILABLE:
        yield
        return
    tracer = trace.get_tracer("alphaforge")
    with tracer.start_as_current_span(name, attributes=attrs):
        yield
