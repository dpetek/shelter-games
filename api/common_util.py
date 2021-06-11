from contextlib import contextmanager
from sqlalchemy.orm import scoped_session
from init import Session
import models.common as common
import random
import string

def get_game_code(db_session):
    while True:
        letters = string.ascii_uppercase
        code = ''.join(random.choice(letters) for i in range(4))
        game = db_session.query(common.Game).filter(common.Game.code == code).first()
        if not game:
            return code
        print ("Game code collision: ", code)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = scoped_session(Session)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()



