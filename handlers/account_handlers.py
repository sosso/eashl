from models import Session, Club, get_games_between, get_clubs, \
    get_matchup_history, get_match_history
import datetime
import logging
import simplejson
import tornado.web



class MatchupHistory(tornado.web.RequestHandler):
    def get(self):
        logger = logging.getLogger('MatchupHistory')
        if "club_id" in self.cookies:
            club_1_id = self.get_cookie("club_id", 0) 
        else:            
            club_1_id = self.get_argument('club_1_id') 
        club_2_id= self.get_argument('club_2_id')
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


class MatchHistory(tornado.web.RequestHandler):
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
            
class ClubSearch(tornado.web.RequestHandler):
    def get(self):
        logger = logging.getLogger('ClubSearch')
        id = self.get_argument('id', None)
        abbr= self.get_argument('abbr', None)        
        try:
            clubs = get_clubs(id, abbr)
            result_obj = [club.search_listing() for club in clubs]
        except Exception, e:
            logger.exception(e)
            Session().rollback()
            result_obj = []
        finally:
            Session.remove()
            self.render("searchresults.html", results=result_obj)
#            self.finish(simplejson.dumps(result_obj))

class SetActiveClub(tornado.web.RequestHandler):
    def get(self):
        logger = logging.getLogger('SetActiveClub')
        club_id = self.get_argument('id', None)        
        try:
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
            self.set_cookie("club_id", value=club_id,expires=expires)
            return
        except Exception, e:
            logger.exception(e)
            Session().rollback()
        finally:
            Session.remove()
            self.render("activeclubsuccess.html")