# app/events/results.py

from flask import current_app, jsonify
from flask_login import login_required
from app.models import Event, Rider, EventResult
from app import db
from . import events_bp
import requests

@events_bp.route("/events/<int:event_id>/load-results", methods=["POST"])
@login_required
def load_results(event_id):
    event = Event.query.get_or_404(event_id)
    if event.results:
        return jsonify({"status": "already_loaded"})

    event_code = current_app.config["EVENT_CODE"]
    api_url = f"https://api.isuresults.eu/events/2026_{event_code}/competitions/{event_id}/results/"

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return jsonify({"status": "not_available"})

    if not data:
        return jsonify({"status": "not_available"})

    # Remove existing results for idempotency
    EventResult.query.filter_by(event_id=event.id).delete()

    added = 0
    position = 1

    # Sort competitors by rank (just in case)
    sorted_competitors = sorted(data, key=lambda x: x.get("rank", 9999))

    for entry in sorted_competitors:
        skater = entry.get("competitor", {}).get("skater")
        if not skater:
            continue

        rider = Rider.query.get(skater["id"])
        if not rider:
            continue

        # Convert time string to float
        time_str = entry.get("time")
        try:
            end_time = float(time_str) if time_str else None
        except ValueError:
            end_time = None

        db.session.add(
            EventResult(
                event_id=event.id,
                rider_id=rider.id,
                position=position,
                end_time=end_time,
            )
        )

        added += 1
        position += 1

    if added > 0:
        db.session.commit()
        return jsonify({"status": "loaded"})

    return jsonify({"status": "not_available"})
