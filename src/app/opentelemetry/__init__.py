from dataclasses import dataclass
from time import time
import os
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute, get_request_handler
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_INSTANCE_ID, Resource

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter

from opentelemetry.instrumentation.logging import LoggingInstrumentor
import logging
from pythonjsonlogger.json import JsonFormatter

from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter

from starlette.routing import Match

from app.settings import Environment, get_settings

from .middleware import Middleware

#Configure opentelemetry 
# 1. to include python logs and
# 2. export to console (for demo purposes)
# see https://cloud.google.com/trace/docs/setup/python-ot

LoggingInstrumentor().instrument()

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

resource = Resource.create(attributes={
    SERVICE_NAME: "policyengine",
    # Use the PID as the service.instance.id to avoid duplicate timeseries
    # from different Gunicorn worker processes.
    SERVICE_INSTANCE_ID: f"worker-{os.getpid()}",
})

def initialize_desktop():
    '''
    configure opentelemetry to dump messages to console for desktop testing.
    '''
    traceProvider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    traceProvider.add_span_processor(processor)
    trace.set_tracer_provider(traceProvider)

    reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meterProvider)

def initialize_prod():
    traceProvider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(CloudTraceSpanExporter())
    traceProvider.add_span_processor(processor)
    trace.set_tracer_provider(traceProvider)

    reader = PeriodicExportingMetricReader(
        CloudMonitoringMetricsExporter()
    )
    meterProvider = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(meterProvider)
        

def initialize(app:FastAPI):
    middleware = Middleware(app)
    app.middleware("http")(middleware)

    match get_settings().environment:
        case Environment.DESKTOP:
            return initialize_desktop()
        case Environment.PRODUCTION:
            return initialize_prod()

