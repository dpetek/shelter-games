from common_util import get_game_code
from constants import *
from flask import jsonify
from flask import request
from flask import session
from flask_socketio import emit, send
from init import app, Session, socketio
from sqlalchemy import desc
from sqlalchemy.sql.expression import func
import models.common as common
import models.wits as wits

def verify_username(username):
    return True

def create_player(game_id, user_id, avatar, db_session):
    game_player = wits.Player(
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

def create_new_board_for_game(game, db_session):
    rand_question = db_session.query(wits.Question).order_by(func.random()).first()

    board = wits.Board(
        game_id = game.id,       
        question_id = rand_question.id,
        question_file = "",
        answer_file = "",
        phase = ANSWERING_PHASE,
        active = 1
    )
    db_session.add(board)
    return board

@app.route('/api/wits/games/', methods = ['GET'])
@app.route('/api/wits/games', methods = ['GET'])
def get_games():
    db_session = Session()
    games = db_session.query(common.Game).filter_by(state = 1).all()
    g = []
    for game in games:
        g.append(game.as_dict(db_session))
    return jsonify({"games": g})

@app.route('/api/wits/game/<code>', methods = ['GET'])
def get_game(code):
    db_session = Session()
    game = db_session.query(common.Game).filter_by(code = code).first()
    if not game:
        return jsonify({"error": "Game not found."})

    board = db_session.query(wits.Board).filter_by(game_id = game.id, active = 1).first()
    if not board:
        return jsonify({"error": "Game board not found."})

    return jsonify({"error": "", "game": game.as_dict(db_session), "board": board.as_dict(db_session)})

@app.route('/api/wits/create', methods=['POST'])
def create_game():
    db_session = Session()

    code = get_game_code(db_session)

    game = common.Game(
        name = request.get_json()["name"],
        state = 1,
        code = code,
        type = "wits"
    )
    db_session.add(game)
    db_session.commit()

    new_board = create_new_board_for_game(game, db_session)
    db_session.add(new_board)
    db_session.commit()
    return {"error": "", "game": game.as_dict(db_session)}

@app.route('/api/wits/delete/<code>', methods=['DELETE'])
def delete_game():
    db_session.query(common.Game).filter_by(code = request.get_json()["id"]).update({"state": 2})
    db_session.commit()
    return {"error": "", "game": game.as_dict(db_session)}

@app.route('/api/wits/game/<code>/players', methods = ['GET'])
def get_players(code):
    db_session = Session()
    game = db_session.query(common.Game).filter_by(code = code).first()
    if not game:
        return jsonify({"error": "Game not found."})

    players = db_session.query(wits.Player).filter_by(game_id = game.id).order_by(desc(wits.Player.coins)).all()
    p = []
    
    for player in players:
        p.append(player.as_dict(db_session))

    return jsonify({"error": "", "players": p})

@app.route('/api/wits/game/<code>/current_player', methods = ['GET'])
def api_game_current_player(code):
    db_session = Session()
    game = db_session.query(common.Game).filter_by(code = code).first()
    if not game:
        return jsonify({"error": "Game not found."})

    if not game.code in session:
        return jsonify({"error": "Player not selected."})
    if "betting_coins_remaining" not in session[game.code]:
        session[game.code]["betting_coins_remaining"] = session[game.code]["coins"]
    return jsonify({"error": "", "player": session[game.code]})


@app.route('/api/wits/game/<code>/enter', methods = ['POST'])
def api_enter_game(code):
    db_session = Session()

    name = get_string_from_request_json(request, "name")
    if not verify_username(name):
        return jsonify({"error": "Wrong name format. Allowed special characters are numbers, '_' and '-'"})

    password = get_string_from_request_json(request, "password")
    returning = get_string_from_request_json(request, "returning")
    avatar = get_string_from_request_json(request, "avatar")

    if not avatar:
        return jsonify({"error": "You have to select your avatar."})

    game = db_session.query(common.Game).filter(common.Game.code == code).first()
    if not game:
        return jsonify({"error": "Can't find the game."})

    player = db_session.query(wits.Player).filter_by(name = name).first()

    if player:
        if password == hash(password):
            session[game.code] = player.as_dict(None)
            return jsonify({"error": "", "player": session[game.code]})
        return jsonify({"error": "User %s is already in the game with different password." % name})

    player = wits.Player(
            name = name,
            password = hash(password),
            user_id = 0,
            avatar = avatar,
            game_id = game.id,
            coins = INITIAL_GAME_COINS,
            num_wins = 0
            )
    db_session.add(player)
    db_session.commit()
    session[game.code] = player.as_dict(None)
    session[game.code]["betting_coins_remaining"] = player.coins
    socketio.emit("wits", {"update": ["leaderboard"]}, broadcast=True)
    return jsonify({"error": "", "player": session[game.code]})

@app.route('/api/wits/game/board/<id>/answer', methods = ['POST'])
def answer_question(id):
    db_session = Session()
    board_id = id

    try:
        answer_value = float(request.get_json()["answer"])
    except ValueError:
        return jsonify({"error": "Answer value can't be parsed as a number."})

    if answer_value <= ANSWER_NEGATIVE_LIMIT:
        return jsonify({"error": "Answer has to be larger than -1e6."})

    board = db_session.query(wits.Board).filter_by(id = board_id).first()
    if not board:
        return jsonify({"error", "Can't find active board for this game."})

    game = db_session.query(common.Game).filter_by(id = board.game_id).first()
    if not game:
        return jsonify({"error": "Game not found."})

    answer = db_session.query(wits.Answer).filter_by(
            player_id = int(session[game.code]["id"]), board_id = int(board_id)).first()
    if answer:
        return jsonify("error", "You already answered %f." % round(answer.answer, 1))

    answer = wits.Answer(
            board_id = int(board_id),
            player_id = int(session[game.code]["id"]),
            answer = answer_value
            )
    db_session.add(answer)
    db_session.commit()

    socketio.emit("wits", {"update": ["answers"]}, broadcast=True)
    return jsonify({"error": "", "answer": answer.as_dict(db_session)})

@app.route('/api/wits/game/board/<id>/answers', methods = ['GET'])
def get_answers(id):
    db_session = Session()

    board = db_session.query(wits.Board).filter_by(id = id).first()
    if not board:
        return jsonify({"error": "Board can't be found."})

    answers = db_session.query(wits.Answer).filter_by(board_id = id).order_by(wits.Answer.answer).all()

    ids = [a.id for a in answers]
    board_bets = db_session.query(wits.Bet).filter(wits.Bet.answer_id.in_(ids)).all()

    game = db_session.query(common.Game).filter(common.Game.id == board.game_id).first()
    if not game:
        return jsonify({"error": "Game can't be found."})

    a = []
    for answer in answers:
        if board.phase == 1:
            if not game.code in session or str(session[game.code]["id"]) != str(answer.player_id):
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
def bet_on_answer(id):
    db_session = Session()

    answer = db_session.query(wits.Answer).filter_by(id = id).first()
    if not answer:
        return jsonify({"error": "Can't find answer for id %d" % id})

    amount_str = request.get_json()["amount"]
    amount = 0
    try:
        amount = int(amount_str)
    except ValueError:
        return jsonify({"error": "Can't parse %s as integer amount." % amount_str})

    if amount < 0:
        return jsonify({"error": "Come on. You can't bet negative amount."});

    board = db_session.query(wits.Board).filter_by(id = answer.board_id).first()
    if not board:
        return jsonify({"error": "Board can't be found."});

    game = db_session.query(common.Game).filter_by(id = board.game_id).first()
    if not game:
        return jsonofy({"error": "Game not found."})

    game_player = db_session.query(wits.Player).filter_by(id = session[game.code]["id"]).first()

    if not game_player:
        return jsonify({"error": "Game player can't be found. Please refresh the page."})

    answers = db_session.query(wits.Answer).filter_by(board_id = answer.board_id).all()
    ids = [a.id for a in answers]

    player_board_bets = db_session.query(wits.Bet).filter_by(player_id = session[game.code]["id"]).filter(wits.Bet.answer_id.in_(ids)).all()

    board_bets_total = 0
    answer_bets_total = 0
    if player_board_bets:
        board_bets_total = sum(b.amount for b in player_board_bets if b.answer_id != answer.id)
        answer_bets_total = sum(b.amount for b in player_board_bets if b.answer_id == answer.id)

    board_bets_total += (answer_bets_total - amount)
    if board_bets_total > MAX_BETS_PER_ROUND:
        return jsonify({"error": "Maximum bet amount per round is %d." % MAX_BETS_PER_ROUND})

    
    bet = db_session.query(wits.Bet).filter_by(answer_id = answer.id, player_id = session[game.code]["id"]).first()
    if not bet:
        bet = wits.Bet(
                player_id = int(session[game.code]["id"]),
                user_id = 0,
                answer_id = int(answer.id),
                amount = 0)

    bet.amount = amount

    if game_player.coins + (answer_bets_total - amount) < 0:
        return jsonify({"error": "You only have %d coins. Can't bet %d more." % (game_player.coins, amount - answer_bets_total)})

    game_player.coins += (answer_bets_total - amount)

    session[game.code]["betting_coins_remaining"] = max(0, min(game_player.coins, MAX_BETS_PER_ROUND - board_bets_total))

    db_session.add(game_player)
    db_session.add(bet)
    db_session.commit()
    socketio.emit("wits", {"update": ["answers", "leaderboard"]}, broadcast=True)
    print ("Broadcase emmited: answers, leaderboard") 

    return jsonify({"error": ""})

@app.route('/api/wits/add_question', methods = ['POST'])
def add_question():
    db_session = Session()

    question = get_string_from_request_json(request, "question")
    try:
        answer = float(request.get_json()["answer"])
    except ValueError:
        return jsonify({"error": "Answer value can't be parsed as a number."})

    notes = get_string_from_request_json(request, "notes")
    category = get_string_from_request_json(request, "category")

    q = wits.Question(
                question = question,
                answer = answer,
                notes = notes,
                category = category
            )
    db_session.add(q)
    db_session.commit()
    return jsonify({"error": ""})

@app.route('/api/wits/questions', methods = ['get'])
def get_questions():
    db_session = Session()
    questions = db_session.query(wits.Question).all()
    q = []
    for question in questions:
        q.append(question.as_dict(None))
    return jsonify({"error": "", "questions": q})

@app.route('/api/wits/game/board/<id>/advance', methods=['POST'])
def wits_advance(id):
    db_session = Session()

    board_id = id
    from_phase = int(request.get_json()["from_phase"])
    answer_value_str = request.get_json()["answer_value"]

    board = db_session.query(wits.Board).filter_by(id = board_id).first()

    if not board:
        return jsonify({"error": "Can't find the board."})

    if board.phase != from_phase:
        return jsonify({"error": "Can't advance game to this state. %d %d" % (board.phase, from_phase)});

    game = db_session.query(common.Game).filter_by(id = board.game_id).first()

    all_answers = db_session.query(wits.Answer).filter_by(board_id = board.id).order_by(wits.Answer.answer).all()
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
        low = wits.Answer(
                board_id = int(board_id),
                player_id = -1,
                answer = ANSWER_NEGATIVE_LIMIT,
                odds = min(odds, 6)
                )
        db_session.add(low)

        board.phase = BETTING_PHASE
    elif board.phase == BETTING_PHASE:
        players = db_session.query(wits.Player).filter_by(game_id = board.game_id).all()
        question = db_session.query(wits.Question).filter_by(id = board.question_id).first()
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
                    answer_bets = db_session.query(wits.Bet).filter_by(answer_id = ans.id).all()
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
