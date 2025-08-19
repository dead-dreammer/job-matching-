from Database.__init__ import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    number = db.Column(db.String(15), nullable=True)  # Added phone number field
    dob = db.Column(db.Date, nullable=True)  # Date of birth field
    gender = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(200))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    jobs = db.relationship('FormalJob', back_populates='company')

from datetime import datetime

class InformalJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    pay_rate = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to employer user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FormalJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    salary = db.Column(db.Float)
    job_field = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    requirements = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    company = db.relationship('Company', backref='formal_jobs')


