"""Custom exceptions for cladetime."""


class Error(Exception):
    """Base class for exceptions raised by cladetime."""


class CladeTimeInvalidDateError(Error):
    """Raised when an invalid date string is passed to CladeTime."""
