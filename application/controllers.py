from flask import render_template, redirect, request 

from .models import *
from flask import current_app as app

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
            return "<h2>This is username alreay exist.</h2>"
        
        user = User.query.filter_by(email=email).first()
        if user:
            return "<h2>This is email alreay registered another account.</h2>"
        
        user = User.query.filter_by(phone_no=phone_no).first()
        if user:
            return "<h2>This is Phone Number alreay registered another account.</h2>"
        
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
            db.session.commit()
            return redirect("/bookings")
        else:
            return '<h2>Trek is already Completed.</h2>' 
    elif whom == 'trek':
        trek = Trek.query.get(id)
        if action == 'complete':
            trek.status = 'Completed'
            db.session.commit()
        return redirect("/treks")
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

@app.route("/staff_update/<int:detailer_id>/<type>/<int:id>")
def staff_update(detailer_id, type, id):
    if type == 'booking':
        book = Booking.query.get(id)
        if book.status == 'Booked':
            book.status = 'Cancelled'
            db.session.commit()

        return redirect(f"/participants/{id}")
    return redirect(f"/staff_trek/{detailer_id}")

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
            number = request.form.get("phone_no")
            userx = User.query.filter(User.phone_no==number, User.id != user_id).first()
            if userx:
                return "<h2>This Phone No. is already register with another account</h2>"
            else:
                user.name = request.form.get('name')
                user.phone_no = number
        elif 'username' in request.form:
            registered = request.form.get("username")
            usery = User.query.filter(User.username==registered, User.id != user_id).first()
            if usery:
                return "<h2>This username is already register with another account</h2>"
            else:
                current_password = request.form.get('current')
                new_password = request.form.get('updated')
                if current_password == user.password:
                    user.password=new_password
                else:
                    return "<h2>Enter Correct Password</h2>"
        db.session.commit()
        return redirect(f"/profile/{user.id}")
    
    return render_template("/user/profile.html", user=user)

# ----- Search ----- #

@app.route("/search/<int:user_id>/<type>", methods=['GET','POST'])
def search(user_id, type):
    keyword = request.form.get('keyword')
    parameter = request.form.get('parameter')
    user = User.query.get(user_id)

    if type == 'staff':
        if parameter == 'id':
            staff = User.query.get(keyword)
        elif parameter == 'phone_no':
            staff = User.query.filter_by(phone_no=keyword).first()
        elif parameter == 'name':
            staff = User.query.filter_by(name=keyword).first()
        if staff:
            return redirect(f'/details/{user_id}/staff/{staff.id}')
        else:
            return "<h2>No such staff exits</h2>"
    elif type == 'user':
        if parameter == 'id':
            user = User.query.get(keyword)
        elif parameter == 'email':
            user = User.query.filter_by(email=keyword).first()
        elif parameter == 'phone_no':
            user = User.query.filter_by(phone_no=keyword).first()
        elif parameter == 'name':
            user = User.query.filter_by(name=keyword).first()
        if user:
            return redirect(f'/details/{user_id}/user/{user.id}')
        else:
            return "<h2>No such user exits</h2>"
    elif type == 'trek':
        trek = None
        trek_list = None
        if parameter == 'id':
            trek = Trek.query.get(keyword)
        elif parameter == 'name':
            trek = Trek.query.filter_by(trek_name=keyword).first()
        elif parameter == 'location':
            trek_list = Trek.query.filter_by(location=keyword).all()
        elif parameter == 'difficulty':
            trek_list = Trek.query.filter_by(difficulty=keyword).all()
        elif parameter == 'status':
            trek_list = Trek.query.filter_by(status=keyword).all()
        if trek:
            return redirect(f'/details/{user_id}/trek/{trek.id}')
        elif trek_list:
            return render_template("search_trek.html", trek_list=trek_list, parameter=parameter, keyword=keyword, user_id=user_id)
        else:
            return "<h2>No such trek exits</h2>"

    # ----- Statistics ----- #

@app.route("/statistics")
def statistics():
    all_treks = Trek.query.all()
    x_axis = [trek.trek_name for trek in all_treks]
    y_axis = [len(trek.bookings) for trek in all_treks]
    plt.bar(x_axis,y_axis)
    plt.xlabel("Treks Names --->")
    plt.ylabel("No. of Bookings --->")
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    plt.savefig('static/bar.png')
    plt.close()

    easy = 0
    moderate = 0
    hard = 0
    for trek in all_treks:
        if trek.difficulty == 'Easy':
            easy += len(trek.bookings)
        elif trek.difficulty == 'Moderate':
            moderate += len(trek.bookings)
        elif trek.difficulty == 'Hard':
            hard += len(trek.bookings)
    labels = ["Easy", "Moderate", "Hard"]
    sizes = [easy,moderate,hard]
    plt.pie(sizes,labels=labels)
    plt.title("No. of Bookings based on difficulty")
    plt.savefig("static/pie.png")
    plt.close()
    return render_template('admin/statistics.html')