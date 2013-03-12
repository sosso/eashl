from gamelistscraper import import_games, earliest_timestamp
from models import get_clubs
from sqlalchemy.sql.functions import current_date
import datetime
import logging
#
logger = logging.getLogger('ImportJob')
d = datetime.datetime.now()
if d.hour in range (0, 4) or d.hour in range(20,25):#only run from 8pm-3:59am
    if d.minute in range(0, 10) or d.minute in range(20,30) or d.minute in range(40,50):
        our_club = get_clubs(1)[0]
        most_recent_game = our_club.get_games(1)[0]
        dt = datetime.datetime.fromtimestamp(float(most_recent_game.ea_page_timestamp))
        days_from_start = (dt - datetime.datetime.fromtimestamp(float(earliest_timestamp))).days - 1
        import_games(our_club.ea_id, days_from_start, 0)
    else:
        logger.info('Skipping import because minutes are %d' % d.minute)
logger.info('Skipping import because hour is ' % d.hour)
