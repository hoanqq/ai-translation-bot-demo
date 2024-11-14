import os
import time

from openai import AzureOpenAI
from opentelemetry.trace import StatusCode, Status
from opentelemetry import trace

from models.translate import TranslateRequest, TranslateResponse, EvaluationRequest, EvaluationResponse
from .observability import get_logger, get_meter, get_tracer, setup_async_function_call_processor


# Language code to language name mapping
language_map = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese'
}


class AzureOpenAIManager:

    def __init__(self):
        self.logger = get_logger(__name__)
        self.latency_meter = get_meter().create_histogram(
            name="azoai_latency", description="Latency of Azure OpenAI requests", unit="ms")
        self.input_tokens_meter = get_meter().create_counter(name="azoai_input_tokens",
                                                             description="Number of input tokens for Azure OpenAI requests", unit="tokens")
        self.output_tokens_meter = get_meter().create_counter(name="azoai_output_tokens",
                                                              description="Number of output tokens for Azure OpenAI requests", unit="tokens")
        self.total_tokens_meter = get_meter().create_counter(name="azoai_total_tokens",
                                                             description="Total number of tokens for Azure OpenAI requests", unit="tokens")
        self.evaluation_score_meter = get_meter().create_histogram(name="azoai_evaluation_score",
                                                                   description="Evaluation score for Azure OpenAI requests", unit="score")
        self.logger.info("AzureOpenAI initialized")

    def translate_text(self, client: AzureOpenAI, deployment_id, source_language, target_language, source_text) -> str:
        """
        Translates the provided text from the source language to the target language using Azure OpenAI.

        Args:
            client: The AzureOpenAI client object.
            deployment_id: The deployment ID of the Azure OpenAI model.
            source_language: The language to translate from.
            target_language: The language to translate to.
            source_text: The text to be translated.

        Returns:
            response: The translation response from the Azure OpenAI model.
        """
        with get_tracer().start_as_current_span("translate_text") as span:
            try:
                start_time = time.time()
                response = client.chat.completions.create(
                    model=deployment_id,
                    messages=[
                        {
                            'role': 'system',
                            'content': '''You are a translator. YOU ONLY TRANSLATE. You are asked to translate the text you receive from {source_language} to {target_language}.
            The translation should avoid the following issues:
            - Distortion: An element of meaning in the source text is altered in the target text.
            - Unjustified omission: An element of meaning in the source text is not transferred into the target text.
            - Unjustified addition: An element of meaning that does not exist in the source text is added to the target text.
            - Inappropriate register: Incorrect variety of language or inappropriate vocabulary for the text type (e.g. inappropriate level of formality or informality).
            - Unidiomatic expression: An expression sounding unnatural or awkward to a native speaker irrespective of the context in which the expression is used, but the intended meaning can be understood.
            - Error of grammar, syntax, spelling or punctuation.'''.format(source_language=source_language, target_language=target_language)
                        },
                        {
                            'role': 'user',
                            'content': source_text
                        }
                    ],
                    max_tokens=4096,
                    temperature=0.5,
                )
                end_time = time.time()
                total_time_ms = (end_time - start_time) * 1000
                attributes = {"model": response.model, "deployment": deployment_id,
                              "source_language": source_language, "target_language": target_language, "temperature": 0.5}

                self.latency_meter.record(
                    amount=total_time_ms, attributes=attributes)
                self.input_tokens_meter.add(
                    amount=response.usage.prompt_tokens, attributes=attributes)
                self.output_tokens_meter.add(
                    amount=response.usage.completion_tokens, attributes=attributes)
                self.total_tokens_meter.add(
                    amount=response.usage.total_tokens, attributes=attributes)

                target_response = response.choices[0].message.content

                span.set_attributes(attributes)
                span.set_attribute("source_text", source_text)
                span.set_attribute("translated_text", target_response)

                span.set_status(status=Status(StatusCode.OK))
                return target_response

            except Exception as e:
                span.record_exception(e)
                self.logger.error(f"Error during translation: {e}")
                return "Error during translation"

    async def translate(self, request: TranslateRequest) -> TranslateResponse:
        client = AzureOpenAI(
            azure_endpoint=os.getenv('OPENAI_API_BASE'),
            api_key=os.getenv('OPENAI_API_KEY'),
            api_version='2024-02-01',
        )
        deployment_id = os.getenv('OPENAI_DEPLOYMENT_ID')

        source_language = language_map[request.source_language]
        target_language = language_map[request.target_language]

        response = self.translate_text(
            client, deployment_id, source_language, target_language, request.source_text)

        return TranslateResponse(
            target_text=response,
        )

    async def evaluate_translation(self, request: EvaluationRequest) -> EvaluationResponse:
        client = AzureOpenAI(
            azure_endpoint=os.getenv('OPENAI_API_BASE'),
            api_key=os.getenv('OPENAI_API_KEY'),
            api_version='2024-02-01',
        )
        deployment_id = os.getenv('OPENAI_DEPLOYMENT_ID')

        with get_tracer().start_as_current_span("evaluate_translation") as span:
            try:
                start_time = time.time()
                response = client.chat.completions.create(
                    model=deployment_id,
                    messages=[
                        {
                            'role': 'system',
                            'content': (
                                "You are an evaluator tasked with assessing a translation from {source_language} to {target_language}. "
                                "Please evaluate the translation based on the following criteria:\n\n"
                                "- **Correct language**: The target language is the expected one.\n"
                                "- **Accuracy**: The translation should faithfully convey the meaning of the source text.\n"
                                "- **Fluency**: The translation should be grammatically correct and sound natural in the target language.\n"
                                "- **Style**: The translation should preserve the style and tone of the source text.\n\n"
                                "Return a single score between **0** (exclusive) and **1** (exclusive), where **0** represents an incorrect translation and **1** represents a perfect translation.\n\n"
                                "YOU MUST RETURN ONLY THE VALUE OF THE EVALUATION."
                            ).format(source_language=request.source_language, target_language=request.target_language)
                        },
                        {
                            'role': 'user',
                            'content': f"Requested Translation Text: {request.requested_translation_text}\nTranslated Text: {request.translated_text}"
                        }
                    ],
                    max_tokens=4096,
                    temperature=0.5,
                )

                end_time = time.time()
                total_time_ms = (end_time - start_time) * 1000
                attributes = {"model": response.model, "deployment": deployment_id,
                              "source_language": request.source_language, "target_language": request.target_language, "temperature": 0.5}

                evaluation_score = float(response.choices[0].message.content)

                self.latency_meter.record(
                    amount=total_time_ms, attributes=attributes)
                self.input_tokens_meter.add(
                    amount=response.usage.prompt_tokens, attributes=attributes)
                self.output_tokens_meter.add(
                    amount=response.usage.completion_tokens, attributes=attributes)
                self.total_tokens_meter.add(
                    amount=response.usage.total_tokens, attributes=attributes)
                self.evaluation_score_meter.record(
                    amount=evaluation_score, attributes=attributes)

                span.set_attributes(attributes)
                span.set_attribute(
                    "source_text", request.requested_translation_text)
                span.set_attribute("translated_text", request.translated_text)
                span.set_attribute("evaluation_score", evaluation_score)

                span.set_status(status=Status(StatusCode.OK))
                self.logger.info("Evaluation complete")

                return {"evaluation": evaluation_score}

            except Exception as e:
                span.record_exception(e)
                self.logger.error(f"Error during evaluation: {e}")
                return {"error": str(e)}


instance: AzureOpenAIManager = None


def setup():
    get_logger().info("Setting up AzureOpenAIManager")
    global instance
    instance = AzureOpenAIManager()

    def evaluation_request_builder(span):
        attributes = span.attributes
        return EvaluationRequest(
            requested_translation_text=attributes.get("source_text"),
            translated_text=attributes.get("translated_text"),
            source_language=attributes.get("source_language"),
            target_language=attributes.get("target_language")
        )

    setup_async_function_call_processor(
        fn=instance.evaluate_translation,
        request_builder=evaluation_request_builder,
        target_span_names=["translate_text"],
        tracer_provider=trace.get_tracer_provider()
    )
