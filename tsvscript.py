#from models import Session, UserGame, Game, User, get_games_for_user
#import simplejson
#
#def get_usergames(id):
#    return Session().query(UserGame).filter(UserGame.user_id==id).all()
#
#def single_player_stats(id):
#    my_games = get_usergames(id)
#    file = open('data.tsv', 'w')
#    file.write('date\tclose\n')
#    total = 0
#    for index, usergame in enumerate(my_games):
#        game = usergame.game
#        date = str(game.game_date())
#        total += usergame.points
#        file.write("%s\t%d\n" % (date, total/(index+1)))
#
#
#
#def multi_player_stats(ids):
#    #games = Session.query(UserGame).filter(UserGame.user_id.in_(ids)).group_by(UserGame.game_id).all()
#    file = open('data.tsv', 'w')
#    game_objs = [get_games_for_user(id) for id in ids]
#    master_list = [tuple.Game for tuple in game_objs[0]]
#    people = [Session.query(User).filter(User.id==id).first() for id in ids]
#    names = ["Game"]   
#    mylist = []
#    [names.append(person.username) for person in people] 
#    mylist.append(names)
#    for person in game_objs:
#        person_list = []
#        for tuple in person:
#            person_list.append(tuple.Game)
#        master_list = list(set(person_list) & set(master_list))
#    
#    for game in master_list:
#        usergames = Session.query(UserGame).filter(UserGame.game_id==game.id).filter(UserGame.user_id.in_(ids)).all()
#        game_stats = [game.ea_id]
#        [game_stats.append(usergame.points) for usergame in usergames]
#        mylist.append(game_stats)
#    file.write(simplejson.dumps(mylist))
#    pass
#
#
#multi_player_stats([17,4,5])    