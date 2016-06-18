from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms_tornado import Form

from leaflets import database
from leaflets.models import User


class LoginForm(Form):
    name = StringField('user_name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class EditUserForm(Form):
    name = StringField('user_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('is_admin')
    is_equal = BooleanField('is_equal')
    user_id = HiddenField('user_id')

    def update(self, user):
        """Update the given user."""
        user.username = self.name.data
        user.email = self.email.data
        user.admin = self.is_admin.data

        # if selected, make the given user equal to this one
        if self.is_equal.data and user.parent:
            user.parent = user.parent.parent

        database.session.commit()
        return user


class AddUserForm(Form):
    PASSWORD_MISMATCH = 'The passwords do not match'

    name = StringField('user_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password_repeat = PasswordField('repeat_password', validators=[DataRequired()])
    is_admin = BooleanField('is_admin')
    is_equal = BooleanField('is_equal')

    def validate_password(self, field):
        if field.data and field.data != self.password_repeat.data:
            raise ValidationError(self.PASSWORD_MISMATCH)

    def save(self, current_user_id):
        user = User(
            username=self.name.data,
            email=self.email.data,
            password_hash=User.hash(self.password.data),
            admin=self.is_admin.data,
            parent_id=User.query.get(current_user_id).parent_id if self.is_equal.data else current_user_id,
        )

        database.session.add(user)
        database.session.commit()
