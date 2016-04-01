from tornado.web import authenticated

from leaflets.views.users.auth import LoginHandler
from leaflets.forms.auth import AddUserForm
from leaflets.models import User
from leaflets import database


class AddUserHandler(LoginHandler):

    url = '/users/add'
    name = 'add_user'

    PASSWORD_MISMATCH = 'The passwords do not match'
    EXISTING_USER = 'There already is a user with that username'

    @property
    def form(self):
        return AddUserForm(self.request.arguments)

    @authenticated
    def post(self):
        """Add a new user."""
        form = self.form
        if not form.validate():
            return self.get(form)

        if form.password.data != form.password_repeat.data:
            form.password.errors.append(self.PASSWORD_MISMATCH)
            return self.get(form)

        user = User.query.filter(User.username == form.name.data).scalar()
        if user:
            form.name.errors.append(self.EXISTING_USER)
            return self.get(form)

        user = User(
            username=form.name.data,
            email=form.email.data,
            password_hash=self.hash(form.password.data),
            admin=form.is_admin.data,
            parent_id=User.query.get(self.current_user).parent_id if form.is_equal.data else self.current_user,
        )

        database.session.add(user)
        database.session.commit()
        self.redirect("/")
