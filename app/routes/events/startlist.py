from flask import current_app, jsonify
from flask_login import login_required
from app.models import Event, Rider, EventStartlist
from app import db
import requests
from . import events_bp

@events_bp.route("/events/<int:event_id>/load-startlist", methods=["POST"])
@login_required
def load_startlist(event_id):
    event = Event.query.get_or_404(event_id)
    event_code = current_app.config["EVENT_CODE"]

    # If startlist already exists
    if event.startlist:
        return jsonify({"status": "already_loaded"})

    # Build API URL for competition-specific startlist
    api_url = f"https://api.isuresults.eu/events/2026_{event_code}/competitions/{event.id}/start-list/"

    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return jsonify({"status": "not_available", "error": str(e)})

    added = 0
    for entry in data:
        competitor = entry.get("competitor")
        if not competitor:
            continue
        skater = competitor.get("skater")
        if not skater:
            continue

        # Match Rider by skater ID
        rider = Rider.query.get(skater["id"])
        if not rider:
            # Optionally, create rider if missing in DB
            rider = Rider(
                id=skater["id"],
                name=f'{skater["firstName"]} {skater["lastName"]}',
                country=skater.get("country"),
                gender=skater.get("gender"),
                profile=None,
                photo=skater.get("photo")
            )
            db.session.add(rider)
            db.session.flush()  # get rider.id without committing

        # Check if startlist entry exists
        exists = EventStartlist.query.filter_by(event_id=event.id, rider_id=rider.id).first()
        if exists:
            continue

        db.session.add(EventStartlist(event_id=event.id, rider_id=rider.id))
        added += 1

    if added > 0:
        db.session.commit()
        return jsonify({"status": "loaded", "added": added})

    return jsonify({"status": "not_available"})
