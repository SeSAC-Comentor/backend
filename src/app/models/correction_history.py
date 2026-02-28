import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class CorrectionHistory(Base):
    __tablename__ = "correction_histories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    original_comment: Mapped[str] = mapped_column(Text)
    corrected_comment: Mapped[str] = mapped_column(Text)
    is_corrected: Mapped[bool] = mapped_column()
    severity: Mapped[str | None] = mapped_column(String(10), nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    problem_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), index=True,
    )

    user = relationship("User", back_populates="histories")
