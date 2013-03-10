from models import Session, Club, get_matchup_history, \
    get_clubs

#def myfunc(club_1_id, club_2_abbr):
#    club_1 = get_club(id=club_1_id)
#    matching_clubs = Session().query(Club).filter(Club.abbr==club_2_abbr).all()
#    games_arr = [{club_2.display_info():get_games_between(club_1, club_2)} for club_2 in matching_clubs]
#    pass

club_1 = get_clubs(1)[0]
club_2 = get_clubs(174)[0]
result_obj = get_matchup_history([club_1, club_2])
pass