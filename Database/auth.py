from flask import Blueprint, request, jsonify, session
from Database.models import User
from Database.__init__ import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# Sign Up
@auth.post('/sign-up')
def sign_up():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Account already exists with that email address'}), 400

    new_user = User(email=email, name=username,
                    password=generate_password_hash(password))
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

    return jsonify({'message': 'Login successful', 'username': user.name}), 200

from flask import session, redirect, url_for

@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

