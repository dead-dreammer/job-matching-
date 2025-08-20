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

    # Relationships
    informal_jobs = db.relationship("InformalJob", back_populates="creator")
    formal_jobs = db.relationship("FormalJob", back_populates="creator")


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    # One company → many jobs
    jobs = db.relationship("FormalJob", back_populates="company")


class InformalJob(db.Model):
    __tablename__ = "informal_job"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    pay_rate = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User", back_populates="informal_jobs")


class FormalJob(db.Model):
    __tablename__ = "formal_job"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    job_field = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    requirements = db.Column(db.Text)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=True)
    company = db.relationship("Company", back_populates="jobs")

    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User", back_populates="formal_jobs")
