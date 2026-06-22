class ExecutionError(Exception):
    """Base exception for all execution related errors."""
    pass

class ToolNotFoundError(ExecutionError):
    pass

class ExecutionPermissionError(ExecutionError):
    pass

class OwnershipViolationError(ExecutionError):
    pass

class ToolExecutionError(ExecutionError):
    pass

class AgentExecutionError(ExecutionError):
    pass

class NoDataFoundError(ExecutionError):
    pass
