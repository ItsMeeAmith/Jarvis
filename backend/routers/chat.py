import json
import os
import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from agents.jarvis_agent import stream_jarvis_response
from agents.memory import save_message

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/jarvis")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    session_id = str(uuid.uuid4())

    try:
        # Load existing session history from Redis
        history_raw = await redis_client.get(f"session:{session_id}:history")
        history: list[dict] = json.loads(history_raw) if history_raw else []

        while True:
            user_message = await websocket.receive_text()

            if not user_message.strip():
                continue

            # Persist user message
            async with AsyncSessionLocal() as db:
                await save_message(db, session_id, "user", user_message)

            # Stream JARVIS response tokens
            full_response = ""
            async for token in stream_jarvis_response(user_message, history):
                await websocket.send_text(token)
                full_response += token

            # Signal end of stream
            await websocket.send_text("[DONE]")

            # Update in-memory history (keep last 20 turns = 10 exchanges)
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": full_response})
            history = history[-20:]

            # Persist updated history to Redis (TTL 2 hours)
            await redis_client.setex(
                f"session:{session_id}:history",
                7200,
                json.dumps(history),
            )

            # Persist JARVIS response
            async with AsyncSessionLocal() as db:
                await save_message(db, session_id, "assistant", full_response)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(f"[ERROR] {str(exc)}")
        except Exception:
            pass
    finally:
        await redis_client.aclose()
