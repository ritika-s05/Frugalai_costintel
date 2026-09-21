from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SemanticCacheEntry(Base):
    __tablename__ = "semantic_cache_entries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    cache_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    semantic_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    finish_reason: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    hit_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    similarity_threshold: Mapped[float] = mapped_column(
        Float,
        default=0.90,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    last_hit_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


''' 
why embedding ? 
numpy array
   ↓
JSON
   ↓
PostgreSQL TEXT '''