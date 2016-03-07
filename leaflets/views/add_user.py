from tornado import gen

from leaflets.views import LoginHandler
from leaflets.forms.auth import AddUserForm


class AddUserHandler(LoginHandler):

    url = '/add_user'

    PASSWORD_MISMATCH = 'The passwords do not match'
    EXISTING_USER = 'There already is a user with that username'

    @property
    def form(self):
        return AddUserForm(self.request.arguments)

    @gen.coroutine
    def post(self):
        form = self.form
        if not form.validate():
            return self.get(form)

        if form.password.data != form.password_repeat.data:
            form.password.errors.append(self.PASSWORD_MISMATCH)
            return self.get(form)

        user = yield self.find_user(form.name.data)
        if user:
            form.name.errors.append(self.EXISTING_USER)
            return self.get(form)

        yield self.add_user(
            form.name.data, form.password.data, form.email.data)
        user_id = yield self.find_user(form.name.data)
        self.set_secure_cookie("user_id", str(user_id))
        self.redirect("/")

    @gen.coroutine
    def find_user(self, username):
        """Find any user with the given username.

        :param str username: the name of the user to find
        :returns: the user's id, or None if not found
        """
        conn = yield self.application.db.connect()
        result = yield conn.execute(
            'SELECT id FROM users WHERE username = %s',
            (username,)
        )
        user_id = result.fetchone()
        raise gen.Return(user_id and user_id[0])

    @gen.coroutine
    def add_user(self, username, password, email):
        """Add a new user with the given params."""
        conn = yield self.application.db.connect()
        yield conn.execute(
            'INSERT INTO users (username, password_hash, email, admin) VALUES (%s, %s, %s, False)',
            (username, self.hash(password), email)
        )

