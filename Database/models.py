from Database.__init__ import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    number = db.Column(db.String(15), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(200), nullable=False)

 
