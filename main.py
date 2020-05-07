from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Link, Subgroup, Text
from markupsafe import escape
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
import re
import random
import sqlalchemy

def create_app():
  app = Flask(__name__)
  app.secret_key = "super secret key"
  Bootstrap(app)
  return app

app = create_app()

app.config.from_pyfile('config/common.py')
app.config.from_pyfile('config/%s.py' % app.config["INSTANCE"])

db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_DATABASE"],
        query={"unix_socket": "/cloudsql/{}".format(app.config["DB_SQL_CONNECTION_NAME"])},
    ),
)
conn = db.connect()
Session = sessionmaker(bind=db)
db_session = Session()

Base = declarative_base(bind=db)

class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state  = Column(Integer)
    question = Column(String)
    players = Column(String)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column( String)
    admin = Column( Integer)

Base.metadata.create_all(db)

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.

def logged_in():
    return ("user" in session) and session["user"]

def verify_username(username):
    return re.match("^[a-z0-9_-]{3,15}$", username)

@app.before_request
def init_all():
    if not logged_in():
        if "user" in session:
            session.pop("user")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    if "user" in session:
        return jsonify({"error": "Already logged in. Please log-off first."})

    name = request.form["username"]
    password = request.form["password"]

    if not verify_username(name):
        return jsonify({"error": "Wrong username format. Allowed special characters are numbers, '_' and '-'"})

    user = db_session.query(User).filter_by(name = name).first()
    if user:
        if str(hash(password)) != user.password:
            return jsonify({"error": "Wrong password."})
    else:
        is_admin = 1 if name == "dpetek" else 0
        user = User(name=name, password=str(hash(password)), admin = is_admin)
        db_session.add(user)
        db_session.commit()

    session["user"] = dict({
        "id": user.id,
        "name": user.name,
        "admin": user.admin
    })
    return jsonify({"error": ""})

@app.route('/logout', methods=['POST'])
def logout():
    if "user" in session:
        session.pop("user")
    return jsonify({"error": ""})

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
    s = select([Game])
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
    # TODO Insert into db if it doesn't exist
    return jsonify({"user": session["name"]})

@app.route('/wits/answer', methods=['POST'])
def wits_answer():
    user = session["name"]
    answer = request.get_json()["answer"]
    return {"user": session["name"]}

@app.route('/wits/game/<id>')
def wits_game(id = None):
    s = select([Game])
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
    full_navbar =  Navbar(
        'Shelter Games',
        View('Home', 'index'),
        View('Wits And Wagers', 'wits_index'),
        View('Codenames', 'codenames_index')
    )
    if logged_in():
        full_navbar.items.append(
                Subgroup("Playing as %s" % session["user"]["name"],
                         Link("Logout", "javascript:doLogout();")
                )
        )
    return full_navbar

nav.init_app(app)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
