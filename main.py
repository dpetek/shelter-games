from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import jsonify
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from markupsafe import escape
import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import random
import os

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
)
conn = db.connect()
metadata = MetaData()

games = Table('game', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('state', Integer),
    Column('question', String),
    Column('players', String),
)

users = Table('user', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('password', String),
        Column('admin', Integer)
)
metadata.create_all(db)

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.

def create_app():
  app = Flask(__name__)
  app.secret_key = "super secret key"
  Bootstrap(app)
  return app

app = create_app()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    if "name" in session:
        return {"error": "Already logged in. Please log-off first."}

    name = request.form["username"]
    password = request.form["password"]

    # Check if user exists
    if not user:
        pass

    session["name"] = name
    session["user"] = user
    session["is_admin"] = (user == "dpetek")

@app.route('/codenames')
def codenames_index():
    return render_template("codenames.html", title = "Codenames")

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
    return render_template("wits.html", title = "Wits & Wagers", games = active_games)

@app.route('/wits/create', methods=['POST'])
def wits_create():
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "%d_%d" % (rf, rq)
    stmt = sqlalchemy.text(
            "insert into game(name, state, question) values(:name, :state, :question)"
    )
    game_name = request.form["name"]
    try:
        conn.execute(stmt, name = game_name, state = 2, question = qf)
    except Exception as e:
        return {"error": str(e)}
    return {"error": "","game": {"name": game_name}}

@app.route('/wits/delete', methods=['POST'])
def wits_delete():
    print (request.form)
    stmt = sqlalchemy.text(
            "delete from game where id = :id"
    )
    try:
        conn.execute(stmt, id = request.form["id"])
    except Exception as e:
        return {"error": str(e)}
    return {"error": ""}

@app.route('/wits/skip', methods=['POST'])
def wits_skip():
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "%d_%d" % (rf, rq)
    stmt = sqlalchemy.text(
            "update game set question = :question where id = :id"
    )
    try:
        conn.execute(stmt, id = request.form["id"], question = qf)
    except Exception as e:
        return {"error": str(e)}
    return {"error": ""}

@app.route('/wits/enter', methods=['POST'])
def wits_enter():
    name = request.form["name"]
    session["name"] = name
    # TODO Insert into db if it doesn't exist
    return jsonify({"user": session["name"]})

@app.route('/wits/answer', methods=['POST'])
def wits_answer():
    user = session["name"]
    answer = request.get_json()["answer"]
    return {"user": session["name"]}

@app.route('/wits/game/<id>')
def wits_game(id = None):
    s = select([games])
    result = conn.execute(s)
    game = None
    for g in result:
        if str(g["id"]) == str(id):
            game = g

    if game == None:
        render_template("not_found.html")

    print(game)
    parts = game["question"].split("_")
    qf = "QA%s/q%s.jpg" % (parts[0], parts[1])
    af = "QA%s/a%s.jpg" % (parts[0], parts[1])

    return render_template("wits_game.html",
            question_file = url_for('static', filename = qf),
            answer_file = url_for('static', filename = af),
            game = game)

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'Shelter Games',
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
