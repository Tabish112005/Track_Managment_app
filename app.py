from flask import Flask
from application.database import db

app = None 

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///treking-database.sqlite3'
    db.init_app(app)
    app.app_context().push()
    return app 

app = create_app()

from application.controllers import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username="admin").first()
        if admin is None:
            admin = User(username="admin", name="Admin", email="admin123@gmail.com", password="admin123", role="admin")
            db.session.add(admin)
            db.session.commit()
    app.run() 