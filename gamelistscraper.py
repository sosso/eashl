from bs4 import BeautifulSoup
from dbutils import get_or_create
from logging_setup import NoParsingFilter
from models import Session, Game, Club, UserGame
import datetime
import logging
import requests
import simplejson
import time

player_positions = {'0':'G', '1':'D', '3':'LW', '4':'C', '5':'RW'}
clubpage_url = 'https://dl.dropbox.com/u/6996716/clubpage.htm'
match_detail_url = 'https://dl.dropbox.com/u/6996716/gamepage.htm'
earliest_timestamp = 1347422400
DELETED_CLUB_NAME = 'XX DELETED XX'

def get_team_names(game):
    try:
        left_team = game.find('td', {'class':"align-left team overflow-hidden"}).text.replace("\n", "").replace(")", "").strip().split("(")
        if left_team is None or len(left_team) < 2:
            raise ValueError
    except:
        left_team = [DELETED_CLUB_NAME, '']
    try:
        right_team = game.find('td', {'class':"align-right team overflow-hidden"}).text.replace("\n", "").replace(")", "").strip().split("(")
        if right_team is None or len(right_team) < 2:
            raise ValueError
    except:
        right_team = [DELETED_CLUB_NAME, '']
    return ([left_team[0], left_team[1]], [right_team[0], right_team[1]])

def get_team_ids(game):
    try:
        left_team = game.find('td', {'class':"align-left team overflow-hidden"})
        left_team_url = left_team.find('a').attrs['href']
        left_team_id = left_team_url.split("/")[-2]
    except:
        left_team_id = -1
    
    try:
        right_team = game.find('td', {'class':"align-right team overflow-hidden"})
        right_team_url = right_team.find('a').attrs['href']
        right_team_id = right_team_url.split("/")[-2]
    except:
        right_team_id = -1
    return (left_team_id, right_team_id)

def get_match_id_and_url(game, left_team_id):
    match_id_div = game.parent.find(lambda tag: tag.name == 'div' and tag.has_key('id')and tag['id'].startswith("match-detail-container"))
    match_id = match_id_div['id'].split("-")[-1]
    match_detail_url = "http://www.easportsworld.com/en_US/clubs/partial/401A0001/%s/match-results/details?match_id=%s&type=all" % (left_team_id, match_id)
    return (match_id, match_detail_url)

def get_team_stats(match_detail_soup):
    team_stats = match_detail_soup.find_all('table', {'class':'styled grey-head full-width'})
    stats = []
    try:
        for team in team_stats:
            if team is not None:
                stats.append(individual_stats(team))  
    except:
        pass
    return stats

def get_scores(game):
    scores = game.find('div', {'class':'match-result-score'}).text.split(' - ')
    return [int(score) for score in scores]
    
def get_time(game):
    time = game.find(lambda tag: tag.name == 'div' and tag.text.startswith("Time:"))
    return time.text[6:]  # trims off 'Time: '

def get_game_info(game, left_team_id):
    score = get_scores(game)
    id, url = get_match_id_and_url(game, left_team_id)
    return {'score':score, 'time':get_time(game), 'left_winner':(True if score[0] > score[1] else False), 'id':id, 'url':url}

def get_logos(game, left_name, right_name):
    images = game.find_all(lambda tag: tag.name == 'img' and not tag.attrs['alt'].startswith("Spinner"))
    my_images = []
    if left_name == DELETED_CLUB_NAME:
        images.insert(0, None)
    if right_name == DELETED_CLUB_NAME:
        images.append(None)
    for image in images:
        if image is not None:
            try:
                my_images.append(image.attrs['src'].replace("small", "big"))
            except Exception as e:
                pass
        else:
            my_images.append(None)
    return my_images
    
def individual_stats(team_stats_soup):
    stats_list = []
    for player_row in team_stats_soup.find_all('tr')[1:]:  # skip header row
        cols = player_row.find_all('td')
        if len(cols) == 4:  # ignore the 'invite players to club link on the right side
            cols = cols[:-1]
        stats_dict = {}
        name = player_row.find_all(lambda tag: tag.name == 'a' and tag['title'].startswith("View"))[1].text
        stats_dict['player_name'] = name
        for col in cols:
            stats_dict[col['title']] = col.text
        stats_dict['Position'] = player_positions[stats_dict['Position']]
        stats_list.append(stats_dict)
    return stats_list

def get_clubpage_soup(url):
    clubpage_html = requests.get(url).content
    return BeautifulSoup(clubpage_html)

