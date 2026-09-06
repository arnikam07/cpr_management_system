from sqlalchemy.orm import Session
from models import Venue, Rate, Booking
from rates import VENUE_RATES, GST


def get_auditorium(db: Session):
    return db.query(Venue).filter(
        Venue.name == "Auditorium"
    ).first()


def get_price(db: Session, category: str, duration_hours: int):

    venue = get_auditorium(db)

    if not venue:
        return None

    rate = db.query(Rate).filter(
        Rate.venue_id == venue.id,
        Rate.category == category,
        Rate.duration_hours == duration_hours
    ).first()

    if not rate:
        return None

    gst_amount = rate.base_price * GST / 100
    total_price = rate.base_price + gst_amount

    return {
        "base_price": rate.base_price,
        "gst_amount": gst_amount,
        "total_price": total_price
    }


def check_availability(
    db: Session,
    booking_date,
    start_time,
    end_time
):

    venue = get_auditorium(db)

    if not venue:
        return False

    existing_booking = db.query(Booking).filter(
        Booking.venue_id == venue.id,
        Booking.booking_date == booking_date,
        Booking.status != "cancelled",
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ).first()

    return existing_booking is None