from tornado.web import authenticated

from leaflets.views.base import BaseHandler
from leaflets.models import User


class UsersListHandler(BaseHandler):

    """Handle listing users."""

    url = '/users/list'

    @authenticated
    def get(self):
        """Show all users that this user can see."""
        current_user = User.query.get(self.current_user)
        if current_user.parent:
            users = current_user.parent.children
        else:
            users = [current_user]
        self.render('users.html', users=users)
