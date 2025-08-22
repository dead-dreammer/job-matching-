from flask import Blueprint, request, jsonify, session
from Database.models import User, Company
from Database.__init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth = Blueprint('auth', __name__)

# -------------------------
# SIGN UP
# -------------------------
@auth.post('/sign-up')
def sign_up():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    number = data.get('number')
    password = data.get('password')
    gender = data.get('gender')
    company_name = data.get('companyName')
    dob_str = data.get('dob')

    # Parse date of birth
    dob_obj = None
    if dob_str:
        dob_obj = datetime.strptime(dob_str, '%Y-%m-%d').date()

    # Prevent duplicate emails
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Account already exists with that email address'}), 400

    # Create new user
    new_user = User(
        email=email,
        name=username,
        number=number,
        dob=dob_obj,
        gender=gender,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()  # commit so new_user.id is available

    # Handle company
    company_obj = None
    if company_name:
        company_obj = Company.query.filter_by(name=company_name).first()
        if not company_obj:
            company_obj = Company(name=company_name)
            db.session.add(company_obj)
            db.session.commit()

    # Store session
    # Store session
    session['user_id'] = new_user.id
    session['username'] = new_user.name
    session['email'] = new_user.email
    session['number'] = new_user.number   # add this

    # calculate and store age
    if new_user.dob:
        today = datetime.today().date()
        age = today.year - new_user.dob.year - ((today.month, today.day) < (new_user.dob.month, new_user.dob.day))
        session['age'] = age
    else:
        session['age'] = None

    session['company_id'] = company_obj.id if company_obj else None
    session['company_name'] = company_obj.name if company_obj else None


    return jsonify({'message': 'Account Created!', 'username': new_user.name}), 201


# -------------------------
# LOGIN
# -------------------------
@auth.post('/login')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Try to find the company linked to this user
    # Assumes a user can have a company via formal jobs
    company = None
    if hasattr(user, 'formal_jobs') and user.formal_jobs:
        company = user.formal_jobs[0].company

    session['user_id'] = user.id
    session['username'] = user.name
    session['email'] = user.email
    session['number'] = user.number
    from datetime import date
 
    if user.dob:
        today = date.today()
        age = today.year - user.dob.year - ((today.month, today.day) < (user.dob.month, user.dob.day))
        session['age'] = age
    else:
        session['age'] = None

    session['company_id'] = company.id if company else None
    session['company_name'] = company.name if company else None

    return jsonify({'message': 'Login successful', 'username': user.name}), 200


# -------------------------
# LOGOUT
# -------------------------
@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})
