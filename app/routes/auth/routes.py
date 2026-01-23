from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User
from app import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login_register():
    if request.method == "POST":
        form_type = request.form.get("form_type")
        username = request.form.get("username")
        password = request.form.get("password")

        if form_type == "login":
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("events.events_overview"))
            flash("Invalid login credentials", "error")

        elif form_type == "signup":
            if User.query.filter_by(username=username).first():
                flash("Username already exists", "error")
            else:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("Registration successful! Please log in.", "success")
                # optionally slide to login form after signup

    return render_template("auth/login_register.html", hide_navbar=True)



@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login_register"))
