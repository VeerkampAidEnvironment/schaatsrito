from flask_login import login_required, current_user
from flask import render_template
from app.models import Event, Prediction
from datetime import datetime, timedelta
from . import events_bp
import json
import os

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

@events_bp.route("/methods")
def methods_page():
    file_path = "/home/schaatsrito/mysite/data/methods.json"
    full_path = os.path.abspath(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            methods = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        methods = {}
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON at {file_path}")
        methods = {}
    except Exception as e:
        print(f"An unexpected error occurred while opening {file_path}: {e}")
        methods = {}
    return render_template("uitleg.html", methods=methods)

