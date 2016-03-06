from tornado.web import RequestHandler
from tornado import gen


class BaseHandler(RequestHandler):

    def get(self):
        self.render('sandra.html')

    def get_current_user(self):
        return self.get_secure_cookie('user_id')



