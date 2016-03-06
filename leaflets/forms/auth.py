from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms_tornado import Form


class LoginForm(Form):
    name = TextField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class AddUserForm(Form):
    PASSWORD_MISMATCH = 'The passwords do not match'

    name = TextField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_repeat = PasswordField('repeat password', validators=[DataRequired()])
    email = TextField('email', validators=[DataRequired(), Email()])

    def validate_password(self, field):
        if field.data and field.data != self.password_repeat.data:
            raise ValidationError(self.PASSWORD_MISMATCH)

