from flask import redirect, url_for, flash
from flask_login import login_required
from app.models import Event
from scripts.calculate_scores import update_scores_for_event
from . import admin_bp

@admin_bp.route("/update-scores")
@login_required
def update_scores():
    events = Event.query.all()
    for event in events:
        update_scores_for_event(event.id)
    flash("Scores updated successfully!", "success")
    return redirect(url_for("leaderboard.leaderboard"))
