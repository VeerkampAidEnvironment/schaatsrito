from flask import Blueprint

leaderboard_bp = Blueprint("leaderboard", __name__)

from .routes import *
