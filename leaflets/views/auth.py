from hashlib import sha512

from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.forms import LoginForm


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

    @classmethod
    def hash(self, passwd):
        """Get a hash for the given password.

        :param str passwd: the password to be hashed
        """
        return sha512(passwd.encode('utf-8')).hexdigest()

    @gen.coroutine
    def get_user(self, form):
        """Get the user from the provided form.

        :param LoginForm form: the login form
        :returns: the user's id, or None if could be found
        """
        result = yield self.application.db.execute(
            'SELECT id FROM users WHERE username = %s AND password_hash = %s',
            (form.name.data, self.hash(form.password.data))
        )
        user_id = result.fetchone()
        raise gen.Return(user_id and user_id[0])

    @gen.coroutine
    def post(self):
        """Log in a user."""
        form = self.form
        if not form.validate():
            return self.get(form)

        user_id = yield self.get_user(form)
        if user_id:
            self.set_secure_cookie("user_id", str(user_id))
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

