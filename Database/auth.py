from flask import Blueprint, request, jsonify, session
from Database.models import User
from Database.models import Company
from Database.__init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth = Blueprint('auth', __name__)

# Sign Up
@auth.post('/sign-up')
def sign_up():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    number = data.get('number')
    password = data.get('password')
    gender = data.get('gender')
    company = data.get('companyName')
    dob_str = data.get('dob')  
    dob_obj = datetime.strptime(dob_str, '%Y-%m-%d').date()

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Account already exists with that email address'}), 400

    new_user = User(email=email, name=username, number=number, dob = dob_obj, gender = gender,
                    password=generate_password_hash(password))
    if company:
        new_company = Company(name = company)
        db.session.add(new_company)
        db.session.commit()

    db.session.add(new_user)
    db.session.commit()

    # Log the user in after signup
    session['user_id'] = new_user.id
    session['username'] = new_user.name

    return jsonify({'message': 'Account Created!', 'username': new_user.name}), 201

# Login
@auth.post('/login')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    session['user_id'] = user.id
    session['username'] = user.name
    session['email'] = user.email



    return jsonify({'message': 'Login successful', 'username': user.name}), 200

from flask import session, redirect, url_for

@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

