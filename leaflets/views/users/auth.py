from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.forms import LoginForm
from leaflets.models import User


class LoginHandler(BaseHandler):

    """Handle all login stuff."""

    BAD_PASSWORD = 'The provided password and user do not match'

    url = '/login'

    @property
    def form(self):
        return LoginForm(self.request.arguments)

    def get(self, form=None):
        """Show the login form."""
        self.render('simple_form.html', form=form or self.form, url=self.url)

    def get_user(self, form):
        """Get the user from the provided form.

        :param LoginForm form: the login form
        :returns: the use, or None if could not be found
        """
        return User.query.filter(
            User.username == form.name.data,
            User.password_hash == User.hash(form.password.data)
        ).scalar()

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


class LogOutHandler(BaseHandler):

    """Handle logging out."""

    url = '/logout'

    def get(self):
        """Log out."""
        self.clear_cookie('user_id')
        self.redirect("/")

