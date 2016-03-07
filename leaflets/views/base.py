from tornado.web import RequestHandler
from tornado import gen


class BaseHandler(RequestHandler):

    def get(self):
        self.render('sandra.html')

    def get_current_user(self):
        """Get the id of the currently logged in user."""
        user_id = self.get_secure_cookie('user_id')
        return user_id and int(user_id)

    @property
    @gen.coroutine
    def is_admin(self):
        """Check whether the current user is an admin."""
        conn = yield self.application.db.connect()
        result = yield conn.execute('SELECT admin FROM users WHERE id = %s', (self.get_current_user(), ))
        is_admin = result.fetchone()
        raise gen.Return(is_admin and is_admin[0])
