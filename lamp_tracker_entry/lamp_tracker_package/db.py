from lamp_tracker_package import app, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from geoalchemy2.types import Geography
from sqlalchemy import inspect, event, text, Integer, bigint, String, unicode
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from flask_migrate import Migrate

class Base(DeclarativeBase):
      pass

db = SQLAlchemy(app, model_class=Base)

# might not work
with app.app_context():
    db.create_all()

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
    id: Mapped[bigint] = mapped_column(primary_key=True)
    password: Mapped[unicode] = mapped_column(nullable=False)
    name: Mapped[unicode] = mapped_column() # figure out how to make 200chars
    email: Mapped[unicode] = mapped_column(nullable=False) # 200chars
    role: Mapped[unicode] = mapped_column(nullable=False) #200chars

class Outage(db.Model):
    lamp_id: Mapped[bigint] = mapped_column(ForeignKey("lamp.id"), primary_key=True)
    found_dtm: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, primary_key=True)
    report_dtm: Mapped[datetime] = mapped_column(nullable=True)
    checked_dtm: Mapped[datetime] = mapped_column(nullable=True)
    fixed_dtm: Mapped[datetime] = mapped_column(nullable=True)
    most_recent_contact_dtm: Mapped[datetime] = mapped_column(nullable=True)
    report_dtm: Mapped[datetime] = mapped_column(nullable=True)
    work_order_id: Mapped[unicode] = mapped_column()

class Lamp(db.Model):
    id: Mapped[bigint] = mapped_column(primary_key=True)
    store_id: Mapped[bigint] = mapped_column(ForeignKey("store.id"), primary_key=True)
    change_dtm: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, primary_key=True)
    location: Mapped['Geography'] = mapped_column(Geography("POINT"))
    #   Chose bigint type because it is used for IDs in OSM's internal schema
    osm_id: Mapped[bigint] = mapped_column()
    verizon_id: Mapped[unicode] = mapped_column()
    apco_id: Mapped[unicode] = mapped_column()
    lynchburg_id: Mapped[unicode] = mapped_column()
    addr_housenumber: Mapped[unicode] = mapped_column()
    addr_street: Mapped[unicode] = mapped_column()
    addr_city: Mapped[unicode] = mapped_column()
    addr_state: Mapped[unicode] = mapped_column()
    addr_postcode: Mapped[unicode] = mapped_column()
