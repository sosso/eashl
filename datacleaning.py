from gamelistscraper import get_games_list, process_game, get_rank_info
from import_constants import earliest_timestamp
from models import Session, Game, Session, sm, get_clubs
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.sql.expression import or_
from sqlalchemy.testing.plugin.noseplugin import logging
import Queue
import datetime
import logging
import threading
import time

queue = Queue.Queue()
threads = []
THREAD_COUNT = 20

class ThreadCleaner(threading.Thread):
    def __init__(self, q, session):
        threading.Thread.__init__(self)
        self.queue = q
        self.session = session

    def run(self):
        logger = logging.getLogger('import')
        while True:
            game = self.queue.get()
            try:
                ranks = [get_rank_info(club, ignore_time=True) for club in [game.club_1, game.club_2]]
                game.update_rank_info(ranks, self.session)
                logger.info('game processed')
            except Exception as e:
                logger.exception(e)
                self.session.rollback()
            self.session.commit()
            self.session.close()
            self.queue.task_done()
            
def rank_fixer():
    s = Session()
    time.clock()
    session = Session()
    if len(threads) != THREAD_COUNT:
        for i in range(THREAD_COUNT):
            t = ThreadCleaner(queue, s)
            t.setDaemon(True)
            t.start()
            threads.append(t)
    dirty_games = s.query(Game).filter(or_(Game.club_1_div_rank == -1, Game.club_2_div_rank == -1)).all()
    clubs_to_check = []
    for game in dirty_games:
#        for club in [game.club_1, game.club_2]:
#            if club not in clubs_to_check and club.should_update(ignore_time=True): 
#                queue.put(club.id)
        queue.put(game)
    queue.join()
    end = time.clock()
    print "Total time: %d" % end
    session.commit()
    Session.remove()
    pass

        
