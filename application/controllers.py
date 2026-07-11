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
    active_staff = User.query.filter(User.role=='staff', User.status=='Active')
    trekkers = User.query.filter_by(role='user')
    active_bookings = Booking.query.filter_by(status="Booked").all()
    treks = Trek.query.filter_by(status="Open")
    return render_template("/admin/admin_dashboard.html", user=admin, trek_count=trek_count, user_count=user_count,
                            staff_count=staff_count, booking_count=booking_count, active_staff=active_staff,
                            trekkers=trekkers, treks=treks, active_bookings=active_bookings)

@app.route("/admin_update/<whom>/<action>/<int:id>")
def admin_update(whom,action,id):
    if whom == 'staff':
        staff = User.query.get(id)
        if action == 'approve' or action == 'whitelist':
            staff.status = 'Active'
        else:
            staff.status = 'Blacklisted'
        db.session.commit()
        return redirect("/staff")
    elif whom == 'user':
        user = User.query.get(id)
        if action == 'blacklist':
            user.status = 'Blacklisted'
        elif action == 'whitelist':
            user.status = 'Active'
        db.session.commit()
        return redirect("/users")
    elif whom == 'booking':
        book = Booking.query.get(id)
        if action == 'cancel':
            book.status = 'Cancelled'
        if action == 'complete':
            book.status = 'Completed'
        db.session.commit()
        return redirect("/bookings")
    return redirect("/admin_dashboard")

@app.route("/details/<detailer_id>/<type>/<id>")
def details(detailer_id,type,id):
    detailer = User.query.get(detailer_id)
    if type == 'user':
        user = User.query.get(id)
        return render_template("user_details.html", user=user, detailer=detailer)
    if type == 'staff':
        staff = User.query.get(id)
        return render_template("user_details.html", user=staff, detailer=detailer)
    if type == 'trek':
        trek = Trek.query.get(id)
        return render_template("trek_detail.html", trek=trek, detailer=detailer)
    return "Error"

@app.route("/close_trek/<int:detailer_id>/<int:trek_id>")
def close_trek(detailer_id,trek_id):
    trek = Trek.query.get(trek_id)
    trek.status = 'Closed'
    db.session.commit()
    return redirect(f"/details/{detailer_id}/trek/{trek.id}")

@app.route("/open_trek/<int:detailer_id>/<int:trek_id>")
def open_trek(detailer_id,trek_id):
    trek = Trek.query.get(trek_id)
    trek.status = 'Open'
    db.session.commit()
    return redirect(f"/details/{detailer_id}/trek/{trek.id}")

@app.route("/booking/<int:booker_id>/<int:trek_id>")
def booking(booker_id, trek_id):
    book = Booking.query.filter_by(user_id=booker_id, trek_id=trek_id).first()
    if book:
        return "<h2>You already booked this trek !!</h2>"
    trek = Trek.query.get(trek_id)
    if trek.available_slots > 0:
        book = Booking(user_id=booker_id, trek_id=trek_id)
        trek.available_slots -= 1
        db.session.add(book)
        db.session.commit()
        return "<h2>Booking conformed</h2>"
    else:
        return "<h2>Oops! All slots are are already Booked.</h2>"
    
@app.route("/assign_staff/<int:trek_id>", methods=['GET', 'POST'])
def assign_staff(trek_id):
    trek = Trek.query.get(trek_id)
    available_staff = User.query.filter_by(role='staff', status='Active').all()
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        trek.staff_id = staff_id
        db.session.commit()
        return redirect(f"/details/1/trek/{trek_id}")
    return render_template("/admin/assign_staff.html", available_staff=available_staff, trek=trek)


# ----- Create Trek ----- #

@app.route("/create_trek", methods=['GET', 'POST'])
def create_trek():
    if request.method == 'POST':
        trek_name = request.form.get('trek_name')
        location = request.form.get('location')
        image = request.form.get('image')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        available_slots = request.form.get('available_slots')
        status = request.form.get('status')
        start_date = date.fromisoformat(request.form.get('start_date'))
        end_date = date.fromisoformat(request.form.get('end_date'))
        description = request.form.get('description')
        new_trek = Trek(trek_name=trek_name, location=location, image=image, difficulty=difficulty, duration=duration, status=status,
                        available_slots=available_slots, start_date=start_date, end_date=end_date, description=description)
        db.session.add(new_trek)
        db.session.commit()
    return render_template("/admin/create_trek.html")

@app.route("/update_trek/<int:updater_id>/<int:trek_id>", methods=['GET', 'POST'])
def update_trek(updater_id,trek_id):
    trek = Trek.query.get(trek_id)
    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name')
        trek.location = request.form.get('location')
        trek.image = request.form.get('image')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = request.form.get('duration')
        trek.available_slots = request.form.get('available_slots')
        trek.status = request.form.get('status')
        trek.start_date = date.fromisoformat(request.form.get('start_date'))
        trek.end_date = date.fromisoformat(request.form.get('end_date'))
        trek.description = request.form.get('description')
        db.session.commit()
        return redirect(f"/details/{updater_id}/trek/{trek_id}")
    return render_template("/update_trek.html", trek=trek, updater_id=updater_id)

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
    user = User.query.filter_by(role='user').all()
    staff = User.query.filter_by(role='staff').all()
    bookings = Booking.query.all()
    return render_template("/admin/bookings.html", bookings=bookings, user=user, staff=staff)


# ----- Staff_Dashboard ----- #

@app.route("/staff_dashboard/<int:staff_id>")
def staff_dashboard(staff_id):
    staff = User.query.get(staff_id)
    participants = sum(len([b for b in trek.bookings if b.status == 'Booked']) for trek in staff.assigned_trek)
    return render_template("/staff/staff_dashboard.html", staff=staff, participants=participants)

@app.route("/staff_treks/<int:staff_id>")
def staff_treks(staff_id):
    staff = User.query.get(staff_id)
    return render_template("/staff/staff_treks.html", staff=staff)

@app.route("/participants/<int:staff_id>")
def participants(staff_id):
    staff =User.query.get(staff_id)
    trek = Trek.query.filter_by(staff_id=staff_id).all()
    return render_template("/staff/participants.html", staff=staff, trek=trek)



# ----- User Dashboard ----- #

@app.route("/user_dashboard/<int:user_id>")
def user_dashboard(user_id):
    user = User.query.get(user_id)
    bookings_count = Booking.query.filter_by(user_id=user_id).count()
    treks_count = Trek.query.filter_by(status='Open').count()
    staff_count = User.query.filter(User.role=='staff', User.status=='Active').count()
    return render_template("/user/user_dashboard.html", user=user, bookings_count=bookings_count, 
                           treks_count=treks_count, staff_count=staff_count)

@app.route("/user_treks/<int:user_id>")
def user_treks(user_id):
    user = User.query.get(user_id)
    treks = Trek.query.all()
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

@app.route("/profile/<int:user_id>", methods=['GET', 'POST'])
def profile(user_id):
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        if 'name' in request.form:
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            user.phone_no = request.form.get('phone_no')
        elif 'current' in request.form:
            current_password = request.form.get('current')
            new_password = request.form.get('updated')
            if current_password == user.password:
                user.password=new_password
            else:
                return "<h2>Enter Correct Password</h2>"
        db.session.commit()
        return redirect(f"/profile/{user.id}")
    
    return render_template("/user/profile.html", user=user)
