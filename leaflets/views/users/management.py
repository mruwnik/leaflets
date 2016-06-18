from tornado.web import authenticated, HTTPError
from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.models import User
from leaflets import database


class UsersListHandler(BaseHandler):

    """Handle listing users."""

    url = '/users/list'

    @property
    def top_level_users(self):
        """Get all users that will be displayed as top level ones."""
        current_user = self.current_user_obj
        if current_user.parent:
            return current_user.parent.children
        else:
            return User.query.filter(User.parent_id == None).all()

    @authenticated
    def get(self):
        """Show all users that this user can see."""
        self.render('users.html', users=self.top_level_users)

    @authenticated
    @gen.coroutine
    def post(self):
        """Move a user to a different group."""
        try:
            to_move = int(self.get_argument('user'))
            target = int(self.get_argument('target'))
        except ValueError:
            raise HTTPError(400, reason='bad_user_ids')

        all_users = [child for user in self.top_level_users for child in user.descendants] + self.top_level_users
        children_ids = {user.id for user in all_users}

        if to_move not in children_ids or target not in children_ids:
            raise HTTPError(400, reason='bad_user_ids')

        user = User.query.get(to_move)
        user.parent_id = target
        database.session.commit()

        self.write({'result': 'ok'})
