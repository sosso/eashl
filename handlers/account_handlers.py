from models import Session, Club, get_games_between, get_clubs, \
    get_matchup_history
import logging
import simplejson
import tornado.web



class MatchupHistory(tornado.web.RequestHandler):
    def get(self):
        logger = logging.getLogger('MatchupHistory')
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
