import click
from flask import current_app
from app import db
from app.models import Event, EventResult, EventStartlist, EventStartlistProvisional, Prediction

@click.command("change-event-id")
@click.argument("old_id", type=int)
@click.argument("new_id", type=int)
def change_event_id(old_id, new_id):
    """Change an Event's ID and update all related tables."""
    app = current_app
    with app.app_context():
        # Check if old event exists
        event = Event.query.get(old_id)
        if not event:
            click.echo(f"Event with id {old_id} does not exist.")
            return

        # Check if new_id is already used
        if Event.query.get(new_id):
            click.echo(f"Event with id {new_id} already exists. Pick a different new_id.")
            return

        click.echo(f"Updating Event ID from {old_id} to {new_id}...")

        # Update Event ID
        event.id = new_id
        db.session.commit()  # commit first to avoid FK conflicts

        # Update all related tables
        EventResult.query.filter_by(event_id=old_id).update({"event_id": new_id})
        EventStartlist.query.filter_by(event_id=old_id).update({"event_id": new_id})
        EventStartlistProvisional.query.filter_by(event_id=old_id).update({"event_id": new_id})
        Prediction.query.filter_by(event_id=old_id).update({"event_id": new_id})

        db.session.commit()
        click.echo("All related tables updated successfully.")
