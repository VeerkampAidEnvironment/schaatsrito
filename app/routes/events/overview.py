from flask_login import login_required, current_user
from flask import render_template
from app.models import Event, Prediction
from datetime import datetime, timedelta
from . import events_bp
import json


@events_bp.route("/events")
@login_required
def events_overview():
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=-159)
    events = Event.query.order_by(Event.start_datetime).all()
    user_predictions = {p.event_id for p in Prediction.query.filter_by(user_id=current_user.id)}

    return render_template(
        "events/overview.html",
        events=events,
        user_predictions=user_predictions,
        now=now
    )

@events_bp.route("/methods")
def methods_page():
    with open("data/methods.json", "r", encoding="utf-8") as f:
        methods = json.load(f)
    return render_template("uitleg.html", methods=methods)