def get_rank_info(club):
    try:
        if club.should_update():
            url = 'http://www.easportsworld.com/en_US/clubs/401A0001/%s/overview' % str(club.ea_id)
            soup = BeautifulSoup(requests.get(url).content)
            stats = soup.find('table', {'class':'plain full-width nowrap less-padding no-margin'})
            tds = stats.find_all('td')
            ret_dict = {}
            ret_dict['division'] = tds[0].contents[1].text
            ret_dict['record'] = str(tds[1].contents[1].text)
            ret_dict['div_rank'] = int(tds[3].contents[1].text)
            ret_dict['overall_rank'] = int(tds[4].text.split(":")[1].strip())
            ret_dict['members'] = int(tds[5].text.split(":")[1].strip())
            club.update_last_rank_fetch(datetime.datetime.now())
        else:
            ret_dict = club.most_recent_rank_info()
    except Exception as e:
        ret_dict = dict(division='', record='', div_rank=-1, overall_rank=-1, members=-1)
    return ret_dict

def import_games(ea_club_id, days_from_start=0, days_from_end=0):
    logger = logging.getLogger('import')
    logger.addFilter(NoParsingFilter())
    logger.info('Starting import for %s from day %d and going %d days' % (ea_club_id, days_from_start, days_from_end))
    for i in range(0 + days_from_start, 178-days_from_end):
        logger.debug('pass %d of %d' % (i-days_from_start, 178-days_from_end-days_from_start))
        dt = datetime.datetime.fromtimestamp(earliest_timestamp) + datetime.timedelta(days=i, hours=1)
        dt_stamp = str(time.mktime(dt.timetuple()))[:-2]#trim '.0' from end
        timeshifted_url = 'http://www.easportsworld.com/en_US/clubs/partial/401A0001/%s/match-results?timestamp=%s' % (str(ea_club_id), dt_stamp) 
        clubpage_soup = get_clubpage_soup(timeshifted_url) 
        games_list = clubpage_soup.find_all('table', {'class':"full-width plain simple-results-table no-margin fixed-layout-table"})
        logger.debug('Found %d games on %s for %s' % (len(games_list), datetime.datetime.now().strftime("%Y-%m-%d"), ea_club_id))
        for game in games_list:
            left_team_id, right_team_id = get_team_ids(game)
            
            left_team_names, right_team_names = get_team_names(game)
            game_info = get_game_info(game, left_team_id)
            left_logo, right_logo = get_logos(game, left_team_names[0], right_team_names[0])
            logger.debug('game processing: %s' % simplejson.dumps(game_info))
            if len(Session().query(Game).filter_by(ea_id=game_info['id']).all()) == 0:  # new game
                left_club = get_or_create(Session(), Club, ea_id=left_team_id, name=left_team_names[0], abbr=left_team_names[1])
                right_club = get_or_create(Session(), Club, ea_id=right_team_id, name=right_team_names[0], abbr=right_team_names[1])
                left_club.update_logo(left_logo)
                right_club.update_logo(right_logo)
                game = get_or_create(Session(), Game, \
                                      ea_id=game_info['id'], club_1_id=left_club.id, \
                                      club_1_score=game_info['score'][0], \
                                      club_2_id=right_club.id, club_2_score=game_info['score'][1],\
                                      time=game_info['time'], ea_page_timestamp=dt_stamp)
                ranks = [get_rank_info(club) for club in [left_club, right_club]]
                game.update_rank_info(ranks)
                match_detail_html = requests.get(game_info['url']).content
                match_detail_soup = BeautifulSoup(match_detail_html)
                try:    
                    left_team_stats, right_team_stats = get_team_stats(match_detail_soup)
                except ValueError:
                    continue
                session = Session()
                for player in left_team_stats:
                    usergame= UserGame(username=player['player_name'], game_id=game.id, \
                                      club_id=left_club.id, position=player['Position'], points=player['Points'], \
                                      hits=player['Total Number of Hits'])
                    session.add(usergame)
                    session.flush()
                    session.commit()
                for player in right_team_stats:
                    usergame = UserGame(username=player['player_name'], game_id=game.id, \
                                          club_id=right_club.id, position=player['Position'], points=player['Points'], \
                                          hits=player['Total Number of Hits'])
                    session.add(usergame)
                    session.flush()
                    session.commit()
            else:
                logger.debug('Game already processed')
import_games('273', 10)
#get_club_stats('http://www.easportsworld.com/en_US/clubs/401A0001/273/overview')