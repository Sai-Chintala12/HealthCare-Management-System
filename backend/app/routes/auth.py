from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, Patient, Doctor

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    name, email = data.get("name"), (data.get("email") or "").lower()
    password, role = data.get("password"), data.get("role")

    if not all([name, email, password]) or role not in ("patient", "doctor"):
        return jsonify(error="name, email, password and role (patient/doctor) required"), 400
    if len(password) < 8:
        return jsonify(error="Password must be at least 8 characters"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # get user.id

    if role == "patient":
        db.session.add(Patient(user_id=user.id))
    else:
        db.session.add(Doctor(user_id=user.id, specialty=data.get("specialty")))
    db.session.commit()
    return jsonify(message="Registered"), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=(data.get("email") or "").lower()).first()
    if not user or not user.check_password(data.get("password") or ""):
        return jsonify(error="Invalid credentials"), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(token=token, user={"id": user.id, "name": user.name, "role": user.role})


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    return jsonify(id=user.id, name=user.name, email=user.email, role=user.role)