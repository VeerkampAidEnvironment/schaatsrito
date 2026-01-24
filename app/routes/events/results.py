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

    # Block if event is final
    if getattr(event, "final", False):
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

    added = 0
    position = 1

    for entry in data:
        skater = entry.get("competitor", {}).get("skater")
        if not skater:
            continue

        rider = Rider.query.get(skater["id"])
        if not rider:
            continue

        # Store time exactly as received
        formatted_time = entry.get("time")

        # Check existing result
        existing_result = EventResult.query.filter_by(event_id=event.id, rider_id=rider.id).first()
        if existing_result:
            existing_result.position = position
            existing_result.end_time = formatted_time
        else:
            db.session.add(
                EventResult(
                    event_id=event.id,
                    rider_id=rider.id,
                    position=position,
                    end_time=formatted_time,
                )
            )

        added += 1
        position += 1

    db.session.commit()

    # Mark event final if all competitors have results
    if added == len(data):
        event.final = True
        db.session.commit()
        return jsonify({"status": "loaded_final"})

    return jsonify({"status": "loaded_partial"})
