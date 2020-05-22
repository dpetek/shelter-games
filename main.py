from eventlet.green import socket
from eventlet.green import threading
from eventlet.green import asyncore
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, Float, desc, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from constants import *
import logging
import random
import re
import sqlalchemy
import time

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

class ApiResource():
    def as_dict(self, db_session = None):
        ret = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return ret

class Game(Base, ApiResource):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state  = Column(Integer)

class WitsQuestion(Base, ApiResource):
    __tablename__ = 'wits_question'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer  = Column(Float)
    notes = Column(Text)
    category = Column(String)

class User(Base, ApiResource):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column( String)
    admin = Column( Integer)


class GamePlayer(Base, ApiResource):
    __tablename__ = 'game_player'
    id =  Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    avatar = Column(String)
    game_id = Column(Integer)
    user_id = Column(Integer)
    coins = Column(Integer)
    num_wins = Column(Integer)

    def as_dict(self, db_session):
        ret = super(GamePlayer, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.game_id:
            game = db_session.query(Game).filter(Game.id == self.game_id).first()
            ret["game"] = game.as_dict(None)
        if self.user_id:
            user = db_session.query(User).filter(User.id == self.user_id).first()
            ret["user"] = user.as_dict(None)
        return ret

    
class GameBoard(Base, ApiResource):
    __tablename__ = 'game_board'
    id =  Column(Integer, primary_key=True)
    game_id = Column(Integer)
    question_file = Column(String)
    answer_file = Column(String)
    phase = Column(Integer)
    active = Column(Integer)
    question_id = Column(Integer)
    answer = Column(Float)

    def as_dict(self, db_session):
        ret = super(GameBoard, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.question_id:
            question = db_session.query(WitsQuestion).filter(WitsQuestion.id == self.question_id).first()
            ret["question"] = question.as_dict(None)
        if self.game_id:
            game = db_session.query(Game).filter(Game.id == self.game_id).first()
            ret["game"] = game.as_dict(None)
        return ret

class BoardAnswer(Base, ApiResource):
    __tablename__ = 'board_answer'
    id =  Column(Integer, primary_key=True)
    board_id = Column(Integer)
    # user_id = Column(Integer)
    player_id = Column(Integer)
    answer = Column(Float)
    won = Column(Integer)
    odds = Column(Integer)

    def as_dict(self, db_session):
        ret = super(BoardAnswer, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.board_id:
            board = db_session.query(GameBoard).filter(GameBoard.id == self.board_id).first()
            ret["board"] = board.as_dict(None)
        if self.player_id:
            player = db_session.query(GamePlayer).filter(GamePlayer.id == self.player_id).first()
            if player:
                ret["player"] = player.as_dict(None)
        return ret

class AnswerBet(Base, ApiResource):
    __tablename__ = 'answer_bet'
    id =  Column(Integer, primary_key=True)
    answer_id = Column(Integer)
    user_id = Column(Integer)
    player_id = Column(Integer)
    amount = Column(Integer)

    def as_dict(self, db_session):
        ret = super(AnswerBet, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.answer_id:
            answer = db_session.query(BoardAnswer).filter(BoardAnswer.id == self.answer_id).first()
            ret["answer"] = answer.as_dict(None)
        if self.player_id:
            player = db_session.query(GamePlayer).filter(GamePlayer.id == self.player_id).first()
            ret["player"] = player.as_dict(None)
        return ret

Base.metadata.create_all(db)

Session = sessionmaker(bind=db, autoflush=False)

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def create_player(game_id, user_id, avatar, db_session):
    game_player = GamePlayer(
        game_id = game_id,
        user_id = user_id,
        avatar = avatar,
        coins = INITIAL_GAME_COINS,
        num_wins = 0
    )
    db_session.add(game_player)

def get_string_from_request_json(request, key):
    if not key in request.get_json():
        return ""
    value = request.get_json()[key]
    if not value:
        return ""
    return request.get_json()[key]

def verify_username(username):
    return True
    # return re.match("^[A-Za-z0-9_-]{3,15}$", username)

def create_new_board_for_game(game, db_session):
    rand_question = db_session.query(WitsQuestion).order_by(func.random()).first()

    board = GameBoard(
        game_id = game.id,       
        question_id = rand_question.id,
        question_file = "",
        answer_file = "",
        phase = ANSWERING_PHASE,
        active = 1
    )
    db_session.add(board)
    return board

@socketio.on('message')
def wits_socket_connected(message):
    # Process messages received from the client.
    pass

@app.route('/')
def index(): 
    return render_template('gen/index.html')

@app.route('/api/login', methods = ['POST'])
def api_login():
    db_session = Session()
    name = request.get_json()["username"]

    if not verify_username(name):
        return jsonify({"error": "Wrong username format. Allowed special characters are numbers, '_' and '-'"})

    user = User(name=name, password=str(hash("")), admin = 0)
    db_session.add(user)
    db_session.commit()
    session["user"] = user.as_dict(db_session)

    return jsonify({"error": "", "user": user.as_dict(db_session)})

@app.route('/api/logout', methods = ['POST'])
def api_logout():
    if "user" in session:
        session.pop("user")
    return jsonify({"error": ""})

@app.route('/api/current_user', methods = ['GET'])
def api_current_user():
    if not "user" in session:
        return jsonify({"error": "User is not logged in..."})

    db_session = Session()
    current_user = db_session.query(User).filter_by(id = session["user"]["id"]).first()
    if not current_user:
        return jsonify({"error": "User is not logged in."})
    return jsonify({"error": "", "user": current_user.as_dict(db_session)})

@app.route('/api/wits/games', methods = ['GET'])
@app.route('/api/wits/games/', methods = ['GET'])
def api_get_wits_games():
    db_session = Session()
    games = db_session.query(Game).filter_by(state = 1).all()
    g = []
    for game in games:
        g.append(game.as_dict(db_session))
    return jsonify({"games": g})

@app.route('/api/wits/game/<id>', methods = ['GET'])
def api_get_wits_game(id):
    db_session = Session()
    game = db_session.query(Game).filter_by(id = id).first()
    if not game:
        return jsonify({"error": "Game not found."})

    board = db_session.query(GameBoard).filter_by(game_id = game.id, active = 1).first()
    if not board:
        return jsonify({"error": "Game board not found."})

    return jsonify({"error": "", "game": game.as_dict(db_session), "board": board.as_dict(db_session)})

@app.route('/api/wits/game/<id>/current_player', methods = ['GET'])
def api_get_wits_game_current_player(id):
    db_session = Session()
    game = db_session.query(Game).filter_by(id = id).first()
    if not game:
        return jsonify({"error": "Game not found."})

    print("Fetching session value for %d" % game.id)
    if not str(game.id) in session:
        return jsonify({"error": "Player not selected."})

    return jsonify({"error": "", "player": session[str(game.id)]})


@app.route('/api/wits/game/<id>/enter', methods = ['POST'])
def api_enter_game(id):
    db_session = Session()

    name = get_string_from_request_json(request, "name")
    if not verify_username(name):
        return jsonify({"error": "Wrong name format. Allowed special characters are numbers, '_' and '-'"})

    password = get_string_from_request_json(request, "password")
    returning = get_string_from_request_json(request, "returning")
    avatar = get_string_from_request_json(request, "avatar")

    if not avatar:
        return jsonify({"error": "You have to select your avatar."})

    game_id = int(id)

    game = db_session.query(Game).filter(Game.id == game_id).first()
    if not game:
        return jsonofy({"error": "Can't find the game."})

    if returning:
        player = db_session.query(GamePlayer).filter_by(name = name, password = hash(password)).first()
        if not player:
            return jsonify({"error": "Wrong name or password."})
        print ("Setting session id for ", game_id)
        session[str(game_id)] = player.as_dict(None)
        return jsonify({"error": "", "player": session[str(game_id)]})


    player = GamePlayer(
            name = name,
            password = hash(password),
            user_id = 0,
            avatar = avatar,
            game_id = game_id,
            coins = INITIAL_GAME_COINS,
            num_wins = 0
            )
    db_session.add(player)
    db_session.commit()
    session[str(game.id)] = player.as_dict(None)
    print("Setting session value for %d" % game.id)
    return jsonify({"error": "", "player": session[str(game.id)]})
    

@app.route('/api/wits/game/<id>/players', methods = ['GET'])
def api_get_wits_game_players(id):
    db_session = Session()
    players = db_session.query(GamePlayer).filter_by(game_id = id).order_by(desc(GamePlayer.coins)).all()
    p = []
    
    for player in players:
        p.append(player.as_dict(db_session))

    return jsonify({"error": "", "players": p})

@app.route('/api/wits/game/board/<id>/answers', methods = ['GET'])
def api_get_board_answers(id):
    db_session = Session()

    board = db_session.query(GameBoard).filter_by(id = id).first()
    if not board:
        return jsonify({"error": "Board can't be found."})

    answers = db_session.query(BoardAnswer).filter_by(board_id = id).order_by(BoardAnswer.answer).all()

    ids = [a.id for a in answers]
    board_bets = db_session.query(AnswerBet).filter(AnswerBet.answer_id.in_(ids)).all()

    game = db_session.query(Game).filter(Game.id == board.game_id).first()
    if not game:
        return jsonify({"error": "Game can't be found."})

    a = []
    for answer in answers:
        if board.phase == 1:
            if not str(game.id) in session or str(session[str(game.id)]["id"]) != str(answer.player_id):
                answer.answer = None
        answer_dict = answer.as_dict(db_session)
        for bet in board_bets:
            if str(bet.answer_id) == str(answer_dict["id"]):
                if not "bets" in answer_dict:
                    answer_dict["bets"] = []
                answer_dict["bets"].append(bet.as_dict(db_session))
        a.append(answer_dict)

    ret = jsonify({"error": "", "answers": a})
    return ret

@app.route('/api/wits/game/answer/<id>/bet', methods = ['POST'])
def api_bet_on_answer(id):
    db_session = Session()

    answer = db_session.query(BoardAnswer).filter_by(id = id).first()
    if not answer:
        return jsonify({"error": "Can't find answer for id %d" % id})

    amount_str = get_string_from_request_json(request, "amount")
    amount = 0
    try:
        amount = int(amount_str)
    except ValueError:
        return jsonify({"error": "Can't parse %s as integer amount." % amount_str})

    if amount < 0:
        return jsonify({"error": "Come on. You can't bet negative amount."});

    board = db_session.query(GameBoard).filter_by(id = answer.board_id).first()
    if not board:
        return jsonify({"error": "Board can't be found."});

    game_player = db_session.query(GamePlayer).filter_by(id = session[str(board.game_id)]["id"]).first()

    if not game_player:
        return jsonify({"error": "Game player can't be found. Please refresh the page."})

    #if not game_player:
    #    game_player = GamePlayer(
    #        game_id = board.game_id,
    #        user_id = None,
    #        coins = INITIAL_GAME_COINS,
    #        num_wins = 0
    #    )

    answers = db_session.query(BoardAnswer).filter_by(board_id = answer.board_id).all()
    ids = [a.id for a in answers]

    player_board_bets = db_session.query(AnswerBet).filter_by(player_id = session[str(board.game_id)]["id"]).filter(AnswerBet.answer_id.in_(ids)).all()

    board_bets_total = 0
    answer_bets_total = 0
    if player_board_bets:
        board_bets_total = sum(b.amount for b in player_board_bets if b.answer_id != answer.id)
        answer_bets_total = sum(b.amount for b in player_board_bets if b.answer_id == answer.id)

    if board_bets_total + amount > MAX_BETS_PER_ROUND:
        return jsonify({"error": "Maximum bet amount per round is %d." % MAX_BETS_PER_ROUND})
    
    bet = db_session.query(AnswerBet).filter_by(answer_id = answer.id, player_id = session[str(board.game_id)]["id"]).first()
    if not bet:
        bet = AnswerBet(
                player_id = int(session[str(board.game_id)]["id"]),
                user_id = 0,
                answer_id = int(answer.id),
                amount = 0)

    bet.amount = amount

    if game_player.coins + (answer_bets_total - amount) < 0:
        return jsonify({"error": "You only have %d coins. Can't bet %d." % (game_player.coins, amount)})

    game_player.coins += (answer_bets_total - amount)
    db_session.add(game_player)
    db_session.add(bet)
    db_session.commit()
    socketio.emit("wits", {"update": ["answers", "leaderboard"]}, broadcast=True)
    print ("Broadcase emmited: answers, leaderboard") 

    return jsonify({"error": ""})

@app.route('/api/wits/game/board/<id>/answer', methods = ['POST'])
def api_add_answers(id):
    db_session = Session()
    board_id = id

    try:
        answer_value = float(request.get_json()["answer"])
    except ValueError:
        return jsonify({"error": "Answer value can't be parsed as a number."})

    if answer_value <= ANSWER_NEGATIVE_LIMIT:
        return jsonify({"error": "Answer has to be larger than -1e6."})

    board = db_session.query(GameBoard).filter_by(id = board_id).first()
    if not board:
        return jsonify({"error", "Can't find active board for this game."})

    answer = db_session.query(BoardAnswer).filter_by(
            player_id = int(session[str(board.game_id)]["id"]), board_id = int(board_id)).first()
    if answer:
        return jsonify("error", "You already answered %f." % round(answer.answer, 1))

    answer = BoardAnswer(
            board_id = int(board_id),
            player_id = int(session[str(board.game_id)]["id"]),
            answer = answer_value
            )
    db_session.add(answer)
    db_session.commit()

    socketio.emit("wits", {"update": ["answers"]}, broadcast=True)
    return jsonify({"error": "", "answer": answer.as_dict(db_session)})

@app.route('/api/wits/add_question', methods = ['POST'])
def api_add_question():
    db_session = Session()

    question = get_string_from_request_json(request, "question")
    try:
        answer = float(request.get_json()["answer"])
    except ValueError:
        return jsonify({"error": "Answer value can't be parsed as a number."})

    notes = get_string_from_request_json(request, "notes")
    category = get_string_from_request_json(request, "category")

    q = WitsQuestion(
                question = question,
                answer = answer,
                notes = notes,
                category = category
            )
    db_session.add(q)
    db_session.commit()
    return jsonify({"error": ""})

@app.route('/api/wits/questions', methods = ['get'])
def api_get_questions():
    db_session = Session()
    questions = db_session.query(WitsQuestion).all()
    q = []
    for question in questions:
        q.append(question.as_dict(None))
    return jsonify({"error": "", "questions": q})

@app.route('/codenames/game/<id>')
def codenames_game(id):
    return render_template("codenames/codenames.html")

@app.route('/api/wits/create', methods=['POST'])
def wits_create():
    db_session = Session()
    game = Game(
        name = request.get_json()["name"],
        state = 1,
    )
    db_session.add(game)
    db_session.commit()

    new_board = create_new_board_for_game(game, db_session)
    db_session.add(new_board)
    db_session.commit()
    return {"error": "", "game": game.as_dict(db_session)}

@app.route('/api/wits/delete/<id>', methods=['DELETE'])
def wits_api_delete():
    db_session.query(Game).filter_by(id = request.get_json()["id"]).update({"state": 2})
    db_session.commit()
    return {"error": "", "game": game.as_dict(db_session)}

@app.route('/api/wits/game/board/<id>/advance', methods=['POST'])
def wits_advance(id):
    db_session = Session()

    board_id = id
    from_phase = int(request.get_json()["from_phase"])
    answer_value_str = request.get_json()["answer_value"]

    board = db_session.query(GameBoard).filter_by(id = board_id).first()

    if not board:
        return jsonify({"error": "Can't find the board."})

    if board.phase != from_phase:
        return jsonify({"error": "Can't advance game to this state. %d %d" % (board.phase, from_phase)});

    game = db_session.query(Game).filter_by(id = board.game_id).first()

    all_answers = db_session.query(BoardAnswer).filter_by(board_id = board.id).order_by(BoardAnswer.answer).all()
    odds = 3
    if board.phase == ANSWERING_PHASE:
        # Calculate answers odds
        if all_answers:
            buckets = [[all_answers[0]]]
            for i in range(1, len(all_answers)):
                if abs(all_answers[i].answer - buckets[len(buckets) - 1][0].answer) < 0.01:
                    buckets[len(buckets) - 1].append(all_answers[i])
                else:
                    buckets.append([all_answers[i]])
            up, bt = 0, 0
            if len(buckets) % 2 == 0:
                up, bt = len(buckets) // 2, len(buckets) // 2 - 1
            else:
                up, bt = len(buckets) // 2 + 1, len(buckets) // 2 - 1
                for answer in buckets[len(buckets) // 2]:
                    answer.odds = 2
                    db_session.add(answer)

            while bt >= 0:
                for answer in buckets[bt]:
                    answer.odds = min(5, odds)
                    db_session.add(answer)
                for answer in buckets[up]:
                    answer.odds = min(5, odds)
                    db_session.add(answer)
                odds += 1
                bt -= 1
                up += 1

        # Add lowest answer
        low = BoardAnswer(
                board_id = int(board_id),
                player_id = -1,
                answer = ANSWER_NEGATIVE_LIMIT,
                odds = min(odds, 6)
                )
        db_session.add(low)

        board.phase = BETTING_PHASE
    elif board.phase == BETTING_PHASE:
        players = db_session.query(GamePlayer).filter_by(game_id = board.game_id).all()
        question = db_session.query(WitsQuestion).filter_by(id = board.question_id).first()
        if not question:
            return jsonify({"error": "Question can't be found."})

        answer_value = question.answer

        winning_answer = None
        for i in range(len(all_answers)):
            if all_answers[i].answer <= answer_value and (i + 1 == len(all_answers) or all_answers[i+1].answer > answer_value):
                winning_answer = all_answers[i].answer

        if winning_answer:
            for ans in all_answers:
                if abs(ans.answer - winning_answer) < 0.01:
                    answer_bets = db_session.query(AnswerBet).filter_by(answer_id = ans.id).all()
                    db_session.add(ans)
                    player_changed = False
                    ans.won = 1
                    for p in players:
                        # Give coins to the closest (or correct) guesses
                        if str(p.id) == str(ans.player_id):
                            p.num_wins += 1
                            if abs(answer_value - winning_answer) < 0.01:
                                p.coins += 2
                                ans.won = 2
                            else:
                                p.coins += 1
                                ans.won = 1
                            player_changed = True
                        for bet in answer_bets:
                            if str(bet.player_id) == str(p.id):
                                p.coins += bet.amount * ans.odds
                                player_changed = True
                        if player_changed:
                            db_session.add(p)

        board.answer = answer_value
        board.phase = BOARD_FINALIZED
    elif board.phase == BOARD_FINALIZED:
        new_board = create_new_board_for_game(game, db_session)
        db_session.add(new_board)
        board.active = 0

    db_session.add(board)
    db_session.commit()
    socketio.emit("wits", {"update": ["game"]}, broadcast=True)

    return jsonify({"error": ""})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    socketio.run(app)

