import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User
from app import db

auth_bp = Blueprint("auth", __name__)

# Only letters, numbers, underscores; 3-20 characters
USERNAME_REGEX = r"^[A-Za-z0-9_ ]{3,20}$"

@auth_bp.route("/", methods=["GET", "POST"])
def login_register():
    slide_to_login = False  # determines which form is shown on render

    if request.method == "POST":
        form_type = request.form.get("form_type")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Basic empty field check
        if not username or not password:
            flash("Username and password cannot be empty.", "error")
            slide_to_login = form_type == "login"
            return render_template("auth/login_register.html", hide_navbar=True, slide_to_login=slide_to_login)

        if form_type == "login":
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("events.events_overview"))
            flash("Invalid login credentials.", "error")
            slide_to_login = True

        elif form_type == "signup":
            # Username validation
            if not re.match(USERNAME_REGEX, username):
                flash(
                    "Username must be 3-20 characters long and contain only letters, numbers, and underscores.",
                    "error"
                )
                slide_to_login = False
            elif User.query.filter_by(username=username).first():
                flash("Username already exists. Please choose another.", "error")
                slide_to_login = False
            else:
                # create user without password restrictions
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("Registration successful! Please log in.", "success")
                slide_to_login = True  # switch to login form after signup

    return render_template(
        "auth/login_register.html",
        hide_navbar=True,
        slide_to_login=slide_to_login
    )


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login_register"))
