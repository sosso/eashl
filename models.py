from dbutils import get_or_create
from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy import Column, Integer, VARCHAR, INTEGER
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import sessionmaker, object_session
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import or_, desc
from sqlalchemy.types import String, Boolean, DateTime
import datetime
import logging
import os
# from passlib.hash import sha256_crypt

# if os.environ.get('TEST_RUN', "False") == "True":
#    engine = create_engine('mysql://anthony:password@127.0.0.1:3306/test_assassins', echo=False, pool_recycle=3600)  # recycle connection every hour to prevent overnight disconnect)
# engine = create_engine('mysql://b2970bc5c51ab9:96b6d5d8@us-cdbr-east-02.cleardb.com/heroku_ee20403d72a96df', echo=False, pool_recycle=3600)  # recycle connection every hour to prevent overnight disconnect)
engine = create_engine('mysql://anthony:password@127.0.0.1:3306/eashlhistory2', echo=False, pool_recycle=3600)  # recycle connection every hour to prevent overnight disconnect)
Base = declarative_base(bind=engine)
sm = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)
Session = scoped_session(sm)
logging.basicConfig(level=logging.DEBUG)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(length=255), nullable=False)
    
    def __init__(self, username):
        self.username = username
        
    games = relationship('UserGame', primaryjoin='UserGame.user_id==User.id')

class Game(Base):
    __tablename__ = 'game'
    id = Column(INTEGER(), primary_key=True)
    ea_id = Column(VARCHAR(255), primary_key=True)
    time = Column(VARCHAR(10), primary_key=True)  # format is ##:## [AM, PM]
    ea_page_timestamp = Column(VARCHAR(255))
    datetime = Column(DateTime)
    club_1_id = Column(Integer, ForeignKey('club.id'), primary_key=True)
    club_1_score = Column(INTEGER(), default=-1)
    club_1_div_rank = Column(INTEGER(), default=-1)
    club_1_division = Column(VARCHAR(10), default='')
    club_1_members = Column(INTEGER(), default=-1)
    club_1_overall_rank = Column(INTEGER(), default=-1)
    club_1_record = Column(VARCHAR(30), default='')
    club_2_id = Column(Integer, ForeignKey('club.id'), primary_key=True)
    club_2_score = Column(INTEGER(), default=-1)        
    club_2_div_rank = Column(INTEGER(), default=-1)
    club_2_division = Column(VARCHAR(10), default='')
    club_2_members = Column(INTEGER(), default=-1)
    club_2_overall_rank = Column(INTEGER(), default=-1)
    club_2_record = Column(VARCHAR(30), default='')
    

    def __init__(self, ea_id, club_1_id, club_1_score, club_2_id, club_2_score, time, ea_page_timestamp):
        self.ea_id = ea_id
        self.club_1_id = club_1_id
        self.club_1_score = club_1_score
        self.club_2_id = club_2_id
        self.club_2_score = club_2_score
        self.time = time
        self.ea_page_timestamp = ea_page_timestamp
        
    def update_rank_info(self, rank_info_list):
        self.club_1_div_rank = rank_info_list[0]['div_rank']
        self.club_1_division = rank_info_list[0]['division']
        self.club_1_members = rank_info_list[0]['members']
        self.club_1_overall_rank = rank_info_list[0]['overall_rank']
        self.club_1_record = rank_info_list[0]['record']
        self.club_2_div_rank = rank_info_list[1]['div_rank']
        self.club_2_division = rank_info_list[1]['division']
        self.club_2_members = rank_info_list[1]['members']
        self.club_2_overall_rank = rank_info_list[1]['overall_rank']
        self.club_2_record = rank_info_list[1]['record']
        s = object_session(self)
        s.add(self)
        s.flush()
        s.commit()
    
    def game_date(self):
        if self.ea_page_timestamp is None:
            return None
        mydate = datetime.datetime.fromtimestamp(float(self.ea_page_timestamp)).date()
        pass
        return mydate
    
    def get_rank_info(self, club_id):
        ret_dict = {}
        if club_id == self.club_1_id:
            ret_dict = dict(div_rank=self.club_1_div_rank, division=self.club_1_division, members=self.club_1_members,\
                            overall_rank=self.club_1_overall_rank, record=self.club_1_record)
        elif club_id == self.club_2_id:
            ret_dict = dict(div_rank=self.club_2_div_rank, division=self.club_2_division, members=self.club_2_members,\
                            overall_rank=self.club_2_overall_rank, record=self.club_2_record)
        return ret_dict
        

class Club(Base):
    __tablename__ = 'club'
    id = Column(INTEGER(), primary_key=True, nullable=False)
    ea_id = Column(VARCHAR(length=255), nullable=False)
    abbr = Column(VARCHAR(length=3), nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)
    logo = Column(VARCHAR(length=255), nullable=False)
    last_rank_fetch = Column(DateTime, default=None, nullable=True)
    
    def __init__(self, ea_id, name, abbr, logo='http://i.imgur.com/rqJBJQy.png'):
        self.ea_id = ea_id
        self.name = name
        self.abbr = abbr
        self.logo = logo
    
    def should_update(self, timestamp=None):
        if self.last_rank_fetch is None:
            return True
        if timestamp is None:
            timestamp = datetime.datetime.now()
        return (timestamp - datetime.timedelta(minutes = 20)) > self.last_rank_fetch
    
    def get_games(self):
        return object_session(self).query(Game).filter_by(or_(Game.club_1_id == self.id, Game.club_2_id == self.id)).all()

    def most_recent_rank_info(self):
        game = object_session(self).query(Game).filter(or_(Game.club_1_id == self.id, Game.club_2_id == self.id)).order_by(desc(Game.ea_id)).limit(1).first()
        return game.get_rank_info(self.id)
        
    def update_logo(self, logo=None):
        if logo is not None:            
            self.logo = logo
            
    def update_last_rank_fetch(self, dt):
        self.last_rank_fetch = dt
        s = object_session(self)
        s.add(self)
        s.flush()
        s.commit()
               

class UserGame(Base):
    __tablename__ = 'user_game'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
    club_id = Column(Integer, ForeignKey('club.id'), primary_key=True)
    
    position = Column(VARCHAR(2))
    points = Column(Integer)
    hits = Column(Integer)

    user = relationship(User, primaryjoin=User.id == user_id)
    game = relationship(Game, primaryjoin=Game.id == game_id)
    
    def __init__(self, game_id, club_id, position, points, hits, username):
        self.user_id = get_or_create(Session(), User, username=username).id  
        self.game_id = game_id
        self.club_id = club_id
        self.position = position
        self.points = points
        self.hits = hits

    def __repr__(self):
        return '<UserGame %s @ %d>' % (self.user.username, self.game_id)

#    def get_api_response_dict(self):
#        response_dict = {'game_id':self.game_id, \
#                'game_password':self.game.password, \
#                'game_friendly_name': self.game.title, \
#                'alive':self.alive, \
#                'is_game_master':self.is_game_master, \
#                'started':self.game.started, \
#                'completed':self.game.over, \
#                'pending_shot':self.pending_shot}
#        return response_dict

def clear_all():
    for table in reversed(Base.metadata.sorted_tables):
        engine.execute(table.delete())
        
def get_games_for_user(id):
    return Session.query(UserGame, Game).filter(UserGame.user_id==id).filter(UserGame.game_id==Game.id).all()
    
Base.metadata.create_all(engine)
