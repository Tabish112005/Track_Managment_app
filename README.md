# TrekEase — Trekking Management Web Application

TrekEase is a full-stack role-based web application for managing trekking expeditions, bookings, staff assignments, and user reservations.

## Features

- **Role-Based Dashboards:** Dedicated interfaces and workflows for **Admins**, **Staff**, and **Users**.
- **Trek & Booking Management:** Browse treks, create and manage bookings (`my_bookings`), and oversee schedules.
- **Admin & Staff Controls:** Manage treks, monitor bookings, and coordinate operations from centralized dashboards.
- **Persistent Storage:** Powered by SQLite and SQLAlchemy ORM.

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Frontend:** HTML5, CSS3, Bootstrap, Jinja2 Templates
- **Database:** SQLite

## Project Structure

```text
TrekEase/
├── application/
│   ├── controllers.py      # Application routes and business logic
│   ├── database.py         # SQLAlchemy database initialization
│   └── models.py           # Database models (Users, Treks, Bookings, etc.)
├── instance/
│   └── treking-database.sqlite3
├── static/                 # CSS, JavaScript, and image assets
├── templates/
│   ├── admin/              # Admin dashboard and management templates
│   ├── staff/              # Staff dashboard templates
│   └── user/               # User views and booking templates
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md
