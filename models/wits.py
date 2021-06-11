from models.api_resource import ApiResource
from init import Base as DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Text
from models.common import *

class Question(DeclarativeBase, ApiResource):
    __tablename__ = 'wits_question'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer  = Column(Float)
    notes = Column(Text)
    category = Column(String)


class Player(DeclarativeBase, ApiResource):
    __tablename__ = 'game_player'
    id =  Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    avatar = Column(String)
    game_id = Column(Integer)
    user_id = Column(Integer)
    coins = Column(Integer)
    num_wins = Column(Integer)
    is_admin = Column(Integer)

    def as_dict(self, db_session):
        ret = super(Player, self).as_dict(db_session)
        del ret["password"]
        if not db_session:
            return ret
        if self.game_id:
            game = db_session.query(Game).filter(Game.id == self.game_id).first()
            ret["game"] = game.as_dict(None)
        if self.user_id:
            user = db_session.query(User).filter(User.id == self.user_id).first()
            ret["user"] = user.as_dict(None)
        return ret

class Board(DeclarativeBase, ApiResource):
    __tablename__ = 'game_board'
    id =  Column(Integer, primary_key=True)
    game_id = Column(Integer)
    question_file = Column(String)
    answer_file = Column(String)
    phase = Column(Integer)
    active = Column(Integer)
    question_id = Column(Integer)
    version = Column(Integer)
    answer = Column(Float)

    def as_dict(self, db_session):
        ret = super(Board, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.question_id:
            question = db_session.query(Question).filter(Question.id == self.question_id).first()
            ret["question"] = question.as_dict(None)
        if self.game_id:
            game = db_session.query(Game).filter(Game.id == self.game_id).first()
            ret["game"] = game.as_dict(None)
        return ret

class Answer(DeclarativeBase, ApiResource):
    __tablename__ = 'board_answer'
    id =  Column(Integer, primary_key=True)
    board_id = Column(Integer)
    # user_id = Column(Integer)
    player_id = Column(Integer)
    answer = Column(Float)
    won = Column(Integer)
    odds = Column(Integer)

    def as_dict(self, db_session):
        ret = super(Answer, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.board_id:
            board = db_session.query(Board).filter(Board.id == self.board_id).first()
            ret["board"] = board.as_dict(None)
        if self.player_id:
            player = db_session.query(Player).filter(Player.id == self.player_id).first()
            if player:
                ret["player"] = player.as_dict(None)
        return ret

class Bet(DeclarativeBase, ApiResource):
    __tablename__ = 'answer_bet'
    id =  Column(Integer, primary_key=True)
    answer_id = Column(Integer)
    user_id = Column(Integer)
    player_id = Column(Integer)
    amount = Column(Integer)

    def as_dict(self, db_session):
        ret = super(Bet, self).as_dict(db_session)
        if not db_session:
            return ret
        if self.answer_id:
            answer = db_session.query(Answer).filter(Answer.id == self.answer_id).first()
            ret["answer"] = answer.as_dict(None)
        if self.player_id:
            player = db_session.query(Player).filter(Player.id == self.player_id).first()
            ret["player"] = player.as_dict(None)
        return ret
