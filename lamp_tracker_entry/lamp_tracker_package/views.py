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

# This route initializes the database if the database is currently empty
@app.route("/init_db")
def init_db():
    # TODO: remove table dropping from web UI
    is_empty = database_is_empty()
    if is_empty:
        db.create_all()
        flash("Initializing database. Done", "success")
    else:
        flash("Database already created. Doing nothing.", "warning")
    return redirect(url_for("setup"))


@app.cli.command("init_db")
def init_db_cli():
    def drop_and_create_db(db):
        print("Dropping database ... Done")
        db.drop_all()
        print("Dropping database ... Done")
        db.create_all()
        print("Initializing database ... Done")

    if database_is_empty():
        drop_and_create_db(db)
    else:
        confirmation_string = "Peter Piper picked a peck of pickled peppers."
        user_string = input(
            f"Database already created! Enter '{confirmation_string}' to overwrite: "
        )
        if user_string == confirmation_string:
            drop_and_create_db(db)
        else:
            print("Confirmation entry incorrect. Doing nothing.")

@app.route("/setup")
def setup():
    return "This is the setup page"

@app.route("/find_lamp")
def find_lamp():
    return "This is the page where you find a lamp"

@app.route("/.well-known/acme-challenge/<path:filename>")
def acme_challenge(filename):
    return send_from_directory("static/.well-known/acme-challenge/", filename)
