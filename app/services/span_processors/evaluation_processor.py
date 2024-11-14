from opentelemetry.sdk.trace import SpanProcessor
import asyncio
import logging

logger = logging.getLogger(__name__)


class AsyncFunctionCallSpanProcessor(SpanProcessor):
    """
    A custom SpanProcessor that calls a specified function asynchronously when a span ends.

    Attributes:
        fn (callable): The function to call asynchronously.
        request_builder (callable): Function to build a request from a span.
        target_span_names (list): List of target span names for evaluation. If empty, all spans are processed.
    """

    def __init__(self, fn, request_builder, target_span_names=None):
        """
        Initializes the AsyncFunctionCallSpanProcessor.

        Args:
            fn (callable): The function to call asynchronously.
            request_builder (callable): Function to build a request from a span.
            target_span_names (list, optional): List of target span names for evaluation. Defaults to an empty list.
        """
        super().__init__()
        self.fn = fn
        self.request_builder = request_builder
        self.target_span_names = target_span_names or []

    def on_end(self, span):
        """
        Called when a span ends. If the span name is in the target span names list (or if the list is empty),
        it builds a request from the span and calls the specified function asynchronously.

        Args:
            span (Span): The span that just ended.
        """
        if not self.target_span_names or span.name in self.target_span_names:
            try:
                request = self.request_builder(span)
                asyncio.create_task(self.fn(request))
            except Exception as e:
                logger.error("Error in AsyncFunctionCallSpanProcessor on_end: %s", str(e), exc_info=True)
