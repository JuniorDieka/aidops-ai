from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FileType(str, Enum):
    PDF = "pdf"
    AUDIO = "audio"
    SPREADSHEET = "spreadsheet"


class IngestionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowType(str, Enum):
    COMPLIANCE = "compliance"
    DRAFTING = "drafting"
    GRANT_MATCHING = "grant_matching"
    CRISIS_MONITOR = "crisis_monitor"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Citation(BaseModel):
    source_file: str
    page: int | None = None
    section: str | None = None
    chunk_id: str
    score: float
    text: str


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str
    citations: list[Citation] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: list[ChatMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_file: str
    page: int | None = None
    section: str | None = None
    language: str = "en"
    ingested_at: datetime = Field(default_factory=datetime.utcnow)


class IngestionJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    file_name: str
    file_type: FileType
    status: IngestionStatus = IngestionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None
    chunks_created: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowRequest(BaseModel):
    workflow_type: WorkflowType
    parameters: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None


class WorkflowResponse(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_type: WorkflowType
    status: str
    result: dict[str, Any] = Field(default_factory=dict)
    citations: list[Citation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StreamChunk(BaseModel):
    type: str
    content: str | None = None
    citation: Citation | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthCheck(BaseModel):
    status: str
    version: str
    demo_mode: bool
    services: dict[str, bool]
