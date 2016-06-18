from tornado.web import authenticated

from leaflets.views.users.auth import LoginHandler
from leaflets.views.users.management import UsersListHandler
from leaflets.forms.auth import AddUserForm, EditUserForm
from leaflets.models import User


class AddUserHandler(LoginHandler):

    url = '/users/add'
    name = 'add_user'
    submit_label = 'save'

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
    submit_label = 'save'

    EXISTING_USER = 'There already is a user with that username'

    @property
    def form(self):
        user = User.query.get(int(self.get_argument('user')))

        if not user:
            self.redirect(UsersListHandler.url)

        current_user = self.current_user_obj
        # make sure that the current user can edit the provided user - all
        # of the current user's siblings and children can be edited
        allowed_users = [current_user] + current_user.children
        if current_user.parent:
            allowed_users = current_user.parent.children

        if user not in allowed_users:
            return self.redirect(UsersListHandler.url)

        return EditUserForm(
            name=user.username,
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
