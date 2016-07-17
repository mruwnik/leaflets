from tornado.web import RequestHandler, url

from leaflets import database
from leaflets.models import User


class BaseHandler(RequestHandler):

    url = '/'
    name = None

    def get(self):
        self.redirect('/campaign/list')

    def get_current_user(self):
        """Get the id of the currently logged in user."""
        user_id = self.get_secure_cookie('user_id')
        return user_id and int(user_id)

    @property
    def current_user_obj(self):
        """Get an object representing the currently logged in user."""
        user_id = self.get_current_user()
        if not user_id:
            return None

        user = User.query.get(user_id)
        if not user:
            self.clear_cookie('user_id')
        return user

    @property
    def is_admin(self):
        """Check whether the current user is an admin."""
        user = self.current_user_obj
        return user and user.admin

    def prepare(self):
        database.session()

    def on_finish(self):
        database.session.remove()

    @classmethod
    def get_url(cls):
        """Get an url object for this handler.

        If the class has no name set, it will be tried to be generated by splitting the
        url on any '/' and joining the reversed result with '_'
        """
        name = cls.name or '_'.join(reversed(list(filter(None, cls.url.split('/'))))) or None
        return url(cls.url, cls, name=name)
