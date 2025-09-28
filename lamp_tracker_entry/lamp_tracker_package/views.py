from lamp_tracker_package import app

# TODO: import db from __Init__ instead
from lamp_tracker_package.db import (
    db,
    database_is_empty,
    User,
    Lamp,
    Outage
)

from flask import (
    render_template,
    make_response,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    abort,
    jsonify
)

from flask_login import login_user, current_user, logout_user, login_required
import re


@app.route("/")
def root():
    if database_is_empty():  # If there is no database
        return redirect(url_for("setup"))  # Run the setup wizard
    else:
        return redirect(url_for("find_lamp"))

@app.route("/setup")
def setup():
    return "This is the setup page"

@app.route("/find_lamp")
def find_lamp():
    return "This is the page where you find a lamp"
