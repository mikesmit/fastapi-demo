from fastapi import FastAPI
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_INSTANCE_ID, Resource

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter

import logging



from starlette.routing import Match

from fastapi_demo.settings import Environment, get_settings

from .middleware import Middleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

#Configure opentelemetry 
# 1. to include python logs and
# 2. export to console (for demo purposes)
# see https://cloud.google.com/trace/docs/setup/python-ot

class GCPLoggingInstrumentor:
    '''
    Configures the standard opentelemetry logging instrumentor to generate
    json logs as per gcp expectations.
    '''
    def instrument(self):
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from pythonjsonlogger.json import JsonFormatter
        logHandler = logging.StreamHandler()
        formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(message)s %(otelTraceID)s %(otelSpanID)s %(otelTraceSampled)s",
            rename_fields={
                "levelname": "severity",
                "asctime": "timestamp",
                "otelTraceID": "logging.googleapis.com/trace",
                "otelSpanID": "logging.googleapis.com/spanId",
                "otelTraceSampled": "logging.googleapis.com/trace_sampled",
                },
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        logHandler.setFormatter(formatter)
        logging.basicConfig(
            level=logging.INFO,
            handlers=[logHandler],
        )
        LoggingInstrumentor().instrument()

def export_ot_to_console(resource:Resource):
    '''
    configure opentelemetry to dump messages to console for debugging on desktop
    '''
    traceProvider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    traceProvider.add_span_processor(processor)
    trace.set_tracer_provider(traceProvider)

    reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meterProvider)

def export_ot_to_gcp(resource:Resource):
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
    '''
    configure opentelemetry to directly export to gcp cloudtrace/metrics
    useful when running in the google cloud
    '''
    traceProvider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(CloudTraceSpanExporter())
    traceProvider.add_span_processor(processor)
    trace.set_tracer_provider(traceProvider)

    reader = PeriodicExportingMetricReader(
        CloudMonitoringMetricsExporter()
    )
    meterProvider = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(meterProvider)


class FastAPIEnhancedInstrumenter:
    '''
    Enhances the default FastAPIInstrumentor to generate per operation
    metrics instead of global for the whole api.
    '''
    def instrument(self, app:FastAPI):
        FastAPIInstrumentor.instrument_app(app)
        middleware = Middleware(app)
        app.middleware("http")(middleware)

