from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.models import User


class UsersListHandler(BaseHandler):

    """Handle listing users."""

    url = '/users/list'

    def get(self):
        """Show all users that this user can see."""
        current_user = User.query.get(self.current_user)
        if current_user.parent:
            users = current_user.parent.children
        else:
            users = [current_user]
        self.render('users.html', users=users)

    @gen.coroutine
    def post(self):
        """Log in a user."""
        form = self.form
        if not form.validate():
            return self.get(form)
        user = self.get_user(form)
        if user:
            self.set_secure_cookie("user_id", str(user.id))
            self.redirect("/")
        else:
            form.password.errors.append(self.BAD_PASSWORD)
            self.get(form)
