from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from ..extensions import db
from ..models import Patient, HealthMeasurement

health_bp = Blueprint("health", __name__)

ALLOWED_METRICS = {"heart_rate", "resting_heart_rate", "steps", "calories",
                   "sleep_hours", "spo2", "body_temperature"}


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt().get("role") != role:
                return jsonify(error="Forbidden"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def current_patient():
    return Patient.query.filter_by(user_id=int(get_jwt_identity())).first()


@health_bp.post("/measurements")
@role_required("patient")
def add_measurements():
    """Accepts one measurement or a list: the wearable ingestion endpoint."""
    payload = request.get_json() or {}
    items = payload if isinstance(payload, list) else [payload]
    patient = current_patient()
    saved = 0

    for m in items:
        if m.get("metric_type") not in ALLOWED_METRICS:
            return jsonify(error=f"Unsupported metric: {m.get('metric_type')}"), 400
        try:
            value = float(m["value"])
            recorded_at = datetime.fromisoformat(m["recorded_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError, TypeError, AttributeError):
            return jsonify(error="Each item needs numeric value and ISO recorded_at"), 400

        db.session.add(HealthMeasurement(
            patient_id=patient.id, metric_type=m["metric_type"], value=value,
            unit=m.get("unit", ""), recorded_at=recorded_at, source=m.get("source", "manual")))
        saved += 1

    db.session.commit()
    return jsonify(saved=saved), 201


@health_bp.get("/measurements")
@role_required("patient")
def list_measurements():
    metric = request.args.get("metric")
    days = min(int(request.args.get("days", 7)), 90)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    q = HealthMeasurement.query.filter(
        HealthMeasurement.patient_id == current_patient().id,
        HealthMeasurement.recorded_at >= since)
    if metric:
        q = q.filter_by(metric_type=metric)
    rows = q.order_by(HealthMeasurement.recorded_at).all()
    return jsonify([r.to_dict() for r in rows])