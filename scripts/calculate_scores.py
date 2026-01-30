# scripts/update_scores.py
import click
from collections import Counter
from app import db
from app.models import Prediction, EventResult

BASE_SCORES = {
    1: 100,
    2: 75,
    3: 55,
    4: 40,
    5: 30,
    6: 20,
    7: 10,
    8: 5,
}

POSITION_MULTIPLIERS = {
    1: 2.0,    # captain
    2: 1.5,    # second
    3: 1.0,    # third
}


def get_base_score(position):
    return BASE_SCORES.get(position, 0)


def get_popularity_multiplier(rider_id, rider_counts, total_predictions):
    count = rider_counts.get(rider_id, 0)

    if count == 1:
        return 2.0

    percentage = count / total_predictions

    if percentage < 0.25:
        return 1.25
    elif percentage < 0.50:
        return 1.10
    else:
        return 1.0


def update_scores_for_event(event_id):
    predictions = Prediction.query.filter_by(event_id=event_id).all()
    total_predictions = len(predictions)

    if total_predictions == 0:
        print("No predictions found.")
        return

    # Result positions
    results = {
        res.rider_id: res.position
        for res in EventResult.query.filter_by(event_id=event_id).all()
    }

    # Count rider popularity
    rider_counts = Counter()
    for p in predictions:
        rider_counts[p.rider_1_id] += 1
        rider_counts[p.rider_2_id] += 1
        rider_counts[p.rider_3_id] += 1

    for pred in predictions:
        total_score = 0

        for idx, rider_id in enumerate(
            [pred.rider_1_id, pred.rider_2_id, pred.rider_3_id],
            start=1
        ):
            position = results.get(rider_id)

            base_score = get_base_score(position)
            captain_multiplier = POSITION_MULTIPLIERS[idx]
            rarity_multiplier = get_popularity_multiplier(
                rider_id, rider_counts, total_predictions
            )

            final_score = int(
                round(base_score * captain_multiplier * rarity_multiplier)
            )

            # Save subscores
            if idx == 1:
                pred.rider_1_base = base_score
                pred.rider_1_captain = captain_multiplier
                pred.rider_1_rarity = rarity_multiplier
                pred.rider_1_score = final_score

            elif idx == 2:
                pred.rider_2_base = base_score
                pred.rider_2_captain = captain_multiplier
                pred.rider_2_rarity = rarity_multiplier
                pred.rider_2_score = final_score

            else:
                pred.rider_3_base = base_score
                pred.rider_3_captain = captain_multiplier
                pred.rider_3_rarity = rarity_multiplier
                pred.rider_3_score = final_score

            total_score += final_score

        pred.score = total_score
        db.session.add(pred)

    db.session.commit()
    print(f"Scores updated for {total_predictions} predictions of event {event_id}.")
