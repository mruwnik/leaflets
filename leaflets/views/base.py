from tornado.web import RequestHandler
from tornado import gen

from leaflets import database
from leaflets.models import User


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
        user = User.query.get(self.get_current_user())
        return user and user.admin

    def prepare(self):
        database.session()

    def on_finish(self):
        database.session.remove()
