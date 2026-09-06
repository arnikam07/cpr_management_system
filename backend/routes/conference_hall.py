from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Booking
from schemas import BookingCreate
from services import conference_hall_service

router = APIRouter(
    prefix="/conference-hall",
    tags=["Conference Hall"]
)


@router.get("/price")
def calculate_price(
    category: str,
    duration_hours: int,
    db: Session = Depends(get_db)
):

    price = conference_hall_service.get_price(
        db,
        category,
        duration_hours
    )

    if not price:
        raise HTTPException(
            status_code=404,
            detail="Rate not found"
        )

    return price


@router.get("/availability")
def check_availability(
    booking_date: str,
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db)
):

    from datetime import date, time

    available = conference_hall_service.check_availability(
        db,
        date.fromisoformat(booking_date),
        time.fromisoformat(start_time),
        time.fromisoformat(end_time)
    )

    return {
        "available": available
    }


@router.post("/book")
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):

    price = conference_hall_service.get_price(
        db,
        booking.category,
        booking.duration_hours
    )

    if not price:
        raise HTTPException(
            status_code=400,
            detail="Invalid category or duration"
        )

    available = conference_hall_service.check_availability(
        db,
        booking.booking_date,
        booking.start_time,
        booking.end_time
    )

    if not available:
        raise HTTPException(
            status_code=409,
            detail="Conference Hall is already booked for this time"
        )

    new_booking = Booking(
        venue_id=booking.venue_id,
        customer_name=booking.customer_name,
        phone=booking.phone,
        category=booking.category,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        duration_hours=booking.duration_hours,
        base_price=price["base_price"],
        gst_amount=price["gst_amount"],
        total_price=price["total_price"],
        status="confirmed"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking