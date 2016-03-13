from tornado.web import RequestHandler

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
    def is_admin(self):
        """Check whether the current user is an admin."""
        user_id = self.get_current_user()
        if not user_id:
            return None

        user = User.query.get(user_id)
        return user and user.admin

    def prepare(self):
        database.session()

    def on_finish(self):
        database.session.remove()
