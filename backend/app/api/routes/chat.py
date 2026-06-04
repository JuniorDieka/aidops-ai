import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.dependencies import get_chat_session_manager, get_streaming_chat_service
from app.core.models import MessageRole
from app.services.cache import cache_service
from app.services.chat.session import ChatSessionManager
from app.services.chat.streaming import StreamingChatService
from app.utils.logging import get_logger
from app.utils.security import SecurityValidator

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    chat_service: StreamingChatService = Depends(get_streaming_chat_service),
    session_manager: ChatSessionManager = Depends(get_chat_session_manager),
) -> None:
    await websocket.accept()
    logger.info("websocket_connected", session_id=session_id)

    pubsub = await cache_service.subscribe(f"chat:{session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            query = message_data.get("message", "")

            try:
                SecurityValidator.validate_input(query)
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "content": f"Invalid input: {str(e)}"}
                )
                continue

            await session_manager.add_message(session_id, MessageRole.USER, query)

            chat_history = await session_manager.get_messages(session_id, limit=10)

            collected_citations = []
            response_text = ""

            async for chunk in chat_service.stream_response(query, chat_history):
                chunk_dict = chunk.model_dump()

                if chunk.type == "citation" and chunk.citation:
                    collected_citations.append(chunk.citation)

                if chunk.type == "token" and chunk.content:
                    response_text += chunk.content

                await websocket.send_json(chunk_dict)

            await session_manager.add_message(
                session_id, MessageRole.ASSISTANT, response_text, collected_citations
            )

            logger.info(
                "message_processed",
                session_id=session_id,
                query_length=len(query),
                response_length=len(response_text),
            )

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("websocket_error", session_id=session_id, error=str(e))
        try:
            await websocket.send_json({"type": "error", "content": f"Error: {str(e)}"})
        except Exception:
            pass
    finally:
        if pubsub:
            await pubsub.unsubscribe(f"chat:{session_id}")
            await pubsub.close()
