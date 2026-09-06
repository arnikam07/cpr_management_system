
import sqlite3

DATABASE = "cpr_management.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            facility TEXT NOT NULL,
            category TEXT NOT NULL,
            duration INTEGER,
            booking_date TEXT NOT NULL,
            base_price REAL NOT NULL,
            gst REAL NOT NULL,
            total_price REAL NOT NULL,
            UNIQUE (facility, booking_date),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    connection.commit()
    connection.close()