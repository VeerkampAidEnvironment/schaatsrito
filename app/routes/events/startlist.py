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

    if event.startlist:
        return jsonify({"status": "already_loaded"})

    api_url = f"https://api.isuresults.eu/events/2026_{event_code}/competitions/{event.id}/start-list/"
    try:
        resp = requests.get(api_url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return jsonify({"status": "not_available", "error": str(e)})

    added = 0

    for entry in data:
        if entry.get("type") in ("ind", "ms"):
            # Individual event: same as before
            competitor = entry.get("competitor")
            if not competitor or not competitor.get("skater"):
                continue
            skater = competitor["skater"]

            rider = Rider.query.get(skater["id"])
            if not rider:
                rider = Rider(
                    id=skater["id"],
                    name=f'{skater["firstName"]} {skater["lastName"]}',
                    country=skater.get("country"),
                    gender=skater.get("gender"),
                    profile=None,
                    photo=skater.get("photo")
                )
                db.session.add(rider)
                db.session.flush()

            if not EventStartlist.query.filter_by(event_id=event.id, rider_id=rider.id).first():
                db.session.add(EventStartlist(event_id=event.id, rider_id=rider.id))
                added += 1

        elif entry.get("type") == "team":
            # Team event: just create a Rider using the team name
            team = entry.get("team")
            if not team or not team.get("name"):
                continue
            team_name = team["name"]
            # Check if this team already exists as a Rider
            rider = Rider.query.filter_by(name=team_name).first()
            if not rider:
                rider = Rider(
                    name=team_name,
                    country=team.get("country"),
                    gender=team.get("gender"),
                    profile=None,
                    photo=None,
                    id=int(entry.get("id"))
                )
                db.session.add(rider)
                db.session.flush()

            if not EventStartlist.query.filter_by(event_id=event.id, rider_id=rider.id).first():
                db.session.add(EventStartlist(event_id=event.id, rider_id=rider.id))
                added += 1

    if added > 0:
        db.session.commit()
        return jsonify({"status": "loaded", "added": added})

    return jsonify({"status": "not_available"})
