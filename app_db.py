from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User (Job Seeker)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    resume_link = db.Column(db.String(255))
    applications = db.relationship('Application', backref='user', lazy=True)
    skills = db.relationship('UserSkill', back_populates='user')

# Company
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)
    jobs = db.relationship('Job', backref='company', lazy=True)

# Job Posting
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    location = db.Column(db.String(120))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    applications = db.relationship('Application', backref='job', lazy=True)
    skills = db.relationship('JobSkill', back_populates='job')

# Application
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected

# Skill
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('UserSkill', back_populates='skill')
    jobs = db.relationship('JobSkill', back_populates='skill')

# Linking Table: UserSkill
class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    user = db.relationship('User', back_populates='skills')
    skill = db.relationship('Skill', back_populates='users')

# Linking Table: JobSkill
class JobSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    job = db.relationship('Job', back_populates='skills')
    skill = db.relationship('Skill', back_populates='jobs')
