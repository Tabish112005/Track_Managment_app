from flask import render_template, redirect, request 

from .models import *
from flask import current_app as app

@app.route("/")
def home():
    return render_template("index.html")

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
                    return "admin route"
                elif user.role == "staff":
                    return "staff dash"
                elif user.role == "user":
                    return "user route"
            else:
                return "Incorrect Password"
        else:
            return "User not found"
    return render_template("login.html")