from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired
from wtforms_tornado import Form


class LoginForm(Form):
    name = TextField('name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

