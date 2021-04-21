from flask import Blueprint

# Define a Blueprint for this module (mchat)
accounts = Blueprint('accounts', __name__, url_prefix='/')

# Import all controllers
from .controllers.users_controller import *
from .controllers.sessions_controller import *
from .controllers.google_auth import *
