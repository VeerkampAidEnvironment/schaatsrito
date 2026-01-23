from flask import current_app, jsonify
from flask_login import login_required
from app.models import Event, Rider, EventResult
from app import db
from . import events_bp
from scripts.seed_results import scrape_results
from scripts.normalize import normalize_name

@events_bp.route("/events/<int:event_id>/load-results", methods=["POST"])
@login_required
def load_results(event_id):
    event = Event.query.get_or_404(event_id)
    if event.results:
        return jsonify({"status": "already_loaded"})

    event_code = current_app.config["EVENT_CODE"]

    try:
        names = scrape_results(event_code, event.id)
    except Exception:
        return jsonify({"status": "not_available"})

    if not names:
        return jsonify({"status": "not_available"})

    EventResult.query.filter_by(event_id=event.id).delete()
    added = 0
    position = 1

    for name in names:
        rider = Rider.query.filter_by(name=name).first()
        if not rider:
            continue
        db.session.add(EventResult(event_id=event.id, rider_id=rider.id, position=position))
        added += 1
        position += 1

    if added > 0:
        db.session.commit()
        return jsonify({"status": "loaded"})

    return jsonify({"status": "not_available"})
