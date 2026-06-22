from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='Trekker')
    is_blacklisted = db.Column(db.Boolean, default=False)

    bookings = db.relationship('Booking', backref='trekker', lazy=True)
    staff_profile = db.relationship('Staff_Profile', backref='user', uselist=False)

class Staff_Profile(db.Model):
    __tablename__ = 'staff_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_detail = db.Column(db.String(150))
    is_approved = db.Column(db.Boolean, default=False)

    assigned_treks = db.relationship('Trek', backref='guide', lazy=True)

class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    slots_available = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    assigned_staff = db.Column(db.Integer, db.ForeignKey('staff_profile.id'), nullable=True)

    bookings = db.relationship('Bookg', backref='trek', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked')
