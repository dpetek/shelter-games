from api.common_util import get_game_code
from constants import *
from flask import jsonify
from flask import request
from flask import session
from flask_socketio import emit, send
from init import app, Session, socketio
from sqlalchemy import desc
from sqlalchemy.sql.expression import func
import models.common as common
import models.codenames as codenames

def create_new_board_for_game(game, db_session):
    Pass

@app.route('/api/codenames/create', methods=['POST'])
def create_game():
    db_session = Session()

    code = get_game_code(db_session)

    game = common.Game(
        name = request.get_json()["name"],
        state = 1,
        code = code,
        type = "codenames"
    )
    db_session.add(game)
    db_session.commit()

    db_session.add(new_board)
    db_session.commit()
    return {"error": "", "game": game.as_dict(db_session)}

