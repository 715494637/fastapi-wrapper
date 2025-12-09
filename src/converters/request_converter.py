"""
Converter for transforming OpenAI chat completion requests to Gemini API format.
"""

from typing import List, Optional, Dict, Any
from src.models.gemini_models import ChatCompletionRequest, ChatMessage
import logging

logger = logging.getLogger(__name__)


class OpenAItoGeminiConverter:
    """Converts OpenAI format requests to Gemini format."""

    def __init__(self):
        """Initialize the converter."""
        # Use Gemini model names directly
        # Accept both GPT-style names (for compatibility) and Gemini names
        self.model_mapping = {
            # GPT-style names (for backward compatibility)
            "gpt-4": "gemini-2.5-pro",
            "gpt-4-turbo": "gemini-2.5-pro",
            "gpt-3.5-turbo": "gemini-2.5-flash",
            "gpt-3.5-turbo-16k": "gemini-2.5-flash",
            # Gemini names (passed through directly)
            "gemini-2.5-pro": "gemini-2.5-pro",
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-3.0-pro": "gemini-3.0-pro",
            "unspecified": "unspecified",
        }

    def convert_request(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """
        Convert OpenAI chat completion request to Gemini format.

        Args:
            request: OpenAI chat completion request

        Returns:
            Dictionary with Gemini-compatible parameters
        """
        try:
            # Extract conversation history
            conversation = self._convert_messages(request.messages)

            # Get mapped model or use provided model
            gemini_model = self.model_mapping.get(request.model, request.model)

            # Build Gemini request parameters
            gemini_params = {
                "prompt": conversation,
                "model": gemini_model,
            }

            # Add optional parameters
            if request.gem_id:
                gemini_params["gem"] = request.gem_id

            if request.files:
                gemini_params["files"] = request.files

            # Add generation parameters (Gemini supports some of these)
            if request.temperature is not None:
                gemini_params["temperature"] = request.temperature

            if request.max_tokens is not None:
                gemini_params["max_tokens"] = request.max_tokens

            logger.info(f"Converted OpenAI request to Gemini format: {gemini_params}")
            return gemini_params

        except Exception as e:
            logger.error(f"Error converting request: {str(e)}")
            raise

    def _convert_messages(self, messages: List[ChatMessage]) -> str:
        """
        Convert OpenAI message format to Gemini conversation format.

        Args:
            messages: List of OpenAI messages

        Returns:
            Formatted conversation string for Gemini
        """
        conversation_parts = []
        system_prompt = None

        for message in messages:
            if message.role == "system":
                system_prompt = message.content
                continue

            # Format message for Gemini
            if message.role == "user":
                prefix = "User: "
            elif message.role == "assistant":
                prefix = "Assistant: "
            else:
                continue  # Skip other roles

            content = message.content or ""
            conversation_parts.append(f"{prefix}{content}")

        # Add system prompt at the beginning if present
        if system_prompt:
            conversation_parts.insert(0, f"System: {system_prompt}")

        return "\n\n".join(conversation_parts)

    def map_model(self, openai_model: str) -> str:
        """
        Map OpenAI model name to Gemini model.

        Args:
            openai_model: OpenAI model name

        Returns:
            Mapped Gemini model name
        """
        return self.model_mapping.get(openai_model, openai_model)