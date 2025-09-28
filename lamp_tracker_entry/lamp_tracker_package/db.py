from lamp_tracker_package import app, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from geoalchemy2.types import Geography
from sqlalchemy import inspect, event, text
from sqlalchemy.sql.expression import and_
from datetime import datetime
from flask_migrate import Migrate

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def database_is_empty():
    engine = db.engines[None]
    table_names = inspect(engine).get_table_names()
    is_empty = table_names == []
    return is_empty


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.BigInteger, primary_key=True)
    password = db.Column(db.Unicode(200), nullable=False)
    name = db.Column(db.Unicode)
    email = db.Column(db.Unicode(200), nullable=False)
    role = db.Column(db.Unicode(200), nullable=False)

class Outage(db.Model):
    lamp_id = db.Column(db.BigInteger, db.ForeignKey("lamp.id"), primary_key=True)
    found_dtm = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, primary_key=True)
    report_dtm = db.Column(db.DateTime, nullable=True);
    checked_dtm = db.Column(db.DateTime, nullable=True);
    fixed_dtm = db.Column(db.DateTime, nullable=True);
    most_recent_contact_dtm = db.Column(db.DateTime, nullable=True);
    report_dtm = db.Column(db.DateTime, nullable=True);
    work_order_id = db.Column(db.Unicode);

class Lamp(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    store_id = db.Column(db.BigInteger, db.ForeignKey("store.id"), primary_key=True)
    change_dtm = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, primary_key=True)
    location = db.Column(Geography("POINT"))
    #   Chose BigInteger type because it is used for IDs in OSM's internal schema
    osm_id = db.Column(db.BigInteger)
    verizon_id = db.Column(db.Unicode);
    appco_id = db.Column(db.Unicode);
    lynchburg_id = db.Column(db.Unicode);
    addr_housenumber = db.Column(db.Unicode)
    addr_street = db.Column(db.Unicode)
    addr_city = db.Column(db.Unicode)
    addr_state = db.Column(db.Unicode)
    addr_postcode = db.Column(db.Unicode)
