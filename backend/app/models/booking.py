from typing import List, Optional
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Float, JSON, ARRAY, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .room import Room
from .user import User

class Booking(Base):
    __tablename__ = "booking"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)
    check_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    check_out: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    user: Optional[Mapped[User]] = relationship("User", lazy="selectin", init=False)
    room: Optional[Mapped[Room]] = relationship("Room", lazy="selectin", init=False)
    
    # additional info about the booking
    guest_name: Mapped[str] = mapped_column(String, nullable=False)
    guest_email: Mapped[str] = mapped_column(String, nullable=False)
    number_of_guests: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    guest_contact_number: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
        
    # status can be booked, cancelled or checked_out
    status: Mapped[str] = mapped_column(String, nullable=False, default="booked")
    
