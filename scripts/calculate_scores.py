# scripts/update_scores.py
import click
from flask import current_app
from app import db
from app.models import Prediction, EventResult

def score_rider_1(position):
    if position == 1:
        return 3
    elif position in (2, 3):
        return 1
    return 0

def score_rider_2_or_3(position):
    if position in (1, 2, 3):
        return 1
    return 0


def update_scores_for_event(event_id):
    predictions = Prediction.query.filter_by(event_id=event_id).all()
    results = {
        res.rider_id: res.position
        for res in EventResult.query.filter_by(event_id=event_id).all()
    }

    for pred in predictions:
        r1_pos = results.get(pred.rider_1_id)
        r2_pos = results.get(pred.rider_2_id)
        r3_pos = results.get(pred.rider_3_id)

        pred.rider_1_score = score_rider_1(r1_pos)
        pred.rider_2_score = score_rider_2_or_3(r2_pos)
        pred.rider_3_score = score_rider_2_or_3(r3_pos)

        pred.score = (
            pred.rider_1_score
            + pred.rider_2_score
            + pred.rider_3_score
        )

        db.session.add(pred)

    db.session.commit()
    print(f"Scores updated for {len(predictions)} predictions of event {event_id}.")


@click.command("update-scores")
@click.argument("event_id", type=int)
def update_scores_command(event_id):
    """Update prediction scores for a given EVENT_ID"""
    update_scores_for_event(event_id)
