from dbutils import get_or_create
from sqlalchemy import Column, Integer, VARCHAR, INTEGER
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import sessionmaker, object_session
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import or_, desc, and_
from sqlalchemy.types import String, Boolean, DateTime
import datetime
import logging
import os
# from passlib.hash import sha256_crypt

# if os.environ.get('TEST_RUN', "False") == "True":
#    engine = create_engine('mysql://anthony:password@127.0.0.1:3306/test_assassins', echo=False, pool_recycle=3600)  # recycle connection every hour to prevent overnight disconnect)
engine = create_engine('mysql://b2970bc5c51ab9:96b6d5d8@us-cdbr-east-03.cleardb.com/heroku_ee20403d72a96df', echo=False, pool_recycle=3600)  # recycle connection every hour to prevent overnight disconnect)
#engine = create_engine('mysql://anthony:password@127.0.0.1:3306/eashlhistory2', echo=False, pool_recycle=3600)  # recycle connection every hour to prevent overnight disconnect)
Base = declarative_base(bind=engine)
sm = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)
Session = scoped_session(sm)
logging.basicConfig(level=logging.INFO)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

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
    club_1_score = Column(INTEGER(), default= -1)
    club_1_div_rank = Column(INTEGER(), default= -1)
    club_1_division = Column(VARCHAR(10), default='')
    club_1_members = Column(INTEGER(), default= -1)
    club_1_overall_rank = Column(INTEGER(), default= -1)
    club_1_record = Column(VARCHAR(30), default='')
    club_2_id = Column(Integer, ForeignKey('club.id'), primary_key=True)
    club_2_score = Column(INTEGER(), default= -1)        
    club_2_div_rank = Column(INTEGER(), default= -1)
    club_2_division = Column(VARCHAR(10), default='')
    club_2_members = Column(INTEGER(), default= -1)
    club_2_overall_rank = Column(INTEGER(), default= -1)
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
            ret_dict = dict(div_rank=self.club_1_div_rank, division=self.club_1_division, members=self.club_1_members, \
                            overall_rank=self.club_1_overall_rank, record=self.club_1_record)
        elif club_id == self.club_2_id:
            ret_dict = dict(div_rank=self.club_2_div_rank, division=self.club_2_division, members=self.club_2_members, \
                            overall_rank=self.club_2_overall_rank, record=self.club_2_record)
        return ret_dict
    
    
    club_1 = relationship("Club", primaryjoin='(Club.id==Game.club_1_id)')
    club_1_usergames = relationship("UserGame", primaryjoin='(and_(UserGame.club_id==Game.club_1_id, UserGame.game_id==Game.id))')
    
    club_2 = relationship("Club", primaryjoin='(Club.id==Game.club_2_id)')
    club_2_usergames = relationship("UserGame", primaryjoin='(and_(UserGame.club_id==Game.club_2_id, UserGame.game_id==Game.id))')
    
    def won_by(self, club):
        if club.id == self.club_1_id:
            return self.club_1_score > self.club_2_score
        elif club.id == self.club_2_id:
            return self.club_2_score > self.club_1_score
        else:
            return False
    
    def game_info(self):
        ret_dict = dict(score="%d - %d" % (self.club_1_score, self.club_2_score), \
                    club_1_rank=dict(division=self.club_1_division, rank=self.club_1_div_rank), \
                    club_2_rank=dict(division=self.club_2_division, rank=self.club_2_div_rank))
        ret_dict['club_1_name'] = self.club_1.name
        ret_dict['club_1_logo'] = self.club_1.logo
        ret_dict['club_1_roster'] = [usergame.info() for usergame in self.club_1_usergames]
        
        ret_dict['club_2_roster'] = [usergame.info() for usergame in self.club_2_usergames]
        ret_dict['club_2_name'] = self.club_2.name
        ret_dict['club_2_logo'] = self.club_2.logo
        if self.ea_page_timestamp is not None:
            ret_dict['date'] = datetime.datetime.fromtimestamp(int(self.ea_page_timestamp)).strftime("%Y-%m-%d")
        else:
            ret_dict['date'] = ''
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
        return (timestamp - datetime.timedelta(minutes=20)) > self.last_rank_fetch
    
    def get_games(self, limit=10):
        return object_session(self).query(Game).filter(or_(Game.club_1_id == self.id, Game.club_2_id == self.id)).order_by(desc(Game.ea_id)).limit(limit).all()

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
        
    def display_info(self):
        return self.logo + ";" + self.name
    
    def search_listing(self):
        return {'logo':self.logo, 'name':self.name, 'id':self.id}
               

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
    
    def info(self):
        return dict(position=self.position, points=self.points, hits=self.hits, username=self.user.username)

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
    return Session.query(UserGame, Game).filter(UserGame.user_id == id).filter(UserGame.game_id == Game.id).all()

def get_clubs(id=None, abbr=None, ea_id=None):
    q = Session.query(Club)
    if id is not None:
        q = q.filter(Club.id == id)
    if abbr is not None:
        q = q.filter(Club.abbr == abbr)
    if ea_id is not None:
        q = q.filter(Club.ea_id == ea_id)
    return q.all()

def get_matchup_history(clubs):
    games = get_games_between(clubs[0], clubs[1])
    club_1_wins = 0
    for game in games:
        if game.won_by(clubs[0]):
            club_1_wins += 1 
    result_dict = {'Series': "%d - %d" % (club_1_wins, len(games) - club_1_wins)}
    if len(games) > 0:
        result_dict['Last Game'] = games[0].game_info()
    else:
        result_dict['Last Game'] = None
    return result_dict

def get_match_history(club):
    games = club.get_games()
    club_wins = 0
    for game in games:
        if game.won_by(club):
            club_wins += 1 
    result_dict = {'record': "%d - %d" % (club_wins, len(games) - club_wins)}
    if len(games) > 0:
        result_dict['games'] = [game.game_info() for game in games]
    else:
        result_dict['games'] = []
    return result_dict

def get_games_between(club_1, club_2):
#    return Session().query(Game).filter(and_(Game.club_1_id == club_1.id, Game.club_2_id == club_2.id)).order_by(desc(Game.ea_id)).all()
    s1 = Session().query(Game).filter(and_(Game.club_1_id == club_1.id, Game.club_2_id == club_2.id)).order_by(desc(Game.ea_id)).all()
    s2 = Session().query(Game).filter(and_(Game.club_1_id == club_2.id, Game.club_2_id == club_1.id)).order_by(desc(Game.ea_id)).all()
    total = set(s1) | set(s2)
    return list(total)
                                        

    
Base.metadata.create_all(engine)
