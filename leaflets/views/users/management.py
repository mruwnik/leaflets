from tornado.web import authenticated, HTTPError
from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.views.users.auth import UpdateUserHandler
from leaflets.forms.auth import InviteUsersForm
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

    @property
    def visible_user_ids(self):
        users = [child for user in self.top_level_users for child in user.descendants] + self.top_level_users
        return {user.id for user in users}

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
            raise HTTPError(400, reason=self.locale.translate('bad_user_ids'))

        children_ids = self.visible_user_ids
        if to_move not in children_ids or target not in children_ids:
            raise HTTPError(400, reason=self.locale.translate('bad_user_ids'))

        user = User.query.get(to_move)
        user.parent_id = target
        database.session.commit()

        self.write({'result': 'ok'})


class InviteHandler(UsersListHandler):

    url = '/users/invite/(\w+)'
    name = 'invite_users'

    @property
    def parent(self):
        """Get the id of the parent of all the newly invited users."""
        try:
            parent = int(self.path_args[0])
        except (TypeError, TypeError):
            raise HTTPError(400, reason='bad_parent_provided')

        if parent not in self.visible_user_ids:
            raise HTTPError(400, reason='bad_parent_provided')

        return parent

    @authenticated
    def get(self, parent):
        """Show the invitation form."""
        self.render('users_invite.html', form=InviteUsersForm(parent=self.parent))

    @authenticated
    @gen.coroutine
    def post(self, parent):
        """Send invitations to all new users."""
        parent = self.parent
        form = InviteUsersForm(self.request.arguments)

        if not form.validate():
            self.render('users_invite.html', form=form)

        form.send('%s://%s%s' % (
            self.request.protocol,
            self.request.host,
            self.reverse_url(UpdateUserHandler.name, '', '')[:-1]
        ))
