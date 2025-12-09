"""
Custom exceptions for the FastAPI wrapper.
"""


class APIError(Exception):
    """Base API error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Authentication related error."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ModelNotFoundError(APIError):
    """Model not found error."""

    def __init__(self, model: str):
        message = f"Model '{model}' not found"
        super().__init__(message, status_code=404)


class InvalidRequestError(APIError):
    """Invalid request error."""

    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, status_code=400)