from datetime import date, time
from pydantic import BaseModel


class BookingCreate(BaseModel):
    venue_id: int
    customer_name: str
    phone: str
    category: str
    booking_date: date
    start_time: time
    end_time: time
    duration_hours: int


class BookingResponse(BaseModel):
    id: int
    venue_id: int
    customer_name: str
    phone: str
    category: str
    booking_date: date
    start_time: time
    end_time: time
    duration_hours: int
    base_price: float
    gst_amount: float
    total_price: float
    status: str

    class Config:
        from_attributes = True