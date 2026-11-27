class IdempotencyConflictError(Exception):
    """Raised when an idempotency key is reused with different file content."""