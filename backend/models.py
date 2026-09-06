from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey
from database import Base


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    category = Column(String, nullable=False)
    duration_hours = Column(Integer, nullable=False)
    base_price = Column(Float, nullable=False)
    gst_percentage = Column(Float, default=18.0)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)

    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    category = Column(String, nullable=False)

    booking_date = Column(Date, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    duration_hours = Column(Integer, nullable=False)

    base_price = Column(Float, nullable=False)
    gst_amount = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    status = Column(String, default="confirmed")