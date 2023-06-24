"""Custom errors.

https://developer.mozilla.org/docs/Web/HTTP/Status
"""


class CustomException(Exception):
    """Custom exception base class."""

    httpResponseCode = 500  # Internal Server Error


class AuthenticationError(CustomException):
    """Unable to authenticate request."""

    httpResponseCode = 403  # Forbidden


class DatabaseError(CustomException):
    """Unable to perform database operation."""


class MissingParameter(CustomException):
    """Request was missing a required parameter."""

    httpResponseCode = 400  # Bad Request


class UnprocessableRequest(CustomException):
    """Request cannot be processed."""

    httpResponseCode = 422  # Unprocessable Entity
