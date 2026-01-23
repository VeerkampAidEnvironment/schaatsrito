from flask import Blueprint

events_bp = Blueprint("events", __name__)

from .overview import *
from .detail import *
from .startlist import *
from .results import *
