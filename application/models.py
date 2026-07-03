from .database import db
from datetime import date

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.String(10), unique=True)
    status = db.Column(db.String, default="Active")
    role = db.Column(db.String, default="user", nullable=True)
    created_at = db.Column(db.Date, default=date.today)
    
    bookings = db.relationship("Booking", backref="user")
    assigned_trek = db.relationship("Trek", backref="staff")

class Trek(db.Model):
    __tablename__ = "trek"
    id = db.Column(db.Integer(), primary_key=True)    
    trek_name = db.Column(db.String(30), unique=True, nullable=False)
    location = db.Column(db.String(), nullable=False)
    difficulty = db.Column(db.String(), nullable=False)
    duration = db.Column(db.Integer(), nullable=False)
    available_slots = db.Column(db.Integer(), nullable=False)
    staff_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    status = db.Column(db.String(), default="Open", nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.Date, default=date.today, nullable=False)

    bookings = db.relationship("Booking", backref="trek")

class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(), default="Booked")
    booking_date = db.Column(db.Date, default=date.today)