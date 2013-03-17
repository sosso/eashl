from gamelistscraper import get_games_list, process_game
from import_constants import earliest_timestamp
from models import Session, sm
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.testing.plugin.noseplugin import logging
import Queue
import datetime
import logging
import threading
import time

queue = Queue.Queue()
out_list = []
threads = []
THREAD_COUNT = 30
processed_count = 0

class ThreadURL(threading.Thread):
    def __init__(self, q, club_id, processed_count):
        threading.Thread.__init__(self)
        self.queue = q
        self.club_id = club_id
        self.session = scoped_session(sm)
        self.processed_count = processed_count

    def run(self):
        while True:
            day = self.queue.get()
            try:
                logger = logging.getLogger('import')
                try:
                    dt = datetime.datetime.fromtimestamp(earliest_timestamp) + datetime.timedelta(days=day, hours=1)
                    if dt > datetime.datetime.now():  # gone past today
                        logger.info('Datetime greater than now, breaking')
                        break
                    dt_stamp = str(time.mktime(dt.timetuple()))[:-2]  # trim '.0' from end
                    timeshifted_url = 'http://www.easportsworld.com/en_US/clubs/partial/401A0001/%s/match-results?timestamp=%s' % (str(self.club_id), dt_stamp) 
                    games_list = get_games_list(timeshifted_url)
                    for game in games_list:
                        process_game(game, dt_stamp, self.session)
                except Exception as e:
                        logger.exception(e)
            except Exception as e:
                print('Job failed for %d', day)
            self.session.commit()
            self.session.close()
            self.queue.task_done()
            self.processed_count += 1
            
def bulk_grabber(club_id):
    start = time.clock()
    session = Session()
    if len(threads) != THREAD_COUNT:
        for i in range(THREAD_COUNT):
            t = ThreadURL(queue, club_id, processed_count)
            t.setDaemon(True)
            t.start()
            threads.append(t)
    days_from_start = (datetime.datetime.now() - datetime.datetime.fromtimestamp(float(earliest_timestamp))).days - 1

    for day in range(days_from_start + 1):
        queue.put(day)

    queue.join()
    end = time.clock()
    print "Total time: %d" % end
    session.commit()

bulk_grabber('72305')