from flask import Blueprint, request, jsonify
from database.db import get_db_connection

banquet_hall = Blueprint("banquet_hall", __name__)


# Banquet Hall pricing
PRICES = {
    "5": {
        "Member": 5000,
        "Non-Member/Police": 6000,
        "Citizen": 10000
    },
    "10": {
        "Member": 8000,
        "Non-Member/Police": 9000,
        "Citizen": 15000
    }
}


# Get Banquet Hall Price
@banquet_hall.route("/api/banquet-hall/price", methods=["GET"])
def get_price():
    duration = request.args.get("duration")
    category = request.args.get("category")

    if duration not in PRICES:
        return jsonify({
            "error": "Duration must be 5 or 10 hours"
        }), 400

    if category not in PRICES[duration]:
        return jsonify({
            "error": "Invalid category"
        }), 400

    base_price = PRICES[duration][category]
    gst = base_price * 0.18
    total_price = base_price + gst

    return jsonify({
        "facility": "Banquet Hall",
        "duration": int(duration),
        "category": category,
        "base_price": base_price,
        "gst": gst,
        "total_price": total_price
    })


# Check Banquet Hall Availability
@banquet_hall.route("/api/banquet-hall/availability", methods=["GET"])
def check_banquet_hall_availability():
    booking_date = request.args.get("booking_date")

    if not booking_date:
        return jsonify({
            "error": "Booking date is required"
        }), 400

    connection = get_db_connection()

    existing_booking = connection.execute(
        """
        SELECT id FROM bookings
        WHERE facility = ? AND booking_date = ?
        """,
        ("Banquet Hall", booking_date)
    ).fetchone()

    connection.close()

    if existing_booking:
        return jsonify({
            "facility": "Banquet Hall",
            "booking_date": booking_date,
            "available": False,
            "message": "Banquet Hall is already booked for this date"
        })

    return jsonify({
        "facility": "Banquet Hall",
        "booking_date": booking_date,
        "available": True,
        "message": "Banquet Hall is available for this date"
    })


# Book Banquet Hall
@banquet_hall.route("/api/banquet-hall/book", methods=["POST"])
def book_banquet_hall():
    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    category = data.get("category")
    duration = str(data.get("duration"))
    booking_date = data.get("booking_date")

    if not name or not phone or not category or not duration or not booking_date:
        return jsonify({
            "error": "Name, phone, category, duration and booking date are required"
        }), 400

    if duration not in PRICES:
        return jsonify({
            "error": "Duration must be 5 or 10 hours"
        }), 400

    if category not in PRICES[duration]:
        return jsonify({
            "error": "Invalid category"
        }), 400

    # Check duplicate booking
    connection = get_db_connection()

    existing_booking = connection.execute(
        """
        SELECT id FROM bookings
        WHERE facility = ? AND booking_date = ?
        """,
        ("Banquet Hall", booking_date)
    ).fetchone()

    if existing_booking:
        connection.close()
        return jsonify({
            "error": "Banquet Hall is already booked for this date"
        }), 409

    # Calculate price
    base_price = PRICES[duration][category]
    gst = base_price * 0.18
    total_price = base_price + gst

    # Insert customer
    cursor = connection.execute(
        """
        INSERT INTO customers (name, phone, email)
        VALUES (?, ?, ?)
        """,
        (name, phone, email)
    )

    customer_id = cursor.lastrowid

    # Insert booking
    connection.execute(
        """
        INSERT INTO bookings
        (customer_id, facility, category, duration,
         booking_date, base_price, gst, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            customer_id,
            "Banquet Hall",
            category,
            int(duration),
            booking_date,
            base_price,
            gst,
            total_price
        )
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Banquet Hall booking successful",
        "customer": name,
        "facility": "Banquet Hall",
        "category": category,
        "duration": int(duration),
        "booking_date": booking_date,
        "base_price": base_price,
        "gst": gst,
        "total_price": total_price
    }), 201


# Get All Banquet Hall Bookings
@banquet_hall.route("/api/banquet-hall/bookings", methods=["GET"])
def get_banquet_hall_bookings():
    connection = get_db_connection()

    bookings = connection.execute(
        """
        SELECT
            bookings.id,
            customers.name,
            customers.phone,
            customers.email,
            bookings.category,
            bookings.duration,
            bookings.booking_date,
            bookings.base_price,
            bookings.gst,
            bookings.total_price
        FROM bookings
        JOIN customers
        ON bookings.customer_id = customers.id
        WHERE bookings.facility = ?
        ORDER BY bookings.booking_date
        """,
        ("Banquet Hall",)
    ).fetchall()

    connection.close()

    return jsonify([
        dict(booking) for booking in bookings
    ])


# Get Single Banquet Hall Booking
@banquet_hall.route("/api/banquet-hall/bookings/<int:booking_id>", methods=["GET"])
def get_single_banquet_hall_booking(booking_id):
    connection = get_db_connection()

    booking = connection.execute(
        """
        SELECT
            bookings.id,
            customers.name,
            customers.phone,
            customers.email,
            bookings.category,
            bookings.duration,
            bookings.booking_date,
            bookings.base_price,
            bookings.gst,
            bookings.total_price
        FROM bookings
        JOIN customers
        ON bookings.customer_id = customers.id
        WHERE bookings.id = ?
        AND bookings.facility = ?
        """,
        (booking_id, "Banquet Hall")
    ).fetchone()

    connection.close()

    if not booking:
        return jsonify({
            "error": "Banquet Hall booking not found"
        }), 404

    return jsonify(dict(booking))


# Cancel Banquet Hall Booking
@banquet_hall.route("/api/banquet-hall/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_banquet_hall_booking(booking_id):
    connection = get_db_connection()

    booking = connection.execute(
        """
        SELECT customer_id
        FROM bookings
        WHERE id = ?
        AND facility = ?
        """,
        (booking_id, "Banquet Hall")
    ).fetchone()

    if not booking:
        connection.close()
        return jsonify({
            "error": "Banquet Hall booking not found"
        }), 404

    customer_id = booking["customer_id"]

    # Delete booking
    connection.execute(
        """
        DELETE FROM bookings
        WHERE id = ?
        AND facility = ?
        """,
        (booking_id, "Banquet Hall")
    )

    # Delete associated customer
    connection.execute(
        """
        DELETE FROM customers
        WHERE id = ?
        """,
        (customer_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Banquet Hall booking cancelled successfully",
        "booking_id": booking_id
    })
    