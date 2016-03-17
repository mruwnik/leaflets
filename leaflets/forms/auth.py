from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms_tornado import Form


class LoginForm(Form):
    name = StringField('user_name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class AddUserForm(Form):
    PASSWORD_MISMATCH = 'The passwords do not match'

    name = StringField('user_name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_repeat = PasswordField('repeat_password', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])

    def validate_password(self, field):
        if field.data and field.data != self.password_repeat.data:
            raise ValidationError(self.PASSWORD_MISMATCH)

