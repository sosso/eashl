from gamelistscraper import earliest_timestamp, import_games
from models import Session, Club, get_games_between, get_clubs, \
    get_matchup_history, get_match_history, get_player
from statsprocessor import get_stats
from utils import grouper
import datetime
import logging
import requests
import simplejson
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def render(self, template, **kwargs):
        # add any variables we want available to all templates
        kwargs['player_id'] = self.get_cookie("player_id", None)
        kwargs['club_id'] = self.get_cookie("club_id", None)
        kwargs['grouper'] = grouper
        super(BaseHandler, self).render(template, **kwargs)

class HomeHandler(BaseHandler):
    def get(self):
        return self.render("index.html")

class ImportGames(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        logger = logging.getLogger('MatchupHistory')            
        ea_id = self.get_argument('ea_id') 
        try:
            club = get_clubs(ea_id=ea_id)
            if len(club) == 0:
                import_games(ea_id, 0, 0)
            else:
                club = club[0]
                most_recent_game = club.get_games(1)[0]
                dt = datetime.datetime.fromtimestamp(float(most_recent_game.ea_page_timestamp))
                days_from_start = (dt - datetime.datetime.fromtimestamp(float(earliest_timestamp))).days - 1
                import_games(club.ea_id, days_from_start, 0)
            result_str = 'success'
        except Exception, e:
            logger.exception(e)
            Session().rollback()
            result_str = e.message
        finally:
            Session.remove()
            self.finish(result_str)


class MatchupHistory(BaseHandler):
    def get(self):
        logger = logging.getLogger('MatchupHistory')
        if "club_id" in self.cookies:
            club_1_id = self.get_cookie("club_id", 0) 
        else:            
            club_1_id = self.get_argument('club_1_id') 
        club_2_id = self.get_argument('club_2_id')
        try:
            clubs = [get_clubs(id)[0] for id in [club_1_id, club_2_id]]
            result_obj = get_matchup_history(clubs)
        except Exception, e:
            logger.exception(e)
            Session().rollback()
            result_obj = {}
        finally:
            Session.remove()
            self.render("matchuphistory.html", history=result_obj)
#            self.finish(simplejson.dumps(result_obj))

class PlayerHistory(BaseHandler):
    def get(self):
        logger = logging.getLogger('PlayerHistory')
        player_id = self.get_argument('player_id', None)
        try:
            userids = self.request.arguments.get("userids")
        except:
            userids = []
        try:
            if userids is not None and len(userids) > 0:
                result_obj = [get_player(player_id).recent_game_history(limit=25) for player_id in userids]
            else:
                if player_id is None:
                    player_id = self.get_cookie("player_id") 
                else:
                    player_id = self.get_argument('player_id')
                result_obj = [get_player(player_id).recent_game_history(limit=25)]
        except Exception, e:
            logger.exception(e)
            Session().rollback()
            result_obj = {}
        finally:
            Session.remove()
            self.render("playerhistory.html", history={'players':result_obj})
#            self.finish(simplejson.dumps(result_obj))

class StatsUpload(BaseHandler):
    def get(self):
        self.render("gamestats.html", game=None)
    def post(self):
        image_url = self.get_argument("image_url")
        result = get_stats(image_url)
        self.render("gamestats.html", game={'team_stats':result})

class MatchHistory(BaseHandler):
    def get(self):
        logger = logging.getLogger('MatchupHistory')
        club_id = self.get_argument('club_id', None)
        if club_id is None:
            club_id = self.get_cookie("club_id") 
        else:
            club_id = self.get_argument('club_id')
        try:
            club = get_clubs(club_id)[0]
            result_obj = get_match_history(club)
        except Exception, e:
            logger.exception(e)
            Session().rollback()
            result_obj = {}
        finally:
            Session.remove()
            self.render("gamehistory.html", result=result_obj)
            
class ClubSearch(BaseHandler):
    def get(self):
        logger = logging.getLogger('ClubSearch')
        id = self.get_argument('id', None)
        abbr = self.get_argument('abbr', None)        
        try:
            clubs = get_clubs(id, abbr)
            result_obj = [club.search_listing() for club in clubs]
        except Exception, e:
            logger.exception(e)
            Session().rollback()
            result_obj = None
        finally:
            Session.remove()
            self.render("searchresults.html", results=result_obj)
#            self.finish(simplejson.dumps(result_obj))

class SetActiveClub(BaseHandler):
    def get(self):
        logger = logging.getLogger('SetActiveClub')
        club_id = self.get_argument('id', None)        
        try:
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
            self.set_cookie("club_id", value=club_id, expires=expires)
        except Exception, e:
            logger.exception(e)
            Session().rollback()
        finally:
            Session.remove()
            self.render("activeclubsuccess.html")

class SetActivePlayer(BaseHandler):
    def get(self):
        logger = logging.getLogger('SetActiveClub')
        player_id = self.get_argument('player_id')        
        try:
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
            self.set_cookie("player_id", value=player_id, expires=expires)
        except Exception, e:
            logger.exception(e)
            Session().rollback()
        finally:
            Session.remove()
            self.render("activeplayersuccess.html")
