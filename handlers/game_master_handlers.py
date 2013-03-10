from handlers.response_utils import auth_required, get_response_dict
from models import User, Session, UserGame, get_game
from pkg_resources import StringIO
from sqlalchemy.sql.functions import random
import dbutils
import os
import simplejson
import tornado.web

#logger = logging.getLogger('modelhandlers')

"""
username
item_id
<file>
"""
class Kick(tornado.web.RequestHandler):
    @auth_required
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument('username')
        game_id = self.get_argument('game_id')
        session = Session()
        try:
            user = dbutils.get_or_create(session, User, username=username)
        except Exception, e:
            session.rollback()
            final_string = "Oops!  Something went wrong.  Please try again"
        finally:
            Session.remove()
            self.finish(final_string)


"""
username
"""
class GrantPowerup(tornado.web.RequestHandler):
    @auth_required
    @tornado.web.asynchronous
    def post(self):
        game_id = self.get_argument('game_id')
        powerup_id = self.get_argument('powerup_id')

        session = Session()
        try:
            pass
        except Exception, e:
            session.rollback()
        Session.remove()
        self.finish(simplejson.dumps())
        
        
class Start(tornado.web.RequestHandler):
    @auth_required
    @tornado.web.asynchronous
    def post(self):
        game_id = self.get_argument('game_id')
        session = Session()
        try:
            game = get_game(game_id)
            game.start()
            response_dict = get_response_dict(True)
        except Exception as e:
            session.rollback()
            response_dict = get_response_dict(False, e.message)
        Session.remove()
        self.finish(simplejson.dumps(response_dict))
    
