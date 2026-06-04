class AidOpsException(Exception):
    pass


class IngestionError(AidOpsException):
    pass


class RetrievalError(AidOpsException):
    pass


class VectorStoreError(AidOpsException):
    pass


class LLMProviderError(AidOpsException):
    pass


class TranscriptionError(AidOpsException):
    pass


class ValidationError(AidOpsException):
    pass


class RateLimitError(AidOpsException):
    pass


class InsufficientContextError(AidOpsException):
    pass
