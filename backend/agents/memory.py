import os
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension

_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
) -> None:
    """Persist a conversation turn with its embedding to PostgreSQL."""
    embedder = _get_embedder()
    embedding = embedder.encode(content).tolist()

    turn = Conversation(
        session_id=session_id,
        role=role,
        content=content,
        embedding=embedding,
    )
    db.add(turn)
    await db.commit()


async def get_relevant_context(
    db: AsyncSession,
    session_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Return the top-k most semantically similar past messages for a session."""
    from sqlalchemy import select, text

    embedder = _get_embedder()
    query_embedding = embedder.encode(query).tolist()
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    stmt = text(
        """
        SELECT role, content,
               embedding <=> CAST(:embedding AS vector) AS distance
        FROM conversations
        WHERE session_id = :session_id
        ORDER BY distance ASC
        LIMIT :top_k
        """
    )
    result = await db.execute(
        stmt,
        {
            "embedding": embedding_str,
            "session_id": session_id,
            "top_k": top_k,
        },
    )
    rows = result.fetchall()
    return [{"role": row.role, "content": row.content} for row in rows]
