from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    specialty = db.Column(db.String(120))


class HealthMeasurement(db.Model):
    __tablename__ = "health_measurements"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    metric_type = db.Column(db.String(50), nullable=False)  # heart_rate, steps, spo2...
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    recorded_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    source = db.Column(db.String(50), default="manual")  # manual, simulator, apple_health...

    def to_dict(self):
        return {
            "id": self.id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "recorded_at": self.recorded_at.isoformat(),
            "source": self.source,
        }