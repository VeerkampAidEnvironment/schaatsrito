from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login_register"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import models
    from app import models

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.leaderboard import leaderboard_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(admin_bp)

    # Register CLI commands
    from scripts.seed_events import seed_events
    app.cli.add_command(seed_events)

    from scripts.seed_riders import seed_riders_command
    app.cli.add_command(seed_riders_command)
    # Register Olympic startlists command
    from scripts.import_olympic_startlists import import_olympic_startlists_command
    app.cli.add_command(import_olympic_startlists_command)

    from scripts.change_event_id import change_event_id
    app.cli.add_command(change_event_id)

    from scripts.reset_password import reset_password
    app.cli.add_command(reset_password)

    from scripts.change_start_time import change_start_time
    app.cli.add_command(change_start_time)

    from scripts.add_team import add_team
    app.cli.add_command(add_team)

    from scripts.add_provisional_bulk import add_provisional_bulk
    app.cli.add_command(add_provisional_bulk)

    from scripts.manage_startlist import manage_startlist
    app.cli.add_command(manage_startlist)

    from scripts.change_rider_id import change_rider_id
    app.cli.add_command(change_rider_id)

    from app.routes import blueprints

    return app
