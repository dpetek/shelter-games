# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from markupsafe import escape
import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import random


db_user = "root"
# todo: store somewhere else
db_pass = "<pass>"
db_name = "witts_new"
cloud_sql_connection_name = "wits-wagers:us-central1:dpetek-witts"


db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_pass,
        database=db_name,
        query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)},
    ),
    # ... Specify additional properties here.
    # ...
)
conn = db.connect()
metadata = MetaData()

games = Table('game', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('state', Integer),
    Column('question', String),
)
metadata.create_all(db)

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.

def create_app():
  app = Flask(__name__)
  Bootstrap(app)

  return app

app = create_app()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/codenames')
def codenames_index():
    return render_template("codenames.html")

@app.route('/codename/create', methods=['POST'])
def codenames_create():
    pass
    

@app.route('/codenames/game/<id>')
def codenames_game(id):
    return render_template("codenames.html")

@app.route('/wits')
def wits_index():
    s = select([games])
    result = conn.execute(s)
    active_games = []
    for game in result:
        active_games.append(game)
    return render_template("wits.html", games = active_games)

@app.route('/wits/create', methods=['POST'])
def wits_create():
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "%d_%d" % (rf, rq)
    stmt = sqlalchemy.text(
            "insert into game(name, state, question) values(:name, :state, :question)"
    )
    try:
        with db.connect() as conn:
            conn.execute(stmt, name = "First game", state = 2, question = qf)
    except Exception as e:
        return {"error": str(e)}
    return {"error": ""}

@app.route('/wits/advance', methods=['POST'])
def wits_advance():
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "%d_%d" % (rf, rq)
    stmt = sqlalchemy.text(
            "update game set question = :question where id = :id"
    )
    try:
        with db.connect() as conn:
            conn.execute(stmt, id = 1, question = qf)
    except Exception as e:
        return {"error": str(e)}
    return {"error": ""}

@app.route('/wits/enter', methods=['POST'])
def wits_enter():
    session["name"] = request.get_json()["name"]
    return {"user": session["name"]}

@app.route('/wits/answer', methods=['POST'])
def wits_answer():
    session["name"] = request.get_json()["name"]
    return {"user": session["name"]}

@app.route('/wits/game/<id>')
def wits_game(id = None):
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "QA%s/q%s.jpg" % (rf, rq)
    af = "QA%s/a%s.jpg" % (rf, rq)
    return render_template("wits_game.html",  question_file = url_for('static', filename=qf), answer_file = url_for('static', filename = af))

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'Dpetek Shelter In Place',
        View('Home', 'index'),
        View('Wits And Wagers', 'wits_index'),
        View('Codenames', 'codenames_index')
    )
nav.init_app(app)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
