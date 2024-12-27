from fastcrud import FastCRUD

from ..models.booking import Booking
from ..schemas.booking import BookingCreate, BookingDelete, BookingRead, BookingUpdate, BookingUpdateInternal

CRUDBooking = FastCRUD[Booking, BookingCreate, BookingUpdate, BookingUpdateInternal, BookingDelete]
crud_bookings = CRUDBooking(Booking)