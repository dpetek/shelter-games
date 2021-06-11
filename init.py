from flask import Flask
from flask_cors import CORS
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy


def create_app(instance = "prod"):
  app = Flask(__name__)
  app.secret_key = "space-secret"
  app.config["SECRET_KEY"] = "space-secret"
  app.config.from_pyfile('config/common.py')
  app.config.from_pyfile('config/%s.py' % instance)
  CORS(app, resources={r"/*":{"origins":"*"}})
  return app

app = create_app()

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
    )
)
conn = db.connect()
Session = sessionmaker(bind=db, autoflush=True)

Base = declarative_base(bind=db)

