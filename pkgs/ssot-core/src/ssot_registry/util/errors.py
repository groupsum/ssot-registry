class RegistryError(Exception):
    """Base registry error."""


class ValidationError(RegistryError):
    """Raised when registry validation fails."""


class GuardError(RegistryError):
    """Raised when a gate or fence refuses a state transition."""
