from api_resource import ApiResource
from init import Base as DeclarativeBase
from sqlalchemy import Column, Integer, String

class Game(DeclarativeBase, ApiResource):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state  = Column(Integer)
    code = Column(String)
    type = Column(String)

class User(DeclarativeBase, ApiResource):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column( String)
    admin = Column( Integer)
