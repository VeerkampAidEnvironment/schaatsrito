import click
from flask.cli import with_appcontext
from app import db
from app.models import Event
from data.events_static_real import EVENTS

from datetime import datetime

@click.command("seed-events")
@with_appcontext
def seed_events():
    for ev in EVENTS:
        existing = Event.query.get(ev["id"])
        if not existing:
            # Convert start_datetime string to datetime object
            start_dt = ev["start_datetime"]
            if isinstance(start_dt, str):
                start_dt = datetime.fromisoformat(start_dt)  # <-- converts '2026-02-14T16:00:00' to datetime

            event = Event(
                id=ev["id"],
                name=ev["name"],
                discipline=ev["discipline"],
                start_datetime=start_dt,
                gender=ev["gender"],
            )
            db.session.add(event)

    db.session.commit()
    click.echo("Events seeded successfully.")

