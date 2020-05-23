from eventlet.green import socket
from eventlet.green import threading
from eventlet.green import asyncore
import eventlet
eventlet.monkey_patch()

from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from flask_cors import CORS

MAX_BETS_PER_ROUND = 50
INITIAL_GAME_COINS = 10

ANSWER_NEGATIVE_LIMIT = -1000000

def create_app():
  app = Flask(__name__)
  app.secret_key = "space-secret"
  app.config["SECRET_KEY"] = "space-secret"
  return app

app = create_app()

app.config.from_pyfile('config/common.py')
app.config.from_pyfile('config/%s.py' % app.config["INSTANCE"])

CORS(app, resources={r"/*":{"origins":"*"}})

socketio = SocketIO(app, async_mode="eventlet")

db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_DATABASE"],
        port=3306,
        host="127.0.0.1.",
        query={"unix_socket": "/cloudsql/{}".format(app.config["DB_SQL_CONNECTION_NAME"])},
    ),
    pool_size = 30,
    max_overflow = 10
)
conn = db.connect()

Base = declarative_base(bind=db)
