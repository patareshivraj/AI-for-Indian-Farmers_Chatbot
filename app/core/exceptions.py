class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""
    pass

class InvalidRoleError(Exception):
    """Raised when a user's role is not recognized or invalid."""
    pass

class AccessDeniedError(Exception):
    """Raised when access is denied for a specific resource."""
    pass

class RepositoryError(Exception):
    """Raised when a database error occurs in the repository layer."""
    pass

class ContextBuilderError(Exception):
    """Raised when context building fails."""
    pass

class MemorySecurityError(Exception):
    """Raised when PII or Secrets are attempted to be written to memory."""
    pass
