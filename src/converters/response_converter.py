"""
Converter for transforming Gemini API responses to OpenAI format.
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from src.models.gemini_models import (
    ChatCompletionResponse,
    Choice,
    ChatMessage,
    Usage,
    ModelInfo,
    ModelsResponse,
    Role,
)
import logging

logger = logging.getLogger(__name__)


class GeminitoOpenAIConverter:
    """Converts Gemini format responses to OpenAI format."""

    def __init__(self):
        """Initialize the converter."""
        # Keep original Gemini model names
        # No mapping needed - return the model name as-is
        self.model_mapping = {}  # Empty dict means no mapping, return model names as-is

    def convert_chat_response(
        self,
        gemini_response: Any,
        model: str,
        request_id: Optional[str] = None,
    ) -> ChatCompletionResponse:
        """
        Convert Gemini response to OpenAI chat completion format.

        Args:
            gemini_response: Gemini API response
            model: Model name used for the request
            request_id: Optional request ID

        Returns:
            OpenAI-compatible chat completion response
        """
        try:
            # Generate response ID
            response_id = request_id or f"chatcmpl-{uuid.uuid4().hex[:8]}"
            timestamp = int(time.time())

            # Extract text from Gemini response
            text_content = getattr(gemini_response, 'text', '')

            # Create choice
            choice = Choice(
                index=0,
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    content=text_content,
                ),
                finish_reason="stop",
            )

            # Create usage info (estimated)
            usage = Usage(
                prompt_tokens=self._estimate_tokens(str(gemini_response.metadata) if hasattr(gemini_response, 'metadata') else ''),
                completion_tokens=self._estimate_tokens(text_content),
                total_tokens=0,
            )
            usage.total_tokens = usage.prompt_tokens + usage.completion_tokens

            # Use original model name
            openai_model = model

            # Create response
            response = ChatCompletionResponse(
                id=response_id,
                created=timestamp,
                model=openai_model,
                choices=[choice],
                usage=usage,
            )

            logger.info(f"Converted Gemini response to OpenAI format")
            return response

        except Exception as e:
            logger.error(f"Error converting response: {str(e)}")
            raise

    def convert_models_list(self, available_models: List[str]) -> ModelsResponse:
        """
        Convert list of available Gemini models to OpenAI models format.

        Args:
            available_models: List of available Gemini model names

        Returns:
            OpenAI-compatible models response
        """
        timestamp = int(time.time())
        model_data = []

        for model_name in available_models:
            openai_model = self.model_mapping.get(model_name, model_name)
            model_info = ModelInfo(
                id=openai_model,
                created=timestamp,
                owned_by="google",
            )
            model_data.append(model_info)

        return ModelsResponse(
            data=model_data,
        )

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # Rough estimation: ~4 characters per token for English
        # This is a simplified estimation - in production, use a proper tokenizer
        return max(1, len(text) // 4)

    def convert_error_response(
        self,
        error_message: str,
        error_type: str = "invalid_request_error",
        status_code: int = 400,
    ) -> Dict[str, Any]:
        """
        Convert error to OpenAI format.

        Args:
            error_message: Error message
            error_type: Type of error
            status_code: HTTP status code

        Returns:
            OpenAI-compatible error response
        """
        return {
            "error": {
                "message": error_message,
                "type": error_type,
                "code": status_code,
            },
            "type": "error",
        }