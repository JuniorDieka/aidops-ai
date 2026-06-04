from datetime import datetime

from app.core.models import ChatMessage, ChatSession, MessageRole
from app.services.cache import CacheService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ChatSessionManager:
    def __init__(self, cache_service: CacheService) -> None:
        self.cache = cache_service

    async def create_session(self) -> ChatSession:
        session = ChatSession()
        await self._save_session(session)
        logger.info("chat_session_created", session_id=session.id)
        return session

    async def get_session(self, session_id: str) -> ChatSession | None:
        cache_key = f"chat_session:{session_id}"
        session_data = await self.cache.get(cache_key)

        if session_data:
            return ChatSession(**session_data)

        return None

    async def add_message(
        self, session_id: str, role: MessageRole, content: str, citations: list | None = None
    ) -> ChatMessage:
        session = await self.get_session(session_id)
        if not session:
            session = ChatSession(id=session_id)

        message = ChatMessage(role=role, content=content, citations=citations or [])
        session.messages.append(message)
        session.updated_at = datetime.utcnow()

        await self._save_session(session)

        logger.info(
            "message_added",
            session_id=session_id,
            role=role.value,
            message_length=len(content),
        )

        return message

    async def get_messages(self, session_id: str, limit: int | None = None) -> list[ChatMessage]:
        session = await self.get_session(session_id)
        if not session:
            return []

        messages = session.messages
        if limit:
            messages = messages[-limit:]

        return messages

    async def _save_session(self, session: ChatSession) -> None:
        cache_key = f"chat_session:{session.id}"
        await self.cache.set(cache_key, session.model_dump(), ttl=86400)
