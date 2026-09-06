from database import SessionLocal, engine, Base
from models import Venue, Rate
from rates import VENUE_RATES, GST


Base.metadata.create_all(bind=engine)

db = SessionLocal()

for venue_name, rates in VENUE_RATES.items():

    venue = db.query(Venue).filter(
        Venue.name == venue_name
    ).first()

    if not venue:
        venue = Venue(name=venue_name)
        db.add(venue)
        db.commit()
        db.refresh(venue)

    for rate_data in rates:

        existing_rate = db.query(Rate).filter(
            Rate.venue_id == venue.id,
            Rate.category == rate_data["category"],
            Rate.duration_hours == rate_data["duration_hours"]
        ).first()

        if not existing_rate:
            rate = Rate(
                venue_id=venue.id,
                category=rate_data["category"],
                duration_hours=rate_data["duration_hours"],
                base_price=rate_data["base_price"],
                gst_percentage=GST
            )

            db.add(rate)

db.commit()
db.close()

print("Database seeded successfully.")