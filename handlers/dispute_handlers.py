from models import Session, login, create_user
import simplejson
import tornado.web

#logger = logging.getLogger('modelhandlers')

"""
username
item_id
<file>
"""
class LoginHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        session = Session()
        final_string = "ERROR"
        try:
            user = login(username=username, password=password)
            if user is not None:
                final_string = "SUCCESS"
                #TODO return their token
        except Exception:
            session.rollback()
        finally:
            Session.remove()
            self.finish(simplejson.dumps({'result':final_string}))


class CreateUserHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        session = Session()
        result_dict = {}
        try:
            picture_binary = self.request.files['profile_picture'][0]['body']    
            create_user(username = username, password=password, profile_picture=picture_binary)
            result_dict['result'] = "SUCCESS"
        except Exception, e:
            session.rollback()
            result_dict['result'] = "ERROR"
            result_dict['reason'] = e.message
        finally:
            Session.remove()
            self.finish(simplejson.dumps(result_dict))
