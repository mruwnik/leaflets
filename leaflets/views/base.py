from tornado.web import RequestHandler
from tornado import gen


class BaseHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render('sandra.html')


