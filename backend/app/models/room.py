from typing import List
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Float, JSON, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base

class RoomFeature(Base):
    __tablename__ = "room_feature"
    id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)

class RoomBadge(Base):
    __tablename__ = "room_badge"
    id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    
class Room(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    
    description: Mapped[str] = mapped_column(String, nullable=False)
    image_2d: Mapped[str] = mapped_column(String, nullable=False)
    image_3d: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    # features: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    # badges: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    # features and badges are many-to-many relationships with the Feature and Badge tables and they are nullable
    
    from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    to_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    status: Mapped[str] = mapped_column(String, nullable=False, default="available") # status can be available, booked, under_maintenance, unavailable

    
    feature_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True, default_factory=[])
    badge_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True, default_factory=[])
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    
