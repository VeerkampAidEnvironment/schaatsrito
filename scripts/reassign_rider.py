import click
from flask.cli import with_appcontext
from app import db
from app.models import (
    Rider,
    EventStartlist,
    EventStartlistProvisional,
    EventResult,
    Prediction,
)


@click.command("reassign-rider")
@click.argument("from_id", type=int)
@click.argument("to_id", type=int)
@with_appcontext
def reassign_rider(from_id, to_id):
    """
    Reassign all references from one rider to another.

    Keeps both Rider records.

    Example:
    flask reassign-rider 8123 8000
    """

    if from_id == to_id:
        click.echo("❌ IDs cannot be the same.")
        return

    from_rider = Rider.query.get(from_id)
    to_rider = Rider.query.get(to_id)

    if not from_rider:
        click.echo(f"❌ Rider {from_id} not found.")
        return

    if not to_rider:
        click.echo(f"❌ Rider {to_id} not found.")
        return

    try:
        # --- STARTLIST ---
        for entry in EventStartlist.query.filter_by(rider_id=from_id).all():
            exists = EventStartlist.query.filter_by(
                event_id=entry.event_id,
                rider_id=to_id
            ).first()

            if not exists:
                entry.rider_id = to_id
            else:
                db.session.delete(entry)

        # --- PROVISIONAL STARTLIST ---
        for entry in EventStartlistProvisional.query.filter_by(rider_id=from_id).all():
            exists = EventStartlistProvisional.query.filter_by(
                event_id=entry.event_id,
                rider_id=to_id
            ).first()

            if not exists:
                entry.rider_id = to_id
            else:
                db.session.delete(entry)

        # --- RESULTS ---
        EventResult.query.filter_by(rider_id=from_id).update(
            {"rider_id": to_id}
        )

        # --- PREDICTIONS ---
        Prediction.query.filter_by(rider_1_id=from_id).update(
            {"rider_1_id": to_id}
        )

        Prediction.query.filter_by(rider_2_id=from_id).update(
            {"rider_2_id": to_id}
        )

        Prediction.query.filter_by(rider_3_id=from_id).update(
            {"rider_3_id": to_id}
        )

        db.session.commit()

        click.echo("✅ All references successfully reassigned.")

    except Exception as e:
        db.session.rollback()
        click.echo("❌ Reassignment failed. Rolled back.")
        click.echo(str(e))
