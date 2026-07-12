from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    logs: Mapped[List["PingLog"]] = relationship("PingLog", back_populates="site", cascade="all, delete-orphan")

class PingLog(Base):
    __tablename__ = "ping_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_up: Mapped[bool] = mapped_column(Boolean, nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    site: Mapped["Site"] = relationship("Site", back_populates="logs")
