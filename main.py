from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_nav import Nav
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Link, Subgroup, Text
from flask_restful import Api, Resource
from markupsafe import escape
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from constants import *
import re
import random
import sqlalchemy

MAX_BETS_PER_ROUND = 20
INITIAL_GAME_COINS = 5

def create_app():
  app = Flask(__name__)
  app.secret_key = "super secret key"
  Bootstrap(app)
  return app

app = create_app()

app.config.from_pyfile('config/common.py')
app.config.from_pyfile('config/%s.py' % app.config["INSTANCE"])
CORS(app)

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

Base = declarative_base(bind=db)

class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state  = Column(Integer)
    question = Column(String)
    players = Column(String)

def game_to_dict(game):
    return dict({
        "id": game.id,
        "name": game.name,
        "state": game.state,
        "question": game.question
    })


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column( String)
    admin = Column( Integer)

def user_to_dict(user):
    return dict({
        "id": user.id,
        "name": user.name,
        "admin": user.admin
    })


class GamePlayer(Base):
    __tablename__ = 'game_player'
    id =  Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    game = relationship("Game")
    user = relationship("User")
    coins = Column(Integer)
    num_wins = Column(Integer)

def player_to_dict(player):
    return dict({
        "id": player.id,
        "game_id": player.game_id,
        "user_id": player.user_id,
        "game": game_to_dict(player.game) if player.game else None,
        "user": user_to_dict(player.user) if player.user else None,
        "coins": player.coins,
        "num_wins": player.num_wins
    })

class GameBoard(Base):
    __tablename__ = 'game_board'
    id =  Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship("Game")
    question_file = Column(String)
    answer_file = Column(String)
    phase = Column(Integer)
    active = Column(Integer)
    answer = Column(Float)

def board_to_dict(board):
    return dict({
        "id": board.id,
        "game_id": board.game_id,
        "question_file": board.question_file,
        "answer_file": board.answer_file,
        "phase": board.phase,
        "active": board.active,
        "answer": board.answer
    })
            

class BoardAnswer(Base):
    __tablename__ = 'board_answer'
    id =  Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey('game_board.id'))
    board = relationship("GameBoard")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")
    answer = Column(Float)
    won = Column(Integer)

class AnswerBet(Base):
    __tablename__ = 'answer_bet'
    id =  Column(Integer, primary_key=True)
    answer_id = Column(Integer, ForeignKey('board_answer.id'))
    answer = relationship("BoardAnswer")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")
    amount = Column(Integer)

def answer_bet_to_dict(answer_bet):
    return dict({
        "id": answer_bet.id,
        "answer_id": answer_bet.answer_id,
        "user": user_to_dict(answer_bet.user) if answer_bet.user else None,
        "amount": answer_bet.amount
    })

Base.metadata.create_all(db)

def logged_in():
    return ("user" in session) and session["user"]

def verify_username(username):
    return re.match("^[a-z0-9_-]{3,15}$", username)

@app.before_request
def init_all():
    db_session = Session()
    if not logged_in():
        if "user" in session:
            session.pop("user")
    else:
        pass
        #user = db_session.query(User).filter_by(id = session["user"]["id"]).first()
        #if user:
        #    session["user"] = dict({
        #        "id": user.id,
        #        "name": user.name,
        #        "admin": user.admin
        #        })


@app.teardown_request
def session_clear(exception=None):
    db_session = Session()

    if exception and db_session.is_active:
        db_session.rollback()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    db_session = Session()

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
        user = User(name=name, password=str(hash(password)), admin = 0)
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
    return render_template("codenames/codenames.html", title = "Codenames")

@app.route('/codename/create', methods=['POST'])
def codenames_create():
    pass

@app.route('/wits/game', methods=['GET'])
def get_board():
    game = db_session.query(Game).first()
    return jsonify(game)

@app.route('/codenames/game/<id>')
def codenames_game(id):
    return render_template("codenames/codenames.html")

@app.route('/wits')
def wits_index():
    if not logged_in():
        return render_template("wits/wits.html")
    db_session = Session()
    active_games = db_session.query(Game).filter_by(state = 1).all()
    joined_games = db_session.query(GamePlayer).filter_by(user_id = int(session["user"]["id"]))

    my_games = [joined.game_id for joined in joined_games]

    return render_template("wits/wits.html", title = "Wits & Wagers", games = active_games, my_games = my_games)

