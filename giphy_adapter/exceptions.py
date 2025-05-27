"""
Custom exceptions for Giphy adapter operations.
"""


class GiphyError(Exception):
    """Base exception for all Giphy adapter errors."""

    def __init__(self, message: str, error_type: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class GiphyTimeout(GiphyError):
    """Raised when API requests timeout."""

    def __init__(self, message: str = "Request timeout"):
        super().__init__(message, "TIMEOUT")


class GiphyValidation(GiphyError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")
