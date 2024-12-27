# write me the code to add:
# const commonFeatures = [
#   "King-size bed",
#   "Queen-size bed",
#   "Twin beds",
#   "Ocean view",
#   "City view",
#   "Mountain view",
#   "Free WiFi",
#   "Flat-screen TV",
#   "Air conditioning",
#   "Mini-bar",
#   "Coffee machine",
#   "In-room safe",
#   "Bathtub",
#   "Shower",
#   "Balcony",
#   "Terrace",
#   "Room service",
#   "Soundproof",
#   "Non-smoking",
#   "Interconnected rooms available",
#   "Up to 3 guests",
#   '55" 4K Smart TV',
# ];

# const commonBadges = [
#   "Ocean View",
#   "Mountain View",
#   "Beachfront",
#   "Family-friendly",
#   "Romantic",
#   "Non-smoking",
#   "Business",
#   "Spa",
#   "Pet-friendly",
#   "Accessible",
#   "Eco-friendly",
#   "Luxury",
#   "Budget",
#   "All-inclusive",
#   "Adults only",
#   "Free Cancellation",
#   "No prepayment",
#   "Breakfast included",
#   "Pool access",
#   "Fitness center",
#   "Restaurant on-site",
#   "Bar on-site",
#   "Free Breakfast",
# ];
# into the RoomFeature and RoomBadge tables respectively
# class RoomFeature(Base):
#     __tablename__ = "room_feature"
#     id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
#     name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
#     description: Mapped[str] = mapped_column(String, nullable=False)

# class RoomBadge(Base):
#     __tablename__ = "room_badge"
#     id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
#     name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
#     description: Mapped[str] = mapped_column(String, nullable=False)
# in the database

from sqlalchemy.orm import Session
from src.app.models.room import RoomFeature, RoomBadge
from src.app.core.config import settings

async def seed(db: Session) -> None:
    common_features = [
        "King-size bed",
        "Queen-size bed",
        "Twin beds",
        "Ocean view",
        "City view",
        "Mountain view",
        "Free WiFi",
        "Flat-screen TV",
        "Air conditioning",
        "Mini-bar",
        "Coffee machine",
        "In-room safe",
        "Bathtub",
        "Shower",
        "Balcony",
        "Terrace",
        "Room service",
        "Soundproof",
        "Non-smoking",
        "Interconnected rooms available",
        "Up to 3 guests",
        '55" 4K Smart TV',
    ]

    common_badges = [
        "Ocean View",
        "Mountain View",
        "Beachfront",
        "Family-friendly",
        "Romantic",
        "Non-smoking",
        "Business",
        "Spa",
        "Pet-friendly",
        "Accessible",
        "Eco-friendly",
        "Luxury",
        "Budget",
        "All-inclusive",
        "Adults only",
        "Free Cancellation",
        "No prepayment",
        "Breakfast included",
        "Pool access",
        "Fitness center",
        "Restaurant on-site",
        "Bar on-site",
        "Free Breakfast",
    ]

    for feature in common_features:
        db.add(RoomFeature(name=feature, description=feature))

    for badge in common_badges:
        db.add(RoomBadge(name=badge, description=badge))

    await db.commit()
    await db.close()
    
import asyncio

uri = settings.POSTGRES_URI

# its async conn to db
async def main():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(uri, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        async with session.begin():
            await seed(session)
            
asyncio.run(main())