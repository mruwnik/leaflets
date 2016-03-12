from leaflets.views import LoginHandler
from leaflets.forms.auth import AddUserForm
from leaflets.models import User
from leaflets import database


class AddUserHandler(LoginHandler):

    url = '/add_user'

    PASSWORD_MISMATCH = 'The passwords do not match'
    EXISTING_USER = 'There already is a user with that username'

    @property
    def form(self):
        return AddUserForm(self.request.arguments)

    def post(self):
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
            password_hash=self.hash(form.password.data)
        )

        database.session.add(user)
        database.session.commit()
        self.set_secure_cookie("user_id", str(user.id))
        self.redirect("/")
