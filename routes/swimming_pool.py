from flask import Blueprint, request, jsonify
from database.db import get_db_connection

swimming_pool = Blueprint("swimming_pool", __name__)


# Swimming Pool pricing
PRICES = {
    "Member": 15000,
    "Non-Member/Police": 25000,
    "Citizen": 35000
}


# Get Swimming Pool Price
@swimming_pool.route("/api/swimming-pool/price", methods=["GET"])
def get_price():
    category = request.args.get("category")

    if category not in PRICES:
        return jsonify({
            "error": "Invalid category"
        }), 400

    base_price = PRICES[category]
    gst = base_price * 0.18
    total_price = base_price + gst

    return jsonify({
        "facility": "Swimming Pool",
        "category": category,
        "base_price": base_price,
        "gst": gst,
        "total_price": total_price
    })


# Check Swimming Pool Availability
@swimming_pool.route("/api/swimming-pool/availability", methods=["GET"])
def check_swimming_pool_availability():
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
        ("Swimming Pool", booking_date)
    ).fetchone()

    connection.close()

    if existing_booking:
        return jsonify({
            "facility": "Swimming Pool",
            "booking_date": booking_date,
            "available": False,
            "message": "Swimming Pool is already booked for this date"
        })

    return jsonify({
        "facility": "Swimming Pool",
        "booking_date": booking_date,
        "available": True,
        "message": "Swimming Pool is available for this date"
    })


# Book Swimming Pool
@swimming_pool.route("/api/swimming-pool/book", methods=["POST"])
def book_swimming_pool():
    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    category = data.get("category")
    booking_date = data.get("booking_date")

    if not name or not phone or not category or not booking_date:
        return jsonify({
            "error": "Name, phone, category and booking date are required"
        }), 400

    if category not in PRICES:
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
        ("Swimming Pool", booking_date)
    ).fetchone()

    if existing_booking:
        connection.close()
        return jsonify({
            "error": "Swimming Pool is already booked for this date"
        }), 409

    # Calculate price
    base_price = PRICES[category]
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
            "Swimming Pool",
            category,
            None,
            booking_date,
            base_price,
            gst,
            total_price
        )
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Swimming Pool booking successful",
        "customer": name,
        "facility": "Swimming Pool",
        "category": category,
        "booking_date": booking_date,
        "base_price": base_price,
        "gst": gst,
        "total_price": total_price
    }), 201


# Get All Swimming Pool Bookings
@swimming_pool.route("/api/swimming-pool/bookings", methods=["GET"])
def get_swimming_pool_bookings():
    connection = get_db_connection()

    bookings = connection.execute(
        """
        SELECT
            bookings.id,
            customers.name,
            customers.phone,
            customers.email,
            bookings.category,
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
        ("Swimming Pool",)
    ).fetchall()

    connection.close()

    return jsonify([
        dict(booking) for booking in bookings
    ])


# Get Single Swimming Pool Booking
@swimming_pool.route("/api/swimming-pool/bookings/<int:booking_id>", methods=["GET"])
def get_single_swimming_pool_booking(booking_id):
    connection = get_db_connection()

    booking = connection.execute(
        """
        SELECT
            bookings.id,
            customers.name,
            customers.phone,
            customers.email,
            bookings.category,
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
        (booking_id, "Swimming Pool")
    ).fetchone()

    connection.close()

    if not booking:
        return jsonify({
            "error": "Swimming Pool booking not found"
        }), 404

    return jsonify(dict(booking))


# Cancel Swimming Pool Booking
@swimming_pool.route("/api/swimming-pool/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_swimming_pool_booking(booking_id):
    connection = get_db_connection()

    booking = connection.execute(
        """
        SELECT customer_id
        FROM bookings
        WHERE id = ?
        AND facility = ?
        """,
        (booking_id, "Swimming Pool")
    ).fetchone()

    if not booking:
        connection.close()
        return jsonify({
            "error": "Swimming Pool booking not found"
        }), 404

    customer_id = booking["customer_id"]

    # Delete booking
    connection.execute(
        """
        DELETE FROM bookings
        WHERE id = ?
        AND facility = ?
        """,
        (booking_id, "Swimming Pool")
    )

    # Delete customer associated with this booking
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
        "message": "Swimming Pool booking cancelled successfully",
        "booking_id": booking_id
    })