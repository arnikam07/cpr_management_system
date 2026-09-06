from flask import Flask
from database.db import create_tables
from routes.swimming_pool import swimming_pool
from routes.banquet_hall import banquet_hall

app = Flask(__name__)

# Create database tables
create_tables()

# Register Swimming Pool routes
app.register_blueprint(swimming_pool)
app.register_blueprint(banquet_hall)


@app.route("/")
def home():
    return "CPR Management System Backend is Running!"


if __name__ == "__main__":
    app.run(debug=True)