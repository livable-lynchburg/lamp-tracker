#THIS IMPORT AND INSTANTIATION MUST COME FIRST
from flask import Flask
# TODO LOOK INTO INSTANCE FOLDER CONCEPT
app = Flask(__name__, static_url_path="/static", static_folder="static")

#THIS IMPORT AND INSTANTIATION MUST COME SECOND
from flask_login import LoginManager
login_manager = LoginManager(app)
login_manager.login_view = "log_in"
login_manager.login_message_category = "info"

from lamp_tracker_package import views

# importing app configuration from Python object
app.config.from_object("config.Config")

# TODO move db instantiation here
