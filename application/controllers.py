from flask import render_template, redirect, request 

from .models import *
from flask import current_app as app

@app.route("/")
def home():
    trek_count = Trek.query.count()
    user_count = User.query.filter_by(role='user').count()
    staff_count = User.query.filter_by(role='staff').count()
    booking_count = Booking.query.count()
    return render_template("index.html", trek_count=trek_count, user_count=user_count, staff_count=staff_count,
                            booking_count=booking_count)

@app.route("/register/<role>", methods=['GET', 'POST'])
def register(role):
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone_no = request.form.get("phone_no")

        user = User.query.filter_by(username=username).first()
        if user:
            return "This is username alreay exist."
        
        user = User.query.filter_by(email=email).first()
        if user:
            return "This is email alreay registered another account."
        
        user = User.query.filter_by(phone_no=phone_no).first()
        if user:
            return "This is Phone Number alreay registered another account."
        
        if role == "user":
            new_user = User(username=username, name=name, email=email, password=password, phone_no=phone_no)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        else:
            new_staff = User(username=username, name=name, email=email, password=password, phone_no=phone_no, status="Pending", role="staff")
            db.session.add(new_staff)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html",role=role)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                if user.role == "admin":
                    return redirect("/admin_dashboard")
                elif user.role == "staff":
                    return redirect (f"/staff_dashboard/{user.id}")
                elif user.role == "user":
                    return redirect (f"/user_dashboard/{user.id}")
            else:
                return "Incorrect Password"
        else:
            return "User not found"
    return render_template("login.html")

# ----- admin_dashboard ----- #

@app.route("/admin_dashboard")
def admin_dashboard():
    admin = User.query.get(1)
    trek_count = Trek.query.count()
    user_count = User.query.filter_by(role='user').count()
    staff_count = User.query.filter(User.role=='staff', User.status=='Active').count()
    booking_count = Booking.query.count()
    active_staff = User.query.filter_by(role='staff', status='Active')
    trekkers = User.query.filter_by(role='user')
    active_bookings = Booking.query.filter_by(status="Booked").all()
    treks = Trek.query.filter_by(status="Open")
    return render_template("/admin/admin_dashboard.html", user=admin, trek_count=trek_count, user_count=user_count,
                            staff_count=staff_count, booking_count=booking_count, active_staff=active_staff,
                            trekkers=trekkers, treks=treks, active_bookings=active_bookings)

@app.route("/treks")
def treks():
    treks = Trek.query.all()
    return render_template("/admin/treks.html",treks=treks)

@app.route("/staff")
def staff():
    all_staff = User.query.filter(User.role == 'staff', User.status != 'Pending').all()
    return render_template("/admin/staff.html",all_staff=all_staff)

@app.route("/pending_staff")
def pending_staff():
    all_staff = User.query.filter(User.role == 'staff', User.status == 'Pending').all()
    return render_template("/admin/pending_staff.html",all_staff=all_staff)

@app.route("/users")
def users():
    trekkers = User.query.filter(User.role == 'user').all()
    return render_template("/admin/users.html",trekkers=trekkers)

@app.route("/bookings")
def bookings():
    bookings = Booking.query.filter_by(status="Booked").all()
    return render_template("/admin/bookings.html",bookings=bookings)

# ----- Staff_Dashboard ----- #

@app.route("/staff_dashboard/<int:staff_id>")
def staff_dashboard(staff_id):
    staff = User.query.get(staff_id)
    return render_template("/staff/staff_dashboard.html", staff=staff)

@app.route("/staff_treks/<int:staff_id>")
def staff_treks(staff_id):
    staff = User.query.get(staff_id)
    return render_template("/staff/staff_treks.html", staff=staff)

@app.route("/participants/<int:staff_id>")
def participants(staff_id):
    staff =User.query.get(staff_id)
    return render_template("/staff/participants.html", staff=staff)

# ----- User Dashboard ----- #

@app.route("/user_dashboard/<int:user_id>")
def user_dashboard(user_id):
    user = User.query.get(user_id)
    bookings_count = Booking.query.filter_by(id=user_id).count()
    treks_count = Trek.query.filter_by(status='Open').count()
    staff_count = User.query.filter(User.role=='staff', User.status=='Active').count()
    return render_template("/user/user_dashboard.html", user=user, bookings_count=bookings_count, 
                           treks_count=treks_count, staff_count=staff_count)

@app.route("/user_treks/<int:user_id>")
def user_treks(user_id):
    user = User.query.get(user_id)
    treks = Trek.query.filter_by(status='Open').all()
    return render_template("/user/user_treks.html", user=user, treks=treks)

@app.route("/trek_info/<int:user_id>")
def treks_info(user_id):
    user = User.query.get(user_id)
    treks = Trek.query.filter_by(status='Open').all()
    return render_template("/user/trek_info.html", user=user, treks=treks)

@app.route("/my_bookings/<int:user_id>")
def my_bookings(user_id):
    user = User.query.get(user_id)
    return render_template("/user/my_bookings.html", user=user)

@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get(user_id)
    return render_template("/user/profile.html", user=user)