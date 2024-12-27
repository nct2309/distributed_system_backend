from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_booking import crud_bookings
from ...crud.crud_rooms import crud_rooms
from ...schemas.booking import BookingCreate, BookingDelete, BookingRead, BookingUpdate, BookingUpdateInternal
from ...schemas.room import RoomRead, RoomUpdate

router = APIRouter(tags=["bookings"])

@router.post("/booking", response_model=BookingRead, status_code=201)
async def write_booking(
    request: Request, booking: BookingCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> BookingRead:
    """_summary_

    Args:
        request (Request): _description_
        booking (BookingCreate): _description_
        db (Annotated[AsyncSession, Depends): _description_

    Returns:
        BookingRead: _description_
    """
    # check if the check_in date is before the check_out date
    if booking.check_in >= booking.check_out:
        raise ValueError("Check-in date should be before the check-out date")
    # check if there is already a booking for the room in the given date range(status = booked)
    existing_booking = await crud_bookings.exists(db=db, room_id=booking.room_id, check_in__lte=booking.check_out, check_out__gte=booking.check_in, status="booked")
    if existing_booking is not False:
        raise DuplicateValueException("Room is already booked in the given date range")
    
    created_booking: BookingRead = await crud_bookings.create(db=db, object=booking)
    
    return created_booking

@router.get("/bookings", response_model=PaginatedListResponse[BookingRead])
async def read_bookings(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    bookings_data = await crud_bookings.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=BookingRead,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=bookings_data, page=page, items_per_page=items_per_page)
    return response

@router.get("/booking/{id}", response_model=BookingRead)
async def read_booking(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    db_booking: BookingRead | None = await crud_bookings.get(
        db=db, schema_to_select=BookingRead, id=id, is_deleted=False
    )
    if db_booking is None:
        raise NotFoundException("Booking not found")

    return dict(db_booking)

@router.put("/booking/{id}", response_model=dict)
async def update_booking(
    request: Request, id: int, booking: BookingUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """_summary_

    Args:
        request (Request): _description_
        id (int): _description_
        booking (BookingUpdate): _description_
        db (Annotated[AsyncSession, Depends): _description_

    Returns:
        dict: _description_
    """
    # check if check_in date is before check_out date
    if booking.check_in >= booking.check_out:
        raise ValueError("Check-in date should be before the check-out date")
    # check if there is already a booking for the room in the given date range (status = booked)
    existing_booking = await crud_bookings.exists(db=db, room_id=booking.room_id, check_in__lte=booking.check_out, check_out__gte=booking.check_in, status="booked")
    if existing_booking is not False:
        raise DuplicateValueException("Room is already booked in the given date range")
    
    updated_booking: BookingRead = await crud_bookings.update(db=db, id=id, object=booking)

    return {"message": "Booking updated successfully"}

@router.delete("/booking/{id}", response_model=dict)
async def delete_booking(
    request: Request, id: int, booking: BookingDelete, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    deleted_booking: BookingRead = await crud_bookings.delete(db=db, id=id, object=booking)
    return {"message": "Booking deleted successfully"}

# get all bookings of a user
@router.get("/user/{user_id}/bookings", response_model=PaginatedListResponse[BookingRead])
async def read_user_bookings(
    request: Request, user_id: int, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    bookings_data = await crud_bookings.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=BookingRead,
        is_deleted=False,
        user_id=user_id,
        sort_columns=["check_in"],
        sort_order="desc",
    )

    response: dict[str, Any] = paginated_response(crud_data=bookings_data, page=page, items_per_page=items_per_page)
    return response

@router.post("/booking/{id}/cancel")
async def cancel_booking(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """_summary_

    Args:
        request (Request): _description_
        id (int): _description_
        db (Annotated[AsyncSession, Depends): _description_

    Raises:
        NotFoundException: _description_

    Returns:
        _type_: _description_
        
    Further details:
    - If the booking status is booked, the booking status will be updated to "cancelled".
    - If the booking status is checked_out, the booking status will not be updated.
    
    """
    booking: BookingRead = await crud_bookings.get(db=db, schema_to_select=BookingRead, id=id, is_deleted=False)
    if booking is None:
        raise NotFoundException("Booking not found")
    
    if booking.get("status") == "cancelled":
        return {
            "message": "Booking already cancelled"
        }
        
    if booking.get("status") == "booked":
        updated_booking: BookingRead = await crud_bookings.update(db=db, id=id, object=BookingUpdate(status="cancelled"))
        
        return {
            "message": "Booking cancelled successfully"
        }
        
    # booking status is checked_out    
    return {
        "message": "Booking already checked out"
    }

from datetime import datetime, timedelta, date
@router.get("/room/{room_id}/bookings", response_model=PaginatedListResponse[BookingRead])
async def read_room_bookings(
    request: Request, room_id: int, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10,
    status: str = Query("booked", alias="status"),
    start_date: datetime = Query(date.today() - timedelta(days=30), alias="start_date"),
    end_date: datetime = Query(date.today() + timedelta(days=30), alias="end_date")
) -> dict:
    """_summary_
    Args:
        request (Request): _description_
        room_id (int): _description_
        db (Annotated[AsyncSession, Depends): _description_
        page (int, optional): _description_. Defaults to 1.
        items_per_page (int, optional): _description_. Defaults to 10.
        start_date (datetime, optional): _description_. Defaults to 1 month ago (from today).
        end_date (datetime, optional): _description_. Defaults to 1 month later (from today).

    Returns:
        dict: _description_
        
    Further details:
    - Get all bookings of a room with given status within a date range (check by check_out date).
    """
    
    bookings_data = await crud_bookings.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=BookingRead,
        is_deleted=False,
        room_id=room_id,
        sort_columns=["check_out"],
        sort_order="asc",
        status=status,
        check_out__gte=start_date,
        check_out__lte=end_date
    )

    response: dict[str, Any] = paginated_response(crud_data=bookings_data, page=page, items_per_page=items_per_page)
    return response
