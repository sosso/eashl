from bs4 import BeautifulSoup
import requests

def get_team_ids(game):
    left_team = game.find('td', {'class':"align-left team overflow-hidden"})
    left_team_url = left_team.find('a').attrs['href']
    left_team_id = left_team_url.split("/")[-2]
    
    right_team = game.find('td', {'class':"align-right team overflow-hidden"})
    right_team_url = right_team.find('a').attrs['href']
    right_team_id = right_team_url.split("/")[-2]

    return (left_team_id, right_team_id)

def get_match_detail_url(game):
    match_id_div = game.parent.find(lambda tag: tag.name=='div' and tag.has_key('id')and tag['id'].startswith("match-detail-container"))
    match_id = match_id_div['id'].split("-")[-1]
    match_detail_url = "http://www.easportsworld.com/en_US/clubs/partial/401A0001/%s/match-results/details?match_id=%s&type=all" % (left_team_id, match_id)
    return match_detail_url

clubpage_url = 'https://dl.dropbox.com/u/6996716/clubpage.htm'
clubpage_html = requests.get(clubpage_url).content
soup = BeautifulSoup(clubpage_html)
games_list = soup.find_all('table', {'class':"full-width plain simple-results-table no-margin fixed-layout-table"})
for game in games_list:
    left_team_id, right_team_id = get_team_ids(game)
    match_detail_url = get_match_detail_url(game)
    match_detail_html = requests.get(match_detail_url).content
    
    match_detail_soup = BeautifulSoup(match_detail_html)
    team_stats = match_detail_soup.find_all('table', {'class':'styled grey-head full-width'})
    left_team_stats = team_stats[0]
    right_team_stats = team_stats[1]
    
    left_team_stats, right_team_stats = 
    
    for player_row in left_team_stats.find_all('tr')[1:]: #skip header row
        cols = player_row.find_all('td')
        stats_dict = {}
        for col in cols:
            stats_dict[col['title']] =  col.text
        pass
    for player_row in right_team_stats.find_all('tr')[1:]:#skip header row
        pass
    pass
    
