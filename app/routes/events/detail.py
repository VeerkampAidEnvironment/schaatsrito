from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Event, Prediction, Rider
from app import db
from . import events_bp
from datetime import datetime, timedelta


@events_bp.route("/events/<int:event_id>", methods=["GET", "POST"])
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=-359)

    prediction = Prediction.query.filter_by(user_id=current_user.id, event_id=event.id).first()

    # FUTURE EVENT: allow prediction
    if event.start_datetime > now:
        startlist_entries = event.startlist
        if startlist_entries:
            startlist = [entry.rider for entry in startlist_entries]
            startlist_loaded = True
        else:
            startlist = Rider.query.filter_by(gender=event.gender).order_by(Rider.name).all()
            startlist_loaded = False

        if request.method == "POST":
            rider_1_id = request.form.get("rider_1")
            rider_2_id = request.form.get("rider_2")
            rider_3_id = request.form.get("rider_3")

            if not all([rider_1_id, rider_2_id, rider_3_id]):
                flash("Please select 3 riders.", "error")
                return redirect(url_for("events.event_detail", event_id=event.id))

            if prediction:
                prediction.rider_1_id = rider_1_id
                prediction.rider_2_id = rider_2_id
                prediction.rider_3_id = rider_3_id
            else:
                prediction = Prediction(
                    user_id=current_user.id,
                    event_id=event.id,
                    rider_1_id=rider_1_id,
                    rider_2_id=rider_2_id,
                    rider_3_id=rider_3_id,
                )
                db.session.add(prediction)

            db.session.commit()
            return redirect(url_for("events.event_detail", event_id=event.id))

        return render_template(
            "events/detail.html",
            event=event,
            startlist=startlist,
            prediction=prediction,
            future=True,
            startlist_loaded=startlist_loaded,
            now=now
        )

    # PAST EVENT: show results + scores
    else:
        results_entries = event.results
        results = sorted(results_entries, key=lambda r: r.position)
        results_loaded = bool(results_entries)

        user_rider_ids = []
        prediction_data = None
        if prediction:
            user_rider_ids = [prediction.rider_1_id, prediction.rider_2_id, prediction.rider_3_id]

            # Only include score info if event is past
            prediction_data = {
                "rider_1_id": prediction.rider_1_id,
                "rider_2_id": prediction.rider_2_id,
                "rider_3_id": prediction.rider_3_id,

                # subscores
                "rider_1_base": prediction.rider_1_base,
                "rider_1_captain": prediction.rider_1_captain,
                "rider_1_rarity": prediction.rider_1_rarity,
                "rider_1_score": prediction.rider_1_score,

                "rider_2_base": prediction.rider_2_base,
                "rider_2_captain": prediction.rider_2_captain,
                "rider_2_rarity": prediction.rider_2_rarity,
                "rider_2_score": prediction.rider_2_score,

                "rider_3_base": prediction.rider_3_base,
                "rider_3_captain": prediction.rider_3_captain,
                "rider_3_rarity": prediction.rider_3_rarity,
                "rider_3_score": prediction.rider_3_score,

                # total score
                "score": prediction.score
            }

        return render_template(
            "events/detail.html",
            event=event,
            results=results,
            user_rider_ids=user_rider_ids,
            prediction=prediction_data,
            future=False,
            results_loaded=results_loaded
        )
