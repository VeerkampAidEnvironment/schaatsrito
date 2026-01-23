from flask import current_app
from flask_login import login_required
from flask import jsonify
from app.models import Event, Rider, EventStartlist
from app import db
from . import events_bp
from scripts.seed_startlists import scrape_startlist

@events_bp.route("/events/<int:event_id>/load-startlist", methods=["POST"])
@login_required
def load_startlist(event_id):
    event = Event.query.get_or_404(event_id)
    event_code = current_app.config["EVENT_CODE"]

    if event.startlist:
        return jsonify({"status": "already_loaded"})

    from scripts.normalize import normalize_name
    try:
        names = scrape_startlist(event_code, event.id)
    except Exception:
        return jsonify({"status": "not_available"})

    added = 0
    for name in names:
        rider = Rider.query.filter_by(name=name).first()
        if not rider:
            continue
        exists = EventStartlist.query.filter_by(event_id=event.id, rider_id=rider.id).first()
        if exists:
            continue
        db.session.add(EventStartlist(event_id=event.id, rider_id=rider.id))
        added += 1

    if added > 0:
        db.session.commit()
        return jsonify({"status": "loaded"})

    return jsonify({"status": "not_available"})
