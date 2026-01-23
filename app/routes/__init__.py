# Import blueprints from each route package

from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.events import events_bp
from app.routes.admin import admin_bp

# List of all blueprints for easy registration
blueprints = [
    auth_bp,
    main_bp,
    events_bp,
    admin_bp,
]
