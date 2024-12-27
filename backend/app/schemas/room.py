from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
    
    # status: Mapped[str] = mapped_column(String, nullable=False, default="available") # status can be available, booked, under_maintenance, reserved, unavailable
    # from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # to_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
class RoomBase(BaseModel):
    name: Annotated[str, Field(examples=["Deluxe Ocean View Suite"])]
    description: Annotated[str, Field(examples=["Experience luxury with a breathtaking view"])]
    image_2d: Annotated[str, Field(examples=["/placeholder.svg?height=200&width=300"])] = ""
    image_3d: Annotated[str, Field(examples=["/placeholder.svg?height=200&width=300"])] = ""
    price: Annotated[float, Field(examples=[299])]
    feature_ids: Annotated[list[int], Field(examples=[[1, 2, 3]])]
    badge_ids: Annotated[list[int], Field(examples=[[1, 2, 3]])]
    # status: Annotated[str, Field(examples=["available"], default="available")]
    # from_date: Annotated[datetime | None, Field(examples=["2022-01-01T00:00:00"], default=None)]
    # to_date: Annotated[datetime | None, Field(examples=["2022-01-01T00:00:00"], default=None)]


class Room(TimestampSchema, RoomBase, UUIDSchema, PersistentDeletion):
    pass

class RoomRead(BaseModel):
    id: int
    name: str
    description: str
    image_2d: str = ""
    image_3d: str = ""
    price: float
    feature_ids: list[int]
    badge_ids: list[int]
    # status: str
    # from_date: datetime | None
    # to_date: datetime | None

class RoomReadExternal(RoomRead):
    features: list[dict]
    badges: list[dict]
    
class RoomCreate(RoomBase):
    model_config = ConfigDict(extra="forbid")
    
class RoomUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: Annotated[str | None, Field(examples=["Deluxe Ocean View Suite"], default=None)]
    description: Annotated[str | None, Field(examples=["Experience luxury with a breathtaking view"], default=None)]
    image_2d: Annotated[str | None, Field(examples=["/placeholder.svg?height=200&width=300"], default=None)] = ""
    image_3d: Annotated[str | None, Field(examples=["/placeholder.svg?height=200&width=300"], default=None)] = ""
    price: Annotated[float | None, Field(examples=[299], default=None)]
    feature_ids: Annotated[list[int] | None, Field(examples=[[1, 2, 3]], default=None)]
    badge_ids: Annotated[list[int] | None, Field(examples=[[1, 2, 3]], default=None)]
    # status: Annotated[str | None, Field(examples=["available"], default=None)]
    # from_date: Annotated[datetime | None, Field(examples=["2022-01-01T00:00:00"], default=None)]
    # to_date: Annotated[datetime | None, Field(examples=["2022-01-01T00:00:00"], default=None)]

class RoomUpdateInternal(RoomUpdate):
    updated_at: datetime
       
class RoomDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    is_deleted: bool
    deleted_at: datetime
    
class RoomFeatureBase(BaseModel):
    name: Annotated[str, Field(examples=["King-size bed"])]
    description: Annotated[str, Field(examples=["A large bed fit for a king"])]

class RoomFeatureDetail(RoomFeatureBase):
    id: int
    
class RoomBadgeBase(BaseModel):
    name: Annotated[str, Field(examples=["Ocean View"])]
    description: Annotated[str, Field(examples=["A room with a view of the ocean"])]
    
class RoomBadgeDetail(RoomBadgeBase):
    id: int