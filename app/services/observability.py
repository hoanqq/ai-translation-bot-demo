import logging
import os
import re
from logging import Logger
from typing import Dict, List, Literal

from fastapi import FastAPI

from .span_processors.evaluation_processor import AsyncFunctionCallSpanProcessor

# OpenTelemetry
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import Meter, MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Span, Tracer, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

SENSITIVE_DATA_SPAN_NAME = "sensitive_data_logged"
SENSITIVE_DATA_INDICATOR_ATTRIBUTE_NAME = "contains_sensitive_data"

DEVELOPMENT_MODE = Literal["DEVELOPMENT"]
PRODUCTION_MODE = Literal["PRODUCTION"]

ACTIVE_SERVICE_NAME = "translator_service"

_has_already_init = False
run_mode: Literal["DEVELOPMENT", "PRODUCTION"] = DEVELOPMENT_MODE

_main_tracer: Tracer = None
_main_logger: Logger = logging.getLogger()
_main_meter: Meter = None
log_level = (os.getenv("OTEL_LOG_LEVEL") or "INFO").upper()

# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s[%(process)d] - %(levelname)s - %(message)s",
)


def ensure_initialized():
    if not _has_already_init:
        raise Exception(
            "Observability module has not been initialized. Please call initialize_observability()."
        )


def is_development() -> bool:
    return run_mode == DEVELOPMENT_MODE


def get_tracer():
    global _main_tracer
    ensure_initialized()
    return _main_tracer


def get_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    return logger


def get_meter():
    global _main_meter
    ensure_initialized()
    return _main_meter


def initialize_observability(
    mode: Literal["DEVELOPMENT", "PRODUCTION"], service_name: str = "ai.translator", environment: str = "Unspecified"
):
    """Initializes the observability once for the lifetime of the application/process"""
    global \
        _has_already_init, \
        run_mode, \
        _main_tracer, \
        _main_logger, \
        _main_meter, \
        ACTIVE_SERVICE_NAME

    if _has_already_init:
        _main_logger.warning(
            "Attempt made to initialize observability more than once")
        return

    _has_already_init = True

    run_mode = mode
    _main_logger.info(f"Initializing the observability with mode: {mode}")
    # See this for all the config options using environment variables: https://opentelemetry.io/docs/specs/otel/protocol/exporter/
    opentelemetry_exporter_otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT")

    if opentelemetry_exporter_otlp_endpoint:
        _main_logger.info("🚀 Configuring OTLP telemetry")
        service_name = os.getenv(
            "OTEL_SERVICE_NAME", service_name
        )  # https://opentelemetry.io/docs/languages/sdk-configuration/general/#otel_service_name
        sample_ratio = float(
            os.getenv("OTEL_TRACES_SAMPLER_ARG", "1.0")
        )  # https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.sampling.html

        # setup the instrumentors
        resource = Resource.create(
            attributes={
                # https://opentelemetry.io/docs/specs/semconv/resource/#service
                "service.name": service_name,
                "service.namespace": "ai.translator",
                # https://opentelemetry.io/docs/specs/semconv/resource/deployment-environment/
                "deployment.environment.name": environment,
                "process.pid": str(
                    os.getpid()
                ),  # https://opentelemetry.io/docs/specs/semconv/attributes-registry/process/
            }
        )

        ACTIVE_SERVICE_NAME = service_name

        # tracing
        trace.set_tracer_provider(
            TracerProvider(
                resource=resource, sampler=ParentBasedTraceIdRatio(
                    sample_ratio)
            )
        )
        batch_span_processor = BatchSpanProcessor(OTLPSpanExporter())
        trace.get_tracer_provider().add_span_processor(batch_span_processor)
        _main_tracer = trace.get_tracer_provider().get_tracer(service_name)

        # metrics
        metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
        meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(meter_provider)
        _main_meter = metrics.get_meter(service_name)

        # logging
        logger_provider = LoggerProvider(resource=resource)
        batch_log_record_processor = BatchLogRecordProcessor(OTLPLogExporter())
        logger_provider.add_log_record_processor(batch_log_record_processor)

        handler = LoggingHandler(
            level=log_level, logger_provider=logger_provider)
        # Attach OTLP handler to root logger
        logging.getLogger().addHandler(handler)
    else:
        _main_logger.info(
            "🚀 OTLP telemetry exporter not configured (set OTEL_EXPORTER_OTLP_ENDPOINT)"
        )
        _main_tracer = trace.get_tracer("default")
        _main_meter = metrics.get_meter("default")

    _main_logger = get_logger()
    _main_logger.info("Observability initialization complete")


def mark_span_as_sensitive(span: Span):
    span.set_attribute(SENSITIVE_DATA_INDICATOR_ATTRIBUTE_NAME, "true")


def add_sensitive_event(span: Span, event: str, attributes: dict[str, str]):
    if not attributes:
        attributes = {}

    attributes[SENSITIVE_DATA_INDICATOR_ATTRIBUTE_NAME] = "true"
    span.add_event(name=event, attributes=attributes)


def log_sensitive_data(
    message: str,
    attributes: str | Dict | int | List = None,
    print_to_console: bool = False,
    span_name: str | None = None,
) -> None:
    if is_development() and print_to_console:
        _main_logger.info(f"{message} - attributes={attributes}")

    if not span_name:
        span_name = SENSITIVE_DATA_SPAN_NAME

    with get_tracer().start_as_current_span(span_name) as span:
        if not attributes:
            attributes = {}
        if isinstance(attributes, dict):
            span.set_attributes({k: str(v) for k, v in attributes.items()})
        if attributes:
            span.set_attribute("event.attributes", str(attributes))

        span.set_attribute("message", message)
        span.set_attribute(SENSITIVE_DATA_INDICATOR_ATTRIBUTE_NAME, "true")


def convert_to_metric_name(input_string: str) -> str:
    """
    Converts a string into a metric name compatible with OpenTelemetry.
    # https://opentelemetry.io/docs/specs/otel/metrics/api/#instrument-name-syntax

    Args:
    input_string (str): The input string to be converted.

    Returns:
    str: The converted metric name.
    """

    # Remove leading and trailing whitespace
    input_string = input_string.strip()
    # Add leading alpha character
    if not re.match(r"^[a-zA-Z]", input_string):
        input_string = "A" + input_string
    # Replace spaces with underscores
    input_string = input_string.replace(" ", "_")
    # Remove special characters and non-alphanumeric characters
    input_string = re.sub(r"[^a-zA-Z0-9_]", "", input_string)
    # Limit the length to 100 characters
    input_string = input_string[:100]

    return input_string


def instrument_application(app: FastAPI):
    _main_logger.info("Setting up OpenTelemetry instrumentation...")
    RequestsInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    OpenAIInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(
        app,
        http_capture_headers_server_request=[".*"]
    )


def setup_async_function_call_processor(fn, request_builder, target_span_names=None, tracer_provider=None):
    """
    Creates and configures an AsyncFunctionCallSpanProcessor, then adds it to the tracer provider.

    :param fn: The function to call on each span.
    :param request_builder: Function to build a request from a span.
    :param target_span_names: List of span names to trigger the function (default is all spans).
    :param tracer_provider: Optional tracer provider. If not provided, uses the global tracer provider.
    """

    if tracer_provider is None:
        tracer_provider = trace.get_tracer_provider()

    async_processor = AsyncFunctionCallSpanProcessor(
        fn=fn,
        request_builder=request_builder,
        target_span_names=target_span_names
    )

    tracer_provider.add_span_processor(async_processor)

    return async_processor
