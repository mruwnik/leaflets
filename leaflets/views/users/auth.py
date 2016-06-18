import time
from tornado import gen
from tornado.web import HTTPError

from leaflets.views.base import BaseHandler
from leaflets.forms import LoginForm
from leaflets.models import User
from leaflets.etc import options


class LoginHandler(BaseHandler):

    """Handle all login stuff."""

    BAD_PASSWORD = 'The provided password and user do not match'

    url = '/login'
    submit_label = 'sign in'

    @property
    def form(self):
        return LoginForm(self.request.arguments)

    def get(self, form=None):
        """Show the login form."""
        form = form or self.form
        if form:
            self.render('simple_form.html', form=form, url=self.url, button=self.submit_label)

    def get_user(self, form):
        """Get the user from the provided form.

        :param LoginForm form: the login form
        :returns: the use, or None if could not be found
        """
        return User.query.filter(
            User.email == form.email.data,
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


class UpdateUserHandler(BaseHandler):

    url = '/users/update/(\d+)-(\w+)'
    name = 'update_user'

    def validate_timestamp(self, timestamp):
        if int(timestamp) > options.ACTIVATION_TIMEOUT + time.time() / (60 * 60 * 24):
            raise HTTPError(400, reason=self.locale.translate('stale_activation_link'))

    def get(self, timestamp, user_hash):
        self.validate_timestamp(timestamp)
        user = User.query.filter(User.password_hash == 'reset-%s-%s' % (timestamp, user_hash)).first()
        self.write(str(user))

