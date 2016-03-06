from hashlib import sha512

from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.forms import LoginForm


class LoginHandler(BaseHandler):

    """Handle all login stuff."""

    BAD_PASSWORD = 'The provided password and user do not match'

    def get(self):
        """Show the login form."""
        self.render('login.html', login_form=LoginForm())

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
        conn = yield self.application.db.connect()
        result = yield conn.execute(
            'SELECT id FROM users WHERE username = %s AND password_hash = %s',
            (form.name.data, self.hash(form.password.data))
        )
        raise gen.Return(result.fetchone())

    @gen.coroutine
    def post(self):
        """Log in a user."""
        form = LoginForm(self.request.arguments)
        if not form.validate():
            self.render('login.html', login_form=form)
        else:
            user = yield self.get_user(form)
            if user:
                self.set_secure_cookie("user_id", user.id)
                self.redirect("/")
            else:
                form.password.errors.append(self.BAD_PASSWORD)
                self.render('login.html', login_form=form)

