from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from datetime import datetime, timezone


class API(Base):
    __tablename__ = "apis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )