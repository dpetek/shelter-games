from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask_cors import CORS
from flask_sockets import Sockets
from markupsafe import escape
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float, desc, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from constants import *
import re
import random
import sqlalchemy

MAX_BETS_PER_ROUND = 50
INITIAL_GAME_COINS = 10

def create_app():
  app = Flask(__name__)
  app.secret_key = "space-secret"
  app.config["SECRET_KEY"] = "space-secret"
  return app

app = create_app()
sockets = Sockets(app)

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
    pool_size = 30,
    max_overflow = 10
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

class WitsQuestion(Base):
    __tablename__ = 'wits_question'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer  = Column(Float)
    notes = Column(Text)
    category = Column(String)

def question_to_dict(question, board = None):
    return dict({
        "id": question.id,
        "question": question.question,
        "answer": question.answer if not board or board.phase >= 2 else None,
        "notes": question.notes,
        "category": question.category
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
    question_id = Column(Integer, ForeignKey("wits_question.id"))
    question = relationship("WitsQuestion")
    answer = Column(Float)

def board_to_dict(board):
    return dict({
        "id": board.id,
        "game_id": board.game_id,
        "question_file": board.question_file,
        "answer_file": board.answer_file,
        "phase": board.phase,
        "active": board.active,
        "answer": board.answer,
        "question": question_to_dict(board.question, board) if board.question else None
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

def answer_to_dict(answer):
    return dict({
        "id": answer.id,
        "board_id": answer.board_id,
        "board": board_to_dict(answer.board) if answer.board else None,
        "user_id": answer.user_id,
        "user": user_to_dict(answer.user) if answer.user else None,
        "answer": answer.answer,
        "won": answer.won
    })

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

def create_player(game_id, user_id, db_session):
    game_player = GamePlayer(
        game_id = game_id,
        user_id = user_id,
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

def logged_in():
    return ("user" in session) and session["user"]

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
    session["user"] = user_to_dict(user)

    return jsonify({"error": "", "user": user_to_dict(user)})

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
    return jsonify({"error": "", "user": user_to_dict(current_user)})

@app.route('/api/wits/games', methods = ['GET'])
@app.route('/api/wits/games/', methods = ['GET'])
def api_get_wits_games():
    db_session = Session()
    games = db_session.query(Game).filter_by(state = 1).all()
    g = []
    for game in games:
        g.append(game_to_dict(game))
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

    return jsonify({"error": "", "game": game_to_dict(game), "board": board_to_dict(board)})

@app.route('/api/wits/game/<id>/players', methods = ['GET'])
def api_get_wits_game_players(id):
    db_session = Session()
    players = db_session.query(GamePlayer).filter_by(game_id = id).order_by(desc(GamePlayer.coins)).all()
    p = []
    for player in players:
        p.append(player_to_dict(player))
    return jsonify({"error": "", "players": p})

@app.route('/api/wits/game/board/<id>/answers', methods = ['GET'])
def api_get_board_answers(id):
    db_session = Session()
    answers = db_session.query(BoardAnswer).filter_by(board_id = id).all()
    ids = [a.id for a in answers]
    board_bets = db_session.query(AnswerBet).filter(AnswerBet.answer_id.in_(ids)).all()

    for bet in board_bets:
        print("Found bet: board: %d answer:%d bet:%d amount:%d" % (bet.answer.board.id, bet.answer.id, bet.id, bet.amount))

    a = []
    for answer in answers:
        answer_dict = answer_to_dict(answer)
        for bet in board_bets:
            if str(bet.answer.id) == str(answer_dict["id"]):
                if not "bets" in answer_dict:
                    answer_dict["bets"] = []
                answer_dict["bets"].append(answer_bet_to_dict(bet))
        a.append(answer_dict)
        
    return jsonify({"error": "", "answers": a})

@app.route('/api/wits/game/answer/<id>/bet', methods = ['POST'])
def api_bet_on_answer(id):
    db_session = Session()

    if not "user" in session:
        return jsonify({"error": "User must be logged in to bet on answers."})

    answer = db_session.query(BoardAnswer).filter_by(id = id).first()

    if not answer:
        return jsonify({"error": "Can't find answer for id %d" % id})

    amount_str = get_string_from_request_json(request, "amount")
    amount = 0
    try:
        amount = int(amount_str)
    except ValueError:
        return jsonify({"error": "Can't parse %s as integer amount." % amount_str})

    game_player = db_session.query(GamePlayer).filter_by(user_id = session["user"]["id"], game_id = answer.board.game.id).first()
    if not game_player:
        game_player = GamePlayer(
            game_id = answer.board.game.id,
            user_id = session["user"]["id"],
            coins = INITIAL_GAME_COINS,
            num_wins = 0
        )
        db_session.add(game_player)

    answers = db_session.query(BoardAnswer).filter_by(board_id = answer.board.id).all()
    ids = [a.id for a in answers]

    user_board_bets = db_session.query(AnswerBet).filter_by(user_id = session["user"]["id"]).filter(AnswerBet.answer_id.in_(ids)).all()
    for b in user_board_bets:
        print("User board bets %s" % b.user.name)

    board_bets_total = 0
    answer_bets_total = 0
    if user_board_bets:
        board_bets_total = sum(b.amount for b in user_board_bets if b.answer.id != answer.id)
        answer_bets_total = sum(b.amount for b in user_board_bets if b.answer.id == answer.id)

    if board_bets_total + amount > MAX_BETS_PER_ROUND:
        return jsonify({"error": "Maximum bet amount per round is %d." % MAX_BETS_PER_ROUND})
    
    bet = db_session.query(AnswerBet).filter_by(answer_id = answer.id, user_id = session["user"]["id"]).first()
    if not bet:
        bet = AnswerBet(
                user_id = int(session["user"]["id"]),
                answer_id = int(answer.id),
                amount = 0)
    bet.amount = amount

    if game_player.coins + (answer_bets_total - amount) < 0:
        return jsonify({"error": "You only have %d coins. Can't bet %d." % (game_player.coins, amount)})

    game_player.coins += (answer_bets_total - amount)
    db_session.add(game_player)
    db_session.add(bet)
    db_session.commit()

    return jsonify({"error": ""})

@app.route('/api/wits/game/board/<id>/answer', methods = ['POST'])
def api_add_answers(id):
    db_session = Session()
    board_id = id

    try:
        answer_value = float(request.get_json()["answer"])
    except ValueError:
        return jsonify({"error": "Answer value can't be parsed as a number."})

    board = db_session.query(GameBoard).filter_by(id = board_id).first()
    if not board:
        return jsonify({"error", "Can't find active board for this game."})

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

    return jsonify({"error": "", "answer": answer_to_dict(answer)})

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
    return {"error": "", "game": game_to_dict(game)}

@app.route('/api/wits/delete/<id>', methods=['DELETE'])
def wits_api_delete():
    db_session = Session()
    db_session.query(Game).filter_by(id = request.get_json()["id"]).update({"state": 2})
    db_session.commit()
    return {"error": "", "game": game_to_dict(game)}

@app.route('/api/wits/game/board/<id>/advance', methods=['POST'])
def wits_advance(id):
    db_session = Session()
    if not "user" in session:
        return jsonify({"error": "User must be logged in."})

    board_id = id
    from_phase = int(request.get_json()["from_phase"])
    answer_value_str = request.get_json()["answer_value"]

    board = db_session.query(GameBoard).filter_by(id = board_id).first()

    if not board:
        return jsonify({"error": "Can't find the board."})

    if board.phase != from_phase:
        return jsonify({"error": "Can't advance game to this state. %d %d" % (board.phase, from_phase)});

    if board.phase == ANSWERING_PHASE:
        board.phase = BETTING_PHASE
    elif board.phase == BETTING_PHASE:
        all_answers = db_session.query(BoardAnswer).filter_by(board_id = board.id).order_by(BoardAnswer.answer).all()
        players = db_session.query(GamePlayer).filter_by(game_id = board.game_id).all()

        answer_value = board.question.answer

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
        new_board = create_new_board_for_game(board.game, db_session)
        db_session.add(new_board)
        board.active = 0

    db_session.add(board)
    db_session.commit()

    return jsonify({"error": ""})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
