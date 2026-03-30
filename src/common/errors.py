class AppError(Exception):
    """Base application error."""


class AuthenticationError(AppError):
    """Raised when an authenticated request cannot be trusted."""


class IntegrationError(AppError):
    """Raised when an external integration fails."""


class PromptLoadError(IntegrationError):
    """Raised when a prompt asset cannot be loaded or rendered."""


class ProviderRequestError(IntegrationError):
    """Raised when an external model provider request fails."""


class ProviderResponseParseError(IntegrationError):
    """Raised when a provider response cannot be parsed or validated."""
