from flask_login import login_required, current_user
from flask import render_template
from app.models import Event, Prediction
from datetime import datetime, timedelta
from . import events_bp



@events_bp.route("/events")
@login_required
def events_overview():
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=1)
    events = Event.query.order_by(Event.start_datetime).all()
    user_predictions = {p.event_id for p in Prediction.query.filter_by(user_id=current_user.id)}

    return render_template(
        "events/overview.html",
        events=events,
        user_predictions=user_predictions,
        now=now
    )
