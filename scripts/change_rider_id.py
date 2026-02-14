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


@click.command("change-rider-id")
@click.argument("old_id", type=int)
@click.argument("new_id", type=int)
@with_appcontext
def change_rider_id(old_id, new_id):
    """
    Change a rider's ID everywhere in the database.

    Example:
    flask change-rider-id 25 8000
    """

    rider = Rider.query.get(old_id)
    if not rider:
        click.echo(f"❌ Rider with ID {old_id} not found.")
        return

    if Rider.query.get(new_id):
        click.echo(f"❌ Rider ID {new_id} already exists.")
        return

    try:
        # Update foreign key references

        EventStartlist.query.filter_by(rider_id=old_id).update(
            {"rider_id": new_id}
        )

        EventStartlistProvisional.query.filter_by(rider_id=old_id).update(
            {"rider_id": new_id}
        )

        EventResult.query.filter_by(rider_id=old_id).update(
            {"rider_id": new_id}
        )

        # Predictions (3 separate fields)
        Prediction.query.filter_by(rider_1_id=old_id).update(
            {"rider_1_id": new_id}
        )

        Prediction.query.filter_by(rider_2_id=old_id).update(
            {"rider_2_id": new_id}
        )

        Prediction.query.filter_by(rider_3_id=old_id).update(
            {"rider_3_id": new_id}
        )

        # Finally update the Rider primary key
        rider.id = new_id

        db.session.commit()

        click.echo("✅ Rider ID updated successfully everywhere.")

    except Exception as e:
        db.session.rollback()
        click.echo("❌ Error occurred. Rolled back.")
        click.echo(str(e))
