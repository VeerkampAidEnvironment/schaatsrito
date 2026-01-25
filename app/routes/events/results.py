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
    if getattr(event, "results_final", False):
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

    for entry in data:
        position = entry.get("rank")
        if position == None:
            position = 999
        formatted_time = entry.get("time")
        if entry.get("type") == "team":
            country_id = entry.get("id")
            # Store time exactly as received
            formatted_time = entry.get("time")

            # Check existing result
            existing_result = EventResult.query.filter_by(event_id=event.id, rider_id=country_id).first()
            if existing_result:
                existing_result.position = position
                existing_result.end_time = formatted_time
            else:
                db.session.add(
                    EventResult(
                        event_id=event.id,
                        rider_id=country_id,
                        position=position,
                        end_time=formatted_time,
                    )
                )
        else:
            skater = entry.get("competitor", {}).get("skater")
            if not skater:
                continue
            position = entry.get("rank")
            if position == None:
                position = 999
            rider = Rider.query.get(skater["id"])
            if not rider:
                continue

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

    db.session.commit()

    if data[-1].get("status") is not None:
        if data[0]['type'] == 'ms':
            if data[0]['laps'][15]['sprintPoints'] == 60:
                event.results_final = True
                db.session.commit()
                return jsonify({"status": "loaded_final"})
            else:
                return jsonify({"status": "loaded_partial"})
        else:
            event.results_final = True
            db.session.commit()
            return jsonify({"status": "loaded_final"})
    else:
        return jsonify({"status": "loaded_partial"})
