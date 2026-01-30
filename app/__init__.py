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
    from app.routes import blueprints

    def create_app():
        app = Flask(__name__)
        app.config.from_object(Config)

        # Import models
        from app import models

        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        Migrate(app, db)

        # Register all blueprints
        for bp in blueprints:
            app.register_blueprint(bp)

        # Add CLI commands
        from scripts.seed_events import seed_events
        app.cli.add_command(seed_events)

        from scripts.seed_riders import seed_riders_command
        app.cli.add_command(seed_riders_command)

        return app

    return app
