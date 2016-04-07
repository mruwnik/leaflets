from tornado.web import authenticated

from leaflets.views.users.auth import LoginHandler
from leaflets.views.users.user_management import UsersListHandler
from leaflets.forms.auth import AddUserForm, EditUserForm
from leaflets.models import User


class AddUserHandler(LoginHandler):

    url = '/users/add'
    name = 'add_user'

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

        user = User.query.filter(User.username == form.name.data).scalar()
        if user:
            form.name.errors.append(self.EXISTING_USER)
            return self.get(form)

        form.save(self.current_user)
        self.redirect(UsersListHandler.url)


class EditUserHandler(LoginHandler):

    url = '/users/edit'
    name = 'edit_user'

    EXISTING_USER = 'There already is a user with that username'

    @property
    def form(self):
        user = User.query.get(int(self.get_argument('user')))
        if not user:
            self.redirect(UsersListHandler.url)

        return EditUserForm(
            email=user.email,
            is_admin=user.admin,
            is_equal=user.parent_id == self.current_user_obj.parent_id,
            user_id=user.id,
        )

    @authenticated
    def post(self):
        """Add a new user."""
        form = EditUserForm(self.request.arguments)
        if not form.validate():
            return self.get(form)

        user = User.query.get(int(form.user_id.data))
        if user:
            form.update(user)

        self.redirect(UsersListHandler.url)
