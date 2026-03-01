from sqlalchemy import Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.db.database import Base


class HealthLog(Base):
    __tablename__ = "health_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    api_id: Mapped[int] = mapped_column(
        ForeignKey("apis.id", ondelete="CASCADE")
    )

    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean)

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationship (optional but good practice)
    api = relationship("API", back_populates="logs")