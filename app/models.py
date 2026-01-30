from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    predictions = db.relationship("Prediction", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Rider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    country = db.Column(db.String(3), nullable=True)
    profile = db.Column(db.String(64), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    photo = db.Column(db.String(255))  # <-- NEW: photo URL


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    discipline = db.Column(db.String(64))
    start_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    gender = db.Column(db.String(16))
    startlist = db.relationship("EventStartlist", backref="event", lazy=True)
    results = db.relationship("EventResult", backref="event", lazy=True)
    predictions = db.relationship("Prediction", backref="event", lazy=True)
    results_final = db.Column(db.Boolean, default=False)


class EventStartlist(db.Model):
    __tablename__ = "event_startlist"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey("rider.id"), nullable=False)

    rider = db.relationship(
        "Rider",
        backref=db.backref("event_entries", lazy=True)
    )

class EventResult(db.Model):
    __tablename__ = "event_result"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey("rider.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.String(20))  # <-- change from Float to String
    laps = db.Column(JSON, nullable=True)  # <-- here

    rider = db.relationship(
        "Rider",
        backref=db.backref("results", lazy=True)
    )


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    rider_1_id = db.Column(db.Integer, db.ForeignKey("rider.id"), nullable=False)
    rider_2_id = db.Column(db.Integer, db.ForeignKey("rider.id"), nullable=False)
    rider_3_id = db.Column(db.Integer, db.ForeignKey("rider.id"), nullable=False)

    score = db.Column(db.Integer, default=0)
    # rider 1
    rider_1_base = db.Column(db.Integer, default=0)
    rider_1_captain = db.Column(db.Float, default=1.0)
    rider_1_rarity = db.Column(db.Float, default=1.0)
    rider_1_score = db.Column(db.Integer, default=0)

    # rider 2
    rider_2_base = db.Column(db.Integer, default=0)
    rider_2_captain = db.Column(db.Float, default=1.0)
    rider_2_rarity = db.Column(db.Float, default=1.0)
    rider_2_score = db.Column(db.Integer, default=0)

    # rider 3
    rider_3_base = db.Column(db.Integer, default=0)
    rider_3_captain = db.Column(db.Float, default=1.0)
    rider_3_rarity = db.Column(db.Float, default=1.0)
    rider_3_score = db.Column(db.Integer, default=0)

    rider_1 = db.relationship("Rider", foreign_keys=[rider_1_id])
    rider_2 = db.relationship("Rider", foreign_keys=[rider_2_id])
    rider_3 = db.relationship("Rider", foreign_keys=[rider_3_id])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
