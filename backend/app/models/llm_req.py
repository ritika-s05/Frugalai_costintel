from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    requested_model: Mapped[str | None] = mapped_column(
    String(100),
    nullable=True,)

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)

    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    estimated_cost: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    actual_cost: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    baseline_cost: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    savings: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    savings_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    cache_hit: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    routed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )