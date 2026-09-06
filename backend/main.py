from fastapi import FastAPI
from database import engine, Base
from routes import auditorium, conference_hall

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CPR Pune Booking System",
    version="1.0.0"
)

app.include_router(auditorium.router)
app.include_router(conference_hall.router)


@app.get("/")
def home():
    return {
        "message": "CPR Pune Booking System API"
    }