def create_new_board_for_game(game, db_session):
    r3 = random.randint(1, 3)
    r24 = random.randint(1, 24)
    question_file = "QA%d/q%d.jpg" % (r3, r24)
    answer_file = "QA%d/a%d.jpg" % (r3, r24)
    board = GameBoard(
        game_id = game.id,       
        question_file = question_file,
        answer_file = answer_file,
        phase = ANSWERING_PHASE,
        active = 1
    )
    db_session.add(board)
    db_session.commit()


@app.route('/wits/create', methods=['POST'])
def wits_create():
    db_session = Session()
    game = Game(
        name = request.form["name"],
        state = 1,
    )
    db_session.add(game)
    db_session.commit()
    create_new_board_for_game(game, db_session)
    return {"error": ""}

@app.route('/wits/delete', methods=['POST'])
def wits_delete():
    db_session = Session()

    db_session.query(Game).filter_by(id = request.form["id"]).update({"state": 2})
    db_session.commit()
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

def create_player(game_id, user_id, db_session):
    game_player = GamePlayer(
        game_id = game_id,
        user_id = user_id,
        coins = INITIAL_GAME_COINS,
        num_wins = 0
    )
    db_session.add(game_player)
    db_session.commit()

@app.route('/wits/enter', methods=['POST'])
def wits_enter():
    db_session = Session()
    id = request.form["id"]
    game_player = create_player(id, int(session["user"]["id"]), db_session)
    return jsonify({"error": "", "game_id": id})

@app.route('/wits/answer', methods=['POST'])
def wits_answer():
    db_session = Session()

    board_id = request.form["board_id"]


    try:
        answer_value = float(request.form["answer_value"])
    except ValueError:
        return jsonify({"error": "Answer value can't be parsed as a number."})

    board = db_session.query(GameBoard).filter_by(id = board_id).first()
    if not board:
        return jsonify({"error", "You can't answer anymore on this question."})

    game_player = db_session.query(GamePlayer).filter_by(game_id = board.game_id, user_id = session["user"]["id"]).first();
    if not game_player:
        game_player = create_player(board.game_id, session["user"]["id"], db_session);

    answer = db_session.query(BoardAnswer).filter_by(user_id = int(session["user"]["id"]), board_id = int(board_id)).first()
    if answer:
        return jsonify("error", "You already answered %f." % round(answer.answer, 1))

    answer = BoardAnswer(
            board_id = int(board_id),
            user_id = int(session["user"]["id"]),
            answer = answer_value
            )
    db_session.add(answer)
    db_session.commit()

    return jsonify({"error": ""})

@app.route('/wits/bet', methods=['POST'])
def wits_bet():
    db_session = Session()

    board_id = request.form["board_id"]
    board = db_session.query(GameBoard).filter_by(id = board_id).first()
    if not board:
        return jsonify({"error": "Board %s can't be found." % board_id})

    answer_id = request.form["answer_id"]
    answer = db_session.query(BoardAnswer).filter_by(id = answer_id).first()
    if not answer:
        return jsonify({"error": "Answer %s can't be found." % answer_id})

    amount = int(request.form["amount"])

    game_player = db_session.query(GamePlayer).filter_by(user_id = session["user"]["id"], game_id = board.game.id).first()
    if not game_player:
        return jsonify({"error": "Can't find player."})

    if game_player.coins < amount:
        return jsonify({"error": "You only have %d coins. Can't bet %d." % (game_player.coins, amount)})

    board_bets = db_session.query(AnswerBet).select_from(GameBoard).filter(AnswerBet.id == answer.id, User.id == session["user"]["id"]).all()
    board_bets_total = 0
    if board_bets:
        board_bets_total = sum(b.amount for b in board_bets)

    if board_bets_total + amount > MAX_BETS_PER_ROUND:
        return jsonify({"error": "You don't have enough credits left to bet %d." % amount})
    
    bet = db_session.query(AnswerBet).filter_by(answer_id = answer_id, user_id = session["user"]["id"]).first()
    if not bet:
        bet = AnswerBet(
                user_id = int(session["user"]["id"]),
                answer_id = int(answer_id),
                amount = 0)
    bet.amount += amount
    game_player.coins -= amount
    db_session.add(game_player)

    #TODO Check totals

    db_session.add(bet)
    db_session.commit()

    return jsonify({"error": ""})

