from flask_login import login_required, current_user
from flask import render_template, redirect, request, url_for, flash
from app import db
from app.models import Event, Prediction, User
from datetime import datetime, timedelta
from . import events_bp
import json
import os

@events_bp.route("/events")
@login_required
def events_overview():
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=1)
    events = Event.query.order_by(Event.start_datetime).all()
    user_predictions = {p.event_id for p in Prediction.query.filter_by(user_id=current_user.id)}

    return render_template(
        "events/overview.html",
        events=events,
        user_predictions=user_predictions,
        now=now
    )

@events_bp.route("/methods")
def methods_page():
    file_path = "/home/schaatsrito/mysite/data/methods.json"
    full_path = os.path.abspath(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            methods = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        methods = {}
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON at {file_path}")
        methods = {}
    except Exception as e:
        print(f"An unexpected error occurred while opening {file_path}: {e}")
        methods = {}
    return render_template("uitleg.html", methods=methods)

@events_bp.route("/account/username", methods=["GET", "POST"])
@login_required
def change_username():
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()

        if not new_username:
            flash("Username cannot be empty.", "error")
            return redirect(url_for("events.change_username"))

        if new_username == current_user.username:
            flash("That is already your username.", "info")
            return redirect(url_for("events.change_username"))

        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            flash("That username is already taken.", "error")
            return redirect(url_for("events.change_username"))

        current_user.username = new_username
        db.session.commit()

        flash("Username updated successfully!", "success")
        return redirect(url_for("events.change_username"))

    return render_template("change_username.html")

@events_bp.route("/admin/users")
@login_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@events_bp.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    # 🔒 OPTIONAL: restrict access
    # if not current_user.is_admin:
    #     abort(403)

    user = User.query.get_or_404(user_id)

    # Prevent self-deletion if you want
    if user.id == current_user.id:
        flash("You cannot delete your own account this way.", "error")
        return redirect(url_for("events.events_overview"))

    # Manually delete predictions if no cascade
    Prediction.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    flash(f"User '{user.username}' has been deleted.", "success")
    return redirect(url_for("events.events_overview"))

