"""
FastAPI server for Gemini API wrapper.
"""

import asyncio
import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path to import gemini_webapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gemini_webapi import GeminiClient, set_log_level
from src.models.gemini_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelsResponse,
)
from src.converters import OpenAItoGeminiConverter, GeminitoOpenAIConverter
from src.utils import setup_logger, APIError, AuthenticationError
from config.settings import settings


# Global variables
gemini_client: GeminiClient = None
request_converter: OpenAItoGeminiConverter = None
response_converter: GeminitoOpenAIConverter = None
logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global gemini_client, request_converter, response_converter, logger

    # Setup logging
    logger = setup_logger(__name__, settings.log_level)
    set_log_level(settings.log_level)

    # Initialize converters
    request_converter = OpenAItoGeminiConverter()
    response_converter = GeminitoOpenAIConverter()

    # Initialize Gemini client
    try:
        logger.info("Initializing Gemini client...")
        client_kwargs = {
            "secure_1psid": settings.secure_1psid,
            "secure_1psidts": settings.secure_1psidts,
        }
        if settings.gemini_proxy:
            client_kwargs["proxy"] = settings.gemini_proxy

        gemini_client = GeminiClient(**client_kwargs)

        await gemini_client.init(
            timeout=settings.gemini_timeout,
            auto_close=False,
            auto_refresh=settings.gemini_auto_refresh,
        )

        logger.info("Gemini client initialized successfully")

        # Fetch available gems
        await gemini_client.fetch_gems()
        logger.info(f"Fetched {len(gemini_client.gems)} gems")

    except Exception as e:
        logger.warning(f"Failed to initialize Gemini client: {str(e)}")
        logger.warning("Server will start in limited mode - API endpoints will return authentication errors")
        # Don't raise - allow server to start for testing purposes

    yield

    # Cleanup
    if gemini_client:
        await gemini_client.close()
        logger.info("Gemini client closed")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Exception handlers
@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request, exc):
    """Handle authentication errors."""
    return JSONResponse(
        status_code=401,
        content=response_converter.convert_error_response(
            str(exc), "authentication_error", 401
        ),
    )


@app.exception_handler(APIError)
async def api_exception_handler(request, exc):
    """Handle API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=response_converter.convert_error_response(
            exc.message, "api_error", exc.status_code
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=response_converter.convert_error_response(
            "Internal server error", "internal_server_error", 500
        ),
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the service is healthy."""
    return {"status": "healthy", "service": settings.api_title}


# Models endpoint
@app.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    """List available models."""
    try:
        # Define available Gemini models
        available_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-3.0-pro",
            "unspecified",
        ]

        return response_converter.convert_models_list(available_models)

    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise APIError(f"Failed to list models: {str(e)}")


# Chat completions endpoint
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    """Create a chat completion."""
    try:
        # Convert OpenAI request to Gemini format
        gemini_params = request_converter.convert_request(request)

        # Generate content with Gemini
        logger.info(f"Generating content with model: {request.model}")

        gemini_response = await gemini_client.generate_content(
            gemini_params["prompt"],
            model=gemini_params.get("model"),
            gem=gemini_params.get("gem"),
            files=gemini_params.get("files"),
        )

        # Convert Gemini response to OpenAI format
        response = response_converter.convert_chat_response(
            gemini_response,
            request.model,
        )

        logger.info("Chat completion generated successfully")
        return response

    except Exception as e:
        logger.error(f"Error generating chat completion: {str(e)}")

        # Check for specific error types
        error_message = str(e).lower()
        if "authentication" in error_message or "unauthorized" in error_message:
            raise AuthenticationError("Authentication with Gemini failed")
        elif "rate limit" in error_message or "quota" in error_message:
            raise APIError("Rate limit exceeded", 429)
        elif "model" in error_message:
            raise APIError(f"Model '{request.model}' not available", 404)
        else:
            raise APIError(f"Failed to generate completion: {str(e)}")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.api_title}",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