@app.route('/wits/advance', methods=['POST'])
def wits_advance():
    db_session = Session()
    # TODO: only admin can do this

    board_id = request.form["board_id"]
    from_phase = int(request.form["from_phase"])

    board = db_session.query(GameBoard).filter_by(id = board_id).first()
    if not board:
        return jsonify({"error": "Can't find the board."})

    if board.phase != from_phase:
        return jsonify({"error": "Can't advance game to this state. %d %d" % (board.phase, from_phase)});

    if board.phase == ANSWERING_PHASE:
        board.phase = BETTING_PHASE
    elif board.phase == BETTING_PHASE:
        board.phase = ANSWER_VISIBLE
    elif board.phase == ANSWER_VISIBLE:
        try:
            answer_value = float(request.form["answer_value"])
        except ValueError:
            return jsonify({"error": "Answer value can't be parsed as a number."})

        all_answers = db_session.query(BoardAnswer).filter_by(board_id = board.id).order_by(BoardAnswer.answer).all()

        players = db_session.query(GamePlayer).filter_by(game_id = board.game_id).all()

        winning_answer = None
        for i in range(len(all_answers)):
            if all_answers[i].answer <= answer_value and (i + 1 == len(all_answers) or all_answers[i+1].answer > answer_value):
                winning_answer = all_answers[i].answer

        if winning_answer:
            for ans in all_answers:
                if abs(ans.answer - winning_answer) < 0.01:
                    answer_bets = db_session.query(AnswerBet).filter_by(answer_id = ans.id).all()
                    ans.won = 1
                    db_session.add(ans)
                    for p in players:
                        # Give coins to the closest (or correct) guesses
                        if str(p.user_id) == str(ans.user_id):
                            if abs(answer_value - winning_answer) < 0.01:
                                p.coins += 2
                                print ("%s gets %d coins to be completely correct." %(p.user.name, 2))
                            else:
                                p.coins += 1
                                print ("%s gets %d coins to be the closest." %(p.user.name, 1))
                        for bet in answer_bets:
                            if str(bet.user_id) == str(p.user_id):
                                print("%s gets %d based on %d bet." %(p.user.name, bet.amount * 2, bet.amount))
                                p.coins += bet.amount * 2
                        db_session.add(p)

        board.answer = answer_value
        board.phase = BOARD_FINALIZED
    elif board.phase == BOARD_FINALIZED:
        create_new_board_for_game(board.game, db_session)
        board.active = 0
        board.phase = ANSWERING_PHASE

    db_session.add(board)
    db_session.commit()

    return jsonify({"error": ""})


@app.route('/wits/results', methods=['POST'])
def wits_results():
    db_session = Session()
    game_id = request.form["id"]

    game_players = db_session.query(GamePlayer).filter_by(game_id = game_id).order_by(desc(GamePlayer.coins)).all()

    p = []
    for player in game_players:
        p.append(player_to_dict(player))
    return jsonify({"players": p})

@app.route('/wits/answer_bets', methods=['POST'])
def wits_bets():
    db_session = Session()
    answer_id = request.form["answer_id"]

    bets = db_session.query(AnswerBet).filter_by(answer_id = answer_id).order_by(desc(AnswerBet.amount)).all()
    a = []
    for bet in bets:
        a.append(answer_bet_to_dict(bet))
    return jsonify({"bets": a})


def normalize_answer(value):
    fv = float(value)
    if abs(float(value) - int(value)) < 0.01:
        return str(int(value))
    return value


@app.route('/wits/game/<id>')
def wits_game(id = None):
    db_session = Session()

    if not logged_in():
        return render_template("wits/wits_game.html", board = None)

    game = db_session.query(Game).filter_by(id = int(id)).first()
    if not game:
        return render_template("base/not_found.html")

    # Find active game board
    board = db_session.query(GameBoard).filter_by(game_id = id, active = 1).first()

    game_bets = db_session.query(AnswerBet).select_from(GameBoard).all()

    if not board:
        return render_template("base/not_found.html", resource_name = "Game Board")

    my_answer = db_session.query(BoardAnswer).filter_by(board_id = board.id, user_id = int(session["user"]["id"])).first()
    all_answers = db_session.query(BoardAnswer).filter_by(board_id = board.id).order_by(BoardAnswer.answer).all()

    game_players = db_session.query(GamePlayer).filter_by(game_id = game.id).order_by(desc(GamePlayer.coins)).all()

    return render_template("wits/wits_game.html",
            question_file = url_for('static', filename = board.question_file),
            answer_file = url_for('static', filename = board.answer_file),
            game = game,
            board = board,
            my_answer = my_answer,
            all_answers = all_answers,
            game_bets = game_bets,
            norm_answer = normalize_answer,
            game_players = game_players)

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
        user_string = session["user"]["name"]
        if session["user"]["admin"] > 0:
            user_string += " (admin)"
        full_navbar.items.append(
                Subgroup("Playing as %s" % user_string,
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
