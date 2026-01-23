from flask import render_template
from flask_login import login_required, current_user
from app.models import User, Event, Prediction, EventResult
from app import db
from sqlalchemy import func
from . import leaderboard_bp
from datetime import datetime


@leaderboard_bp.route("/leaderboard")
@login_required
def leaderboard():
    now = datetime.utcnow()

    # Get user scores
    user_scores = (
        db.session.query(
            User.id,
            User.username,
            func.coalesce(func.sum(Prediction.score), 0).label("total_score")
        )
        .outerjoin(Prediction, Prediction.user_id == User.id)
        .group_by(User.id)
        .order_by(func.sum(Prediction.score).desc())
        .all()
    )

    events = Event.query.order_by(Event.start_datetime).all()

    user_event_scores = {}
    score_details = {}

    for user in user_scores:
        user_event_scores[user.id] = {}
        score_details[user.id] = {}
        for event in events:
            pred = Prediction.query.filter_by(user_id=user.id, event_id=event.id).first()

            if event.start_datetime <= now:
                # Past event
                if pred:
                    user_event_scores[user.id][event.id] = pred.score
                    results = {r.rider_id: r.position for r in EventResult.query.filter_by(event_id=event.id).all()}

                    score_details[user.id][event.id] = [
                        {"rider": pred.rider_1.name, "position": results.get(pred.rider_1_id),
                         "points": pred.rider_1_score},
                        {"rider": pred.rider_2.name, "position": results.get(pred.rider_2_id),
                         "points": pred.rider_2_score},
                        {"rider": pred.rider_3.name, "position": results.get(pred.rider_3_id),
                         "points": pred.rider_3_score}
                    ]
                else:
                    # Past event but no score yet
                    user_event_scores[user.id][event.id] = "⏳"
                    score_details[user.id][event.id] = []
            else:
                # Future event
                user_event_scores[user.id][event.id] = "✅" if pred else "❌"
                score_details[user.id][event.id] = []

    return render_template(
        "events/leaderboard.html",
        user_scores=user_scores,
        events=events,
        user_event_scores=user_event_scores,
        score_details=score_details,
        current_user_id=current_user.id,
        now=now
    )
