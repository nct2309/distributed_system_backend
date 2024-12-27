from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema

class BookingBase(BaseModel):
    user_id: Annotated[int, Field(examples=[1])]
    room_id: Annotated[int, Field(examples=[1])]
    check_in: Annotated[datetime, Field(examples=["2022-01-01T12:00:00Z"])]
    check_out: Annotated[datetime, Field(examples=["2022-01-02T12:00:00Z"])]
    total_price: Annotated[float, Field(examples=[299])]
    status: Annotated[str, Field(examples=["booked"])]
    
    guest_name: Annotated[str, Field(examples=["John Doe"])]
    guest_contact_number: Annotated[str, Field(examples=["+1234567890"])]
    guest_email: Annotated[str, Field(examples=["abc@gmail.com"])]
    number_of_guests: Annotated[int, Field(examples=[1])]
        
class Booking(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
    
class BookingReadExternal(BookingRead):
    user: dict = {}
    room: dict = {}

class BookingCreate(BookingBase):
    # odmit user and room fields as they are not required when creating a booking
    model_config = ConfigDict(extra="forbid")
            
class BookingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    user_id: Annotated[int | None, Field(examples=[1], default=None)]
    room_id: Annotated[int | None, Field(examples=[1], default=None)]
    check_in: Annotated[datetime | None, Field(examples=["2022-01-01T12:00:00Z"], default=None)]
    check_out: Annotated[datetime | None, Field(examples=["2022-01-02T12:00:00Z"], default=None)]
    total_price: Annotated[float | None, Field(examples=[299], default=None)]
    status: Annotated[str | None, Field(examples=["booked"], default=None)]
    
    guest_name: Annotated[str | None, Field(examples=["John Doe"], default=None)]
    guest_contact_number: Annotated[str, Field(examples=["+1234567890"], default=None)]
    guest_email: Annotated[str | None, Field(examples=["abc@gmail.com"], default=None)]
    number_of_guests: Annotated[int | None, Field(examples=[1], default=None)]
    
class BookingUpdateInternal(BookingUpdate):
    updated_at: datetime
    
class BookingDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    deleted_at: datetime
    
