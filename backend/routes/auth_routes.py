from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token
)
import re

from models.user import User
from extensions import db

auth_bp = Blueprint("auth", __name__)

# ── SIGNUP ─────────────────────────────

@auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    #  Username Validation
    if not username or len(username) < 3:
        return jsonify({
            "success": False,
            "message": "Username must be at least 3 characters"
        }), 400
    # mail Validation
    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not email or not re.match(email_pattern, email):
        return jsonify({
            "success": False,
            "message": "Invalid email"
        }), 400
    # Password Validation
    if not password or len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters"
        }), 400
    
    existing = User.query.filter(
        (User.email == email) |
        (User.username == username)
    ).first()

    if existing:
        return jsonify({
            "success": False,
            "message": "User already exists"
        }), 400

    user = User(
        username=username,
        email=email
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    })


# ── LOGIN ─────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(
        email=email
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401

    token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    })