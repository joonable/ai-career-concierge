class AppError(Exception):
    """Base application error."""


class AuthenticationError(AppError):
    """Raised when an authenticated request cannot be trusted."""


class IntegrationError(AppError):
    """Raised when an external integration fails."""
