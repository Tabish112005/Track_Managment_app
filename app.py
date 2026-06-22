import os
from flask import Flask
from models.models import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///terking.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)

with app.app_context():
    db.create_all()

    admin_exists = User.query.filter_by(role="Admin").first()
    if not admin_exists:
        admin_user = User(
            username="admin",
            email="admin123@gamil.com",
            password_hash="admin123",
            role="Admin"
        )
        db.session.add(admin_user)
        db.session.comit()
        print("Database created")

@app.route('/')
def home():
    return "hello world"

if __name__ == '__main__':
    app.run(debug=True